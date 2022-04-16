frappe.ui.form.on("Purchase Invoice", {
    refresh(frm){
        console.log("inn")
        var item_fields_stock = ['warehouse_section'];

	    cur_frm.fields_dict['items'].grid.set_column_disp(item_fields_stock,
		(cint(frm.doc.update_stock)==1 || cint(frm.doc.is_return)==1 ? true : false));

	    cur_frm.refresh_fields();
    },
    after_workflow_action(frm) {
        if (frm.doc.workflow_state == "Approved") {
            frappe.db.set_value("Purchase Invoice", frm.doc.name, {
                'pi_approval_date': frappe.datetime.now_datetime(),
                'pi_approved_by': frappe.session.user
            })

            cur_frm.reload_doc()

        }
    },
    validate(frm) {
        var total = 0;
        var total2 = 0;
        var total3 = 0;
        var total4 = 0;
        $.each(frm.doc.items || [], function(i, d) {
            total += flt(d.invoice_quantity);
            total2 += flt(d.short_quantity);
            d.amount_s = d.invoice_quantity * d.rate_s;
            total3 += flt(d.amount_s);
            total4 += flt(d.rejected_qty)
        // diff = d.rate_s - d.rate;
        // total4 += flt(diff);
            if (d.rate != d.rate_s) {
                frappe.msgprint("Kindly raise Debit Note for Rate Difference")
            }
        });
        frm.set_value("total_invoice_qty", total);
        frm.set_value("total_short_qty", total2);
        frm.set_value("total_invoice_amount", total3);
        frm.set_value("total_rejected", total4);
        // if (frm.doc.posting_date <= '2022-03-31') {
        //     if (frm.doc.is_return == 1 && frm.doc.__islocal) {
        //         frm.set_value('naming_series', "DN/.abbr./21-22/")
        //         //frm.set_value('naming_series',"DN-.abbr.-")

        //     }
        //     if (frm.doc.is_return == 0) {
        //         frm.set_value('naming_series', "PI/.abbr./21-22/")
        //         //frm.set_value('naming_series',"PI-.abbr.-")

        //     }
        // } else if (frm.doc.posting_date > '2022-03-31') {
        //     if (frm.doc.is_return == 1 && frm.doc.__islocal) {
        //         frm.set_value('naming_series', "DN/.abbr./22-23/")
        //         //frm.set_value('naming_series',"DN-.abbr.-")

        //     }
        //     if (frm.doc.is_return == 0) {
        //         frm.set_value('naming_series', "PI/.abbr./22-23/")
        //         //frm.set_value('naming_series',"PI-.abbr.-")

        //     }
    //    }
        for (var i = 0; i < cur_frm.doc.items.length; i++) {
            cur_frm.doc.purchase_order = cur_frm.doc.items[i].purchase_order;
            cur_frm.doc.purchase_receipt = cur_frm.doc.items[i].purchase_receipt
        }
        cur_frm.refresh_field('items')


    },
    posting_date(frm) {
        if ((frm.doc.posting_date) > frappe.datetime.get_today()) {
            frm.set_value('posting_date', frappe.datetime.get_today())
            frm.refresh();
            frappe.throw("Posting date Cannot be a future date")
        }
    },
});
frappe.ui.form.on("Purchase Invoice", "validate", function() {
    for (var i = 0; i < cur_frm.doc.items.length; i++) {
        cur_frm.doc.purchase_order = cur_frm.doc.items[i].purchase_order;
        cur_frm.doc.purchase_receipt = cur_frm.doc.items[i].purchase_receipt
    }
    cur_frm.refresh_field('items')
});


frappe.ui.form.on("Purchase Invoice", "validate", function(frm, cdt, cdn) {
    var total = 0;
    var total2 = 0;
    var total3 = 0;
    var total4 = 0;
    $.each(frm.doc.items || [], function(i, d) {
        total += flt(d.invoice_quantity);
        total2 += flt(d.short_quantity);
        d.amount_s = d.invoice_quantity * d.rate_s;
        total3 += flt(d.amount_s);
        total4 += flt(d.rejected_qty)
        // diff = d.rate_s - d.rate;
        // total4 += flt(diff);
        if (d.rate != d.rate_s) {
            frappe.msgprint("Kindly raise Debit Note for Rate Difference")
        }
    });
    frm.set_value("total_invoice_qty", total);
    frm.set_value("total_short_qty", total2);
    frm.set_value("total_invoice_amount", total3);
    frm.set_value("total_rejected", total4);
});
