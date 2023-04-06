frappe.ui.form.off("Purchase Receipt", "clean_up")
// frappe.ui.form.off("Purchase Receipt", "refresh")
frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
		// frm.remove_custom_button('Purchase Invoice','Create');
		frm.add_custom_button(__('PI'),
					function () {
						frappe.model.open_mapped_doc({
							method: "core_erp.customizations.purchase_receipt.purchase_receipt.make_purchase_invoice",
							frm: cur_frm
						})

					}, __("Create"));
		setTimeout(() => {
			frm.remove_custom_button('Purchase Order','Get items from');
			}, 10);
		// frm.remove_custom_button('Purchase Order', "Get items from")
				frm.add_custom_button(__('PO'),
					function () {
						if (!frm.doc.supplier) {
							frappe.throw({
								title: __("Mandatory"),
								message: __("Please Select a Supplier")
							});
						}

						frm.doc.taxes = [];
						erpnext.utils.map_current_doc({
							method: "core_erp.customizations.purchase_order.purchase_order.make_purchase_receipt",
							source_doctype: "Purchase Order",
							target: frm,
							setters: {
								supplier: frm.doc.supplier,
							},
							get_query_filters: {
								docstatus: 1,
								status: ["not in", ["Closed", "On Hold"]],
								per_received: ["<", 99.99],
								company: frm.doc.company
							}
						})
					}, __("Get Items From"));
			
		if (frm.doc.docstatus == 0) {
			frm.add_custom_button(__('Delivery Note'),
				function () {
					erpnext.utils.map_current_doc({
						method: "core_erp.customizations.delivery_note.delivery_note.make_purchase_receipt",
						source_doctype: "Delivery Note",
						target: me.frm,
						setters: {
							// supplier: me.frm.doc.supplier || undefined,
						},
						get_query_filters: {
							docstatus: 1,
							status: ["not in", ["Closed", "On Hold"]],
							// per_received: ["<", 99.99],
							// company: me.frm.doc.company
						}
					})
				}, __("Get Items From"));
		}
	},
	setup(frm) {
		cur_frm.fields_dict.gate_entry_no.get_query = function (doc) {
			if (!doc.is_return) {
				if(doc.transaction_type == "Stock Transfer"){
				return {
					filters: {
						supplier: doc.supplier,
						company: doc.company,
						docstatus: 1,
						gate_entry_type: "Sales Inward",
						status: "Open"
					}
				}
			}
		
		else {
			return {
				filters: {
					supplier: doc.supplier,
					company: doc.company,
					docstatus: 1,
					gate_entry_type: "Inward",
					status: "Open"
				}
				}
			}
		}
	}
	},
	after_workflow_action(frm) {
		if (frm.doc.workflow_state == "Approved") {
			frappe.db.set_value("Purchase Receipt", frm.doc.name, {
				'mrn_approval_date': frappe.datetime.now_datetime(),
				'mrn_approved_by': frappe.session.user
			})
			cur_frm.reload_doc()
		}
	},
	supplier(frm) {
		frappe.model.with_doc("Supplier", frm.doc.supplier, function () {
			var tabletransfer = frappe.model.get_doc("Supplier", frm.doc.supplier)
			$.each(tabletransfer.internal_transfer_account, function (index, row) {
				if (row.company == frm.doc.company) {
					frm.doc.expense_account = row.account
					return;
				}
			})
		})
	},
	before_save(frm){
	    $.each(frm.doc.items || [], function(i, d) {
	        frappe.db.get_value('Purchase Order',d.purchase_order,'po_type').then(({ message }) => {
	            frm.set_value('mrn_type',message.po_type)
	        })
	    })    
	},
	transaction_type(frm) {
		if (frm.doc.transfer_type == 'Normal') {
			frm.set_df_property('gate_entry_no', 'reqd', 1)
		}
		else {
			frm.set_df_property('gate_entry_no', 'reqd', 0)
		}
	},
	validate(frm) {
		frappe.model.with_doc("Supplier", frm.doc.supplier, function () {
			var tabletransfer = frappe.model.get_doc("Supplier", frm.doc.supplier)
			$.each(tabletransfer.internal_transfer_account, function (index, row) {
				if (row.company == frm.doc.company) {
					frm.doc.expense_account = row.account
					return;
				}
			})
		})
		if (frm.doc.transfer_type == 'Normal') {
			frm.set_df_property('gate_entry_no', 'reqd', 1)
		}
		else {
			frm.set_df_property('gate_entry_no', 'reqd', 0)
		}
		if (frm.doc.mrn_type == 'Normal') {
			frm.set_df_property('gate_entry_no', 'reqd', 1)
			frm.fields_dict.items.grid.toggle_reqd("manufacturing_date", 1)
			frm.fields_dict.items.grid.toggle_reqd("expiry_date", 1)
		}
		$.each(frm.doc.items || [], function (i, d) {
			if (!frm.doc.is_return) {
				var short_quantity = d.invoice_quantity - d.received_qty;
				if (short_quantity > 0) {
					d.short_quantity = short_quantity
				}
				else {
					d.short_quantity = 0
				}
			}
			if (d.item_code.slice(0, 2) == 'RM') {
				frm.fields_dict.items.grid.toggle_reqd("vendor_batch_no", 1)
			}
			d.total_gross_weight = d.received_qty * d.gross_weight_per_unit;
			d.amount_s = d.invoice_quantity * d.rate_s;
		});
		$.each(frm.doc.items || [], function (i, d) {
			if (frm.doc.transaction_type == "Internal Transfer" && d.item_code) {
				d.expense_account = frm.doc.expense_account
			}
		})
		frm.refresh_field("items")

		var total = 0;
		var total2 = 0;
		var total3 = 0;
		var total4 = 0;
		var reject = 0;
		$.each(frm.doc.items || [], function (i, d) {
			total += flt(d.invoice_quantity);
			total2 += flt(d.short_quantity);
			total3 += flt(d.total_gross_weight);
			total4 += flt(d.amount_s);
			reject += flt(d.rejected_qty)
		});
		frm.set_value("total_invoice_qty", total);
		frm.set_value("total_short_qty", total2);
		frm.set_value("total_gross_weight", total3);
		frm.set_value("total_invoice_amount", total4);
		frm.set_value("total_rejected_qty", reject);

		cur_frm.doc.supp = cur_frm.doc.supplier.substr(0, 5)
	},
	posting_date(frm) {
		if ((frm.doc.posting_date) > frappe.datetime.get_today()) {
			frm.set_value('posting_date', frappe.datetime.get_today())
			frm.refresh();
			frappe.throw("Posting date Cannot be a future date")
		}
	},
	tare_weight(frm) {
		var diff = (frm.doc.gross_weight - frm.doc.tare_weight)
		frm.set_value("net_weight", diff)
	}
});


frappe.ui.form.on("Purchase Receipt Item", {
	rate_s(frm, cdt, cdn) {
		var total = 0;
		$.each(frm.doc.items || [], function (i, d) {
			d.amount_s = d.invoice_quantity * d.rate_s;
			total += flt(d.amount_s);
			frm.refresh_fields();
		});
		frm.set_value("total_invoice_amount", total);
	},
	invoice_quantity(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var total = 0;
		var total1 = 0
		var total2 = 0
			row.received_qty = row.invoice_quantity
			row.qty = row.invoice_quantity
			row.amount_s = row.invoice_quantity * row.rate_s;
			frm.refresh_field("items");
		$.each(frm.doc.items, function (i, d) {
			total += flt(d.invoice_quantity);
			total1 += d.invoice_quantity
			total2 += flt(d.amount_s);
		})
		frm.set_value("total_qty", total1);
		frm.set_value("total_invoice_qty", total);
		frm.set_value("total_invoice_amount", total2);
	},
	received_qty(frm, cdt, cdn) {
		var total = 0;
		$.each(frm.doc.items || [], function (i, d) {
			total += flt(d.invoice_quantity) - flt(d.received_qty);
			var short_quantity = d.invoice_quantity - d.received_qty;
			if (short_quantity > 0) {
				d.short_quantity = short_quantity
			}
			else {
				d.short_quantity = 0
			}
		});
		if (total > 0) {
			frm.set_value("total_short_qty", total);
		}
		else {
			total = 0
			frm.set_value("total_short_qty", total);
		}
	},
	manufacturing_date(frm, cdt, cdn) {
		var d = frappe.model.get_doc(cdt, cdn);
		if (d.item_code) {
			frappe.db.get_value('Item', { name: d.item_code }, ['shelf_life_in_days', 'has_expiry_date'], (r) => {
				if (r.has_expiry_date && r.shelf_life_in_days) {
					// Calculate expiry date based on shelf_life_in_days
					var expiry_date = frappe.datetime.add_days(d.manufacturing_date, r.shelf_life_in_days);
					frappe.model.set_value(cdt, cdn, "expiry_date", expiry_date);
				}
			})
		}
	}
})
