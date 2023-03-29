frappe.ui.form.on('Purchase Order', {
    setup(frm) {
        frm.fields_dict.items.grid.get_field('expense_account').get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "is_group": ['=', 0]
                }
            }
        }
    },
    after_workflow_action(frm) {
        if (frm.doc.workflow_state == "Pending for Controller approval" || frm.doc.workflow_state == "Pre Approved") {
            frappe.db.set_value("Purchase Order", frm.doc.name, {
                'l1_approval_date': frappe.datetime.now_datetime(),
                'l1_approved_by': frappe.session.user
            })

            cur_frm.reload_doc()

        }
        if (frm.doc.workflow_state == "CPO Approval") {
            frappe.db.set_value("Purchase Order", frm.doc.name, {
                'l2_approval_date': frappe.datetime.now_datetime(),
                'l2_approved_by': frappe.session.user
            })

            cur_frm.reload_doc()

        }
        if (frm.doc.workflow_state == "Approved") {
            frappe.db.set_value("Purchase Order", frm.doc.name, {
                'l3_approval_date': frappe.datetime.now_datetime(),
                'l3_approved_by': frappe.session.user
            })

            cur_frm.reload_doc()
        }


    },
    po_type(frm) {
        if (frm.doc.po_type) {
            frappe.db.get_value('PO Type', frm.doc.po_type, ['ins']).then(({
                message
            }) => {
                frm.doc.ins = message.ins
            })
        }
    },
    po_sub_type(frm) {
        if (frm.doc.po_sub_type == "Capex" && frm.doc.po_type == "Indirect") {
            frm.doc.ins = "C"
        } else {
            frappe.db.get_value('PO Type', frm.doc.po_type, ['ins']).then(({
                message
            }) => {
                frm.doc.ins = message.ins
            })
        }
    },
    validate(frm) {
        if (!frm.doc.ins) {
            frappe.db.get_value('PO Type', frm.doc.po_type, ['ins']).then(({
                message
            }) => {
                frm.doc.ins = message.ins
            })
        }
        let customer;
        frappe.call({
            freeze: true,
            async: false,
            method: "frappe.client.get",
            args: {
                doctype: "Supplier",
                name: frm.doc.supplier,
            },
            callback(r) {
                if (r.message) {
                    customer = r.message;

                }
            }
        });
        if (customer.category === "Raw material-Food") {
            if (frappe.datetime.get_day_diff(customer.fssai_valid_to_, frappe.datetime.get_today()) <= 30) {
                frappe.throw("Supplier FSSAI to be expired in 30 days")
            }
        }
        $.each(frm.doc.items || [], function(i, d) {
            d.po_qty = d.qty;
            if (d.rate <= 0) {
                frappe.throw("Item Rate can't be 0")
            }
            if (d.cost_center) {
                frappe.db.get_value('Cost Center', d.cost_center, ['company']).then(({
                    message
                }) => {
                    if (message.company != cur_frm.doc.company) {
                        frappe.validated = false;
                        frappe.msgprint({
                            title: __('Not Allowed'),
                            message: __("Cost Center " + d.cost_center + " does not belong to company " + cur_frm.doc.company),
                            indicator: 'red'
                        });
                    }
                });
            }
        });

    },
    refresh(frm) {
        console.log('hello ashish verma')
        frm.toggle_display("naming_series", false);
        //frm.set_df_property("company", "hidden", 0);
        if (cur_frm.doc.ship_gst_state == cur_frm.doc.supp_gst_state) {
            frm.set_value("tax_category", "In State(Purchase)")
        } else {
            frm.set_value("tax_category", "Out Of State(Purchase)")
        }
        cur_frm.refresh_fields()
    },
    transaction_date(frm) {
        if ((frm.doc.transaction_date) > frappe.datetime.get_today()) {
            frm.set_value('transaction_date', frappe.datetime.get_today())
            frm.refresh();
            frappe.throw("Transaction date Cannot be a future date")
        }
    },
    onload_post_render: function(frm) {
        if (frm.doc.__islocal) {
            frm.set_value('transaction_date', frappe.datetime.get_today())
        }

    }
})
