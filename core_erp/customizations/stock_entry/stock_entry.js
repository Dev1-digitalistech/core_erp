frappe.ui.form.off("Stock Entry", "clean_up")
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
		if (frm.doc.stock_entry_type == 'Manufacture' && frm.doc.items) frm.call('update_default_batch_in_item')
	},
	refresh(frm) {
		frm.remove_custom_button('Material Request', "Get items from")
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
		}, __("Get items from"));

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
	setup(frm) {
		frm.set_query("line", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			}
		});
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