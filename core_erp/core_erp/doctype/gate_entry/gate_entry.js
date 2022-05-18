// Copyright (c) 2022, Extension Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry Details", "invoice_qty", function(frm, cdt, cdn) {
    var total = 0;
    $.each(frm.doc.items || [], function(i, d) {
        total += flt(d.invoice_qty);
    });
    frm.set_value("total_inv_qty", total);
});

cur_frm.fields_dict.purchase_order.get_query = function(doc) {
    return {
        filters: {
            supplier: doc.supplier,
            company: doc.company,
            docstatus: 1,
            per_received: ["<", 99.99]
        }
    }
}

frappe.ui.form.on("Gate Entry", "validate", function(frm) {
    if (frm.doc.__islocal) {
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Gate Entry",
                fieldname: "name",
                filters: {
                    supplier: frm.doc.supplier,
                    supplier_bill_no: frm.doc.supplier_bill_no
                }
            },
            callback: function(response) {
                var supp = response.message;
                let s = new Date(supp['date'])
                var d = new Date('2021-03-31')
                //console.log(s>d)
                //console.log(s)
                if ((Object.keys(supp).length > 0) && (s > d)) {
                    frappe.msgprint("Same bill with the Same Supllier Already Exist in Record.");
                    frappe.validated = false;
                    return false;


                }
            }
        });
    }
});
