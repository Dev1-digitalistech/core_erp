frappe.ui.form.on('Delivery Note', {
    set_basic_rate: function (frm, cdt, cdn) {
        const item = locals[cdt][cdn];
        item.transfer_qty = flt(item.qty) * flt(item.conversion_factor);

        const args = {
            'item_code': item.item_code,
            'posting_date': frm.doc.posting_date,
            'posting_time': frm.doc.posting_time,
            'warehouse': cstr(item.s_warehouse) || cstr(item.t_warehouse),
            'serial_no': item.serial_no,
            'company': frm.doc.company,
            'qty': item.s_warehouse ? -1 * flt(item.transfer_qty) : flt(item.transfer_qty),
            'voucher_type': frm.doc.doctype,
            'voucher_no': item.name,
            'allow_zero_valuation': 1,
        };

        if (item.item_code || item.serial_no) {
            console.log("first call")
            frappe.call({
                method: "erpnext.stock.utils.get_incoming_rate",
                args: {
                    args: args
                },
                callback: function (r) {
                    console.log(r)
                    frappe.model.set_value(cdt, cdn, 'rate', (r.message || 0.0));
                    //frm.events.calculate_basic_amount(frm, item);
                }
            });
        }
    },
    customer(frm) {
        frappe.model.with_doc("Customer", frm.doc.customer, function () {
            var tabletransfer = frappe.model.get_doc("Customer", frm.doc.customer)
            $.each(tabletransfer.internal_transfer_account, function (index, row) {
                if (row.company == frm.doc.company) {
                    frm.doc.expense_account = row.account
                    return;
                }
            })
            frm.refresh_field('internal_transfer_account')
        })
    },
    validate(frm) {
        frappe.model.with_doc("Customer", frm.doc.customer, function () {
            var tabletransfer = frappe.model.get_doc("Customer", frm.doc.customer)
            $.each(tabletransfer.internal_transfer_account, function (index, row) {
                if (row.company == frm.doc.company) {
                    frm.doc.expense_account = row.account
                    return;
                }
            })
            frm.refresh_field('internal_transfer_account')
        })
        $.each(frm.doc.items || [], function (i, d) {
            if (frm.doc.custom_transaction_type == "Internal Transfer" && d.item_code) {
                d.expense_account = frm.doc.expense_account
            }
        })
        frm.refresh_field("items")
    }
})

frappe.ui.form.on('Delivery Note Item', {
    qty: function (frm, cdt, cdn) {
        // frappe.msgprint(str(frm.doc.name))
        console.log(frm.doc.custom_transaction_type)
        if (frm.doc.custom_transaction_type != 'Normal') {
            let d = frappe.model.get_doc(cdt, cdn);
            if (d.item_code) {
                frm.events.set_basic_rate(frm, cdt, cdn);
            }
        }
    }
})