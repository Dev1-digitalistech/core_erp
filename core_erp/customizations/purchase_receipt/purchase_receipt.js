frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
		if (this.frm.doc.docstatus == 0) {
			this.frm.add_custom_button(__('Delivery Note'),
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
				}, __("Get items from"));
		}
	}
})