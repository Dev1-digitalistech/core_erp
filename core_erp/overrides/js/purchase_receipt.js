// frappe.ui.form.on('Purchase Receipt', {
//     onload(frm) {
//         console.log("callll")
//         $.each(frm.doc.items || [], function(i, d) {
//             if (d.qty > 1 && d.pending_qty == 0) {
//                 d.pending_qty = d.qty;
//             }
//         });
//     },
//     after_workflow_action(frm) {
//         console.log("call" + frm.doc.workflow_state)
//         if (frm.doc.workflow_state == "Pending For Quality") {
//             frappe.call({
//                 method: "core_erp.overrides.purchase_receipt.create_quality_inspection",
//                 args: {
//                     'self': frm.doc.name
//                 }
//             })
//         }
//         if (frm.doc.workflow_state == "Approved") {
//             frappe.db.set_value("Purchase Receipt", frm.doc.name, {
//                 'mrn_approval_date': frappe.datetime.now_datetime(),
//                 'mrn_approved_by': frappe.session.user
//             })
//             cur_frm.reload_doc()
//         }
//     },
//     supplier(frm) {
//         frappe.model.with_doc("Supplier", frm.doc.supplier, function() {
//             var tabletransfer = frappe.model.get_doc("Supplier", frm.doc.supplier)
//             $.each(tabletransfer.internal_transfer_account, function(index, row) {
//                 if (row.company == frm.doc.company) {
//                     frm.doc.expense_account = row.account
//                     return;
//                 }
//             })
//         })
//     },
//     custom_transaction_type(frm) {
//         if (frm.doc.custom_transaction_type == 'Normal') {
//             frm.set_df_property('gate_entry_no', 'reqd', 1)
//         } else {
//             frm.set_df_property('gate_entry_no', 'reqd', 0)
//         }
//     },
//     validate(frm) {
//         cur_frm.doc.supp = cur_frm.doc.supplier.substr(0, 5)
//         frappe.model.with_doc("Supplier", frm.doc.supplier, function() {
//             var tabletransfer = frappe.model.get_doc("Supplier", frm.doc.supplier)
//             $.each(tabletransfer.internal_transfer_account, function(index, row) {
//                 if (row.company == frm.doc.company) {
//                     frm.doc.expense_account = row.account
//                     return;
//                 }
//             })
//         })
//         if (frm.doc.custom_transaction_type == 'Normal') {
//             frm.set_df_property('gate_entry_no', 'reqd', 1)
//         } else {
//             frm.set_df_property('gate_entry_no', 'reqd', 0)
//         }
//         if (frm.doc.mrn_type == 'Normal') {
//             frm.set_df_property('gate_entry_no', 'reqd', 1)
//             frm.fields_dict.items.grid.toggle_reqd("manufacturing_date", 1)
//             frm.fields_dict.items.grid.toggle_reqd("expiry_date", 1)
//         }
//         $.each(frm.doc.items || [], function(i, d) {
//             if (!frm.doc.is_return) {
//                 var short_quantity = d.invoice_quantity - d.received_qty;
//                 if (short_quantity > 0) {
//                     d.short_quantity = short_quantity
//                 } else {
//                     d.short_quantity = 0
//                 }
//             }
//             if (d.item_code.slice(0, 2) == 'RM') {
//                 frm.fields_dict.items.grid.toggle_reqd("vendor_batch_no", 1)
//             }
//             d.total_gross_weight = d.received_qty * d.gross_weight_per_unit;
//             d.amount_s = d.invoice_quantity * d.rate_s;
//         });
//         $.each(frm.doc.items || [], function(i, d) {
//             if (frm.doc.custom_transaction_type == "Internal Transfer" && d.item_code) {
//                 d.expense_account = frm.doc.expense_account
//             }
//         })
//         frm.refresh_field("items")
//     },
//     posting_date(frm) {
//         if ((frm.doc.posting_date) > frappe.datetime.get_today()) {
//             frm.set_value('posting_date', frappe.datetime.get_today())
//             frm.refresh();
//             frappe.throw("Posting date Cannot be a future date")
//         }
//     },
//     tare_weight(frm) {
//         var diff = (frm.doc.gross_weight - frm.doc.tare_weight)
//         frm.set_value("net_weight", diff)
//     }
// });
// cur_frm.fields_dict.gate_entry_no.get_query = function(doc) {
//     if (!doc.is_return) {
//         if(frm.doc.custom_transaction_type == "Stock Transfer"){
//             return {
//                 filters: {
//                     supplier: doc.supplier,
//                     company: doc.company,
//                     docstatus: 1,
//                     gate_entry_type: "Sales Inward",
//                     status: "Open"
//                 }
//             }
//         }
//      else {
//         return {
//             filters: {
//                 supplier: doc.supplier,
//                 company: doc.company,
//                 docstatus: 1,
//                 gate_entry_type: "Inward",
//                 status: "Open"
//             }
//         }
//     }
// }
// }

// frappe.ui.form.on("Purchase Receipt Item", "rate_s", function(frm, cdt, cdn) {
//     var total = 0;
//     $.each(frm.doc.items || [], function(i, d) {
//         d.amount_s = d.invoice_quantity * d.rate_s;
//         total += flt(d.amount_s);
//         frm.refresh_fields();
//     });
//     frm.set_value("total_invoice_amount", total);
// });
// frappe.ui.form.on("Purchase Receipt Item", "invoice_quantity", function(frm, cdt, cdn) {
//     var total = 0;
//     var total1 = 0
//     var total2 = 0
//     $.each(frm.doc.items || [], function(i, d) {
//         total += flt(d.invoice_quantity);
//         d.received_qty = d.invoice_quantity
//         d.qty = d.invoice_quantity
//         d.amount_s = d.invoice_quantity * d.rate_s;
//         total1 += d.invoice_quantity
//         total2 += flt(d.amount_s);
//         frm.refresh_fields();
//     });
//     frm.set_value("total_qty", total1);
//     frm.set_value("total_invoice_qty", total);
//     frm.set_value("total_invoice_amount", total2);
// });
// frappe.ui.form.on("Purchase Receipt Item", "received_qty", function(frm, cdt, cdn) {
//     var total = 0;
//     $.each(frm.doc.items || [], function(i, d) {
//         total += flt(d.invoice_quantity) - flt(d.received_qty);
//         var short_quantity = d.invoice_quantity - d.received_qty;
//         if (short_quantity > 0) {
//             d.short_quantity = short_quantity
//         } else {
//             d.short_quantity = 0
//         }
//     });
//     if (total > 0) {
//         frm.set_value("total_short_qty", total);
//     } else {
//         total = 0
//         frm.set_value("total_short_qty", total);
//     }
// });
// frappe.ui.form.on("Purchase Receipt Item", "manufacturing_date", function(frm, cdt, cdn) {
//     var d = frappe.model.get_doc(cdt, cdn);
//     if (d.item_code) {
//         frappe.db.get_value('Item', {
//             name: d.item_code
//         }, ['shelf_life_in_days', 'has_expiry_date'], (r) => {
//             if (r.has_expiry_date && r.shelf_life_in_days) {
//                 console.log(r.shelf_life_in_days)
//                 //console.log(frm.doc.)
//                 // Calculate expiry date based on shelf_life_in_days
//                 var expiry_date = frappe.datetime.add_days(d.manufacturing_date, r.shelf_life_in_days);
//                 frappe.model.set_value(cdt, cdn, "expiry_date", expiry_date);
//                 console.log(d.expiry_date)
//             }
//         })
//     }
// });
// frappe.ui.form.on("Purchase Receipt", "validate", function(frm, cdt, cdn) {
//     var total = 0;
//     var total2 = 0;
//     var total3 = 0;
//     var total4 = 0;
//     var reject = 0;
//     console.log("inn")
//     $.each(frm.doc.items || [], function(i, d) {
//         total += flt(d.invoice_quantity);
//         total2 += flt(d.short_quantity);
//         total3 += flt(d.total_gross_weight);
//         total4 += flt(d.amount_s);
//         reject += flt(d.rejected_qty)
//     });
//     frm.set_value("total_invoice_qty", total);
//     frm.set_value("total_short_qty", total2);
//     frm.set_value("total_gross_weight", total3);
//     frm.set_value("total_invoice_amount", total4);
//     frm.set_value("total_rejected_qty", reject);
// });