frappe.ui.form.on('Payment Entry', {
    get_invoice_outstanding: function(frm) {
		const today = frappe.datetime.get_today();
		const fields = [

                      {fieldtype:"Section Break", label: __("Due Date")},
                      {fieldtype:"Date", label: __("From Due Date"), fieldname:"from_due_date"},
                      {fieldtype:"Column Break"},
                      {fieldtype:"Date", label: __("To Due Date"), fieldname:"to_due_date", default:today},
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"),
				fieldname:"from_posting_date"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"), fieldname:"to_posting_date"},
//			{fieldtype:"Section Break", label: __("Due Date")},
//			{fieldtype:"Date", label: __("From Date"), fieldname:"from_due_date"},
//			{fieldtype:"Column Break"},
//			{fieldtype:"Date", label: __("To Date"), fieldname:"to_due_date"},
			{fieldtype:"Section Break", label: __("Outstanding Amount")},
			{fieldtype:"Float", label: __("Greater Than Amount"),
				fieldname:"outstanding_amt_greater_than", default: 0},
			{fieldtype:"Column Break"},
			{fieldtype:"Float", label: __("Less Than Amount"), fieldname:"outstanding_amt_less_than"},
			{fieldtype:"Section Break"},
			{fieldtype:"Check", label: __("Allocate Payment Amount"), fieldname:"allocate_payment_amount", default:1},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.validate_filters_data(frm, filters);
			frm.events.get_outstanding_documents(frm, filters);
		}, __("Filters"), __("Get Outstanding Documents"));
	}
})

frappe.ui.form.on('Payment Entry Reference', {
    reference_name: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];

        frappe.call({
            method: 'core_erp.customizations.purchase_invoice.purchase_invoice.get_payment_schedule',
            args: {
                doctype: child.reference_doctype,
                docname: child.reference_name,
            },
            callback: function(response){
                if (frm.doc.payment_type == "Pay"){
                    frappe.db.get_doc("Payment Terms Template",response.message.data)
                    .then(result => {
                        if (frm.doc.payment_type == "Pay"){
                            if (response && response.message) {
                                if (response.message.data){
                                    frappe.model.set_value(cdt, cdn, 'payment_term', result.terms[0].payment_term);
                                }
                            }
                            else{
                                console.error('Error fetching value. Response:', response);
                            }
                        }
                        });
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.error('Request Failed:', textStatus, errorThrown);
            }
        });
    }
});
