frappe.ui.form.off("Stock Entry", "clean_up")
frappe.ui.form.off("Stock Entry", "setup")
frappe.ui.form.on('Stock Entry', {
	onload_post_render(frm) {
		frm.set_query('work_order', function () {
			return {
				filters: [
					['Work Order', 'docstatus', '=', 1],
					['Work Order', 'status', '!=', 'Completed'],
					['Work Order', 'company', '=', frm.doc.company]
				]
			}
		})
		frm.trigger('new_function')
		if (frm.doc.stock_entry_type == 'Manufacture' && frm.doc.items) frm.call('update_default_batch_in_item')
	},
	setup(frm){
		frm.trigger('new_function')
	},
	refresh(frm) {
		frm.trigger('new_function')
		frm.remove_custom_button('Material Request', "Get Items From")
		frm.add_custom_button(__('Material Requests'), function () {
			erpnext.utils.map_current_doc({
				method: "core_erp.customizations.material_request.material_request.make_stock_entry",
				source_doctype: "Material Request",
				target: frm,
				date_field: "schedule_date",
				setters: {
					company: frm.doc.company,
				},
				get_query_filters: {
					docstatus: 1,
					material_request_type: ["in", ["Material Transfer", "Material Issue", 'Material Transfer for Manufacture']],
					status: ["not in", ["Transferred", "Issued", "Stopped"]]
				}
			})
		}, __("Get Items From"));

		if (cur_frm.doc.stock_entry_type == 'Manufacture') {
			$.each(frm.doc.items || [], function (i, d) {
				if (d.t_warehouse != '') {
					d.manufacturing_date = frappe.datetime.get_today()
					cur_frm.refresh_fields()
				}
			})
		}
	},
	clean_up: function() {
		// Clear Work Order record from locals, because it is updated via Stock Entry
		if(this.frm.doc.work_order &&
			in_list(["Manufacture", "Material Transfer for Manufacture", "Material Consumption for Manufacture","Material Issue"],
				this.frm.doc.purpose)) {
			// console.log(this.frm.doc.work_order)
			frappe.model.remove_from_locals("Work Order",
				this.frm.doc.work_order);
		}
	},
	posting_date(frm) {
		if ((frm.doc.posting_date) > frappe.datetime.get_today()) {
			frm.set_value('posting_date', frappe.datetime.get_today())
			frm.refresh();
			frappe.throw("Posting date Cannot be a future date")
		}
	},
	onload(frm) {
		if (frm.doc.__islocal && frm.doc.work_order) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					'doctype': 'Work Order',
					'filters': {
						name: frm.doc.work_order
					},
					'fieldname': ['work_station']
				},
				callback: function (r) {
					frm.set_value('line', r.message.work_station)

				}
			})
		}
	},
	validate(frm) {
		if (cur_frm.doc.stock_entry_type == 'Manufacture') {
			$.each(frm.doc.items || [], function (i, d) {
				d.expense_account = ""
			})
		}
	},
	new_function(frm) {
		frm.set_query("line", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			}
		});
		frm.set_indicator_formatter('item_code', function(doc) {
			if (!doc.s_warehouse) {
				return 'blue';
			} else {
				return (doc.qty<=doc.actual_qty) ? 'green' : 'orange';
			}
		});

		frm.set_query('work_order', function() {
			return {
				filters: [
					['Work Order', 'docstatus', '=', 1],
					['Work Order', 'qty', '>','`tabWork Order`.produced_qty'],
					['Work Order', 'company', '=', frm.doc.company]
				]
			}
		});

		frm.set_query('outgoing_stock_entry', function() {
			return {
				filters: [
					['Stock Entry', 'docstatus', '=', 1],
					['Stock Entry', 'per_transferred', '<','100'],
				]
			}
		});

		frm.set_query('source_warehouse_address', function() {
			return {
				filters: {
					link_doctype: 'Warehouse',
					link_name: frm.doc.from_warehouse
				}
			}
		});

		frm.set_query('target_warehouse_address', function() {
			return {
				filters: {
					link_doctype: 'Warehouse',
					link_name: frm.doc.to_warehouse
				}
			}
		});

		frappe.db.get_value('Stock Settings', {name: 'Stock Settings'}, 'sample_retention_warehouse', (r) => {
			if (r.sample_retention_warehouse) {
				var filters = [
							["Warehouse", 'company', '=', frm.doc.company],
							["Warehouse", "is_group", "=",0],
							['Warehouse', 'name', '!=', r.sample_retention_warehouse]
						]
				frm.set_query("from_warehouse", function() {
					return {
						filters: filters
					};
				});
				frm.set_query("s_warehouse", "items", function() {
					return {
						filters: filters
					};
				});
			}
		});

		frm.set_query('batch_no', 'items', function(doc, cdt, cdn) {
			var item = locals[cdt][cdn];
			if(!item.item_code) {
				frappe.throw(__("Please enter Item Code to get Batch Number"));
			} else {
				if (in_list(["Material Transfer for Manufacture", "Manufacture", "Send to Subcontractor"], doc.purpose)) {
					var filters = {
						'item_code': item.item_code,
						'posting_date': frm.doc.posting_date || frappe.datetime.nowdate()
					}
				} else {
					var filters = {
						'item_code': item.item_code
					}
				}

				// User could want to select a manually created empty batch (no warehouse)
				// or a pre-existing batch
				if (frm.doc.purpose != "Material Receipt") {
					filters["warehouse"] = item.s_warehouse || item.t_warehouse;
				}

				return {
					query : "erpnext.controllers.queries.get_batch_no",
					filters: filters
				}
			}
		});


		frm.add_fetch("bom_no", "inspection_required", "inspection_required");
		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);

		frappe.db.get_single_value('Stock Settings', 'disable_serial_no_and_batch_selector')
		.then((value) => {
			if (value) {
				frappe.flags.hide_serial_batch_dialog = true;
			}
		});
		attach_bom_items(frm.doc.bom_no);

		if(!check_should_not_attach_bom_items(frm.doc.bom_no)) {
			erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
		}
	
	}
})

frappe.ui.form.on('Stock Entry Detail', {
	before_items_remove(frm) {
		if (frm.doc.stock_entry_type == 'Manufacture') {
			frappe.throw("Can't delete Items")
		}
	}
})

let customize_fg_rate = function (frm) {
	let items = frm.doc.items;
	let fg_item;
	let amt = 0;
	items.forEach(item => {
		if (item.t_warehouse) {
			fg_item = item;
		} else {
			amt += item.amount;
		}
	})
	if (fg_item) {
		fg_item.basic_rate = amt / fg_item.qty
		fg_item.basic_amount = amt
		fg_item.amount = amt
		fg_item.valuation_rate = amt / fg_item.qty
	}
	frm.set_value({
		"total_incoming_value": fg_item.basic_amount,
		"value_difference": 0
	})
	refresh_field(["total_incoming_value", "value_difference", "items"])
}