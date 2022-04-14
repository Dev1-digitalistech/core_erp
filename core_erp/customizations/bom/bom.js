frappe.ui.form.on('BOM', {
	item(frm) {
		if (frm.doc.item) {
			frappe.call({
				method: "core_erp.customizations.bom.bom.set_uom_table",
				args: {
					'item': frm.doc.item
				},
				callback: function (r) {
					if (r.message) {
						console.log(r.message)
						let message_body = r.message;
						frm.doc.uoms = []
						for (var i in message_body) {
							frm.add_child("uoms");
							frm.fields_dict.uoms.get_value()[i].uom = message_body[i].uom;
							frm.fields_dict.uoms.get_value()[i].conversion_factor = message_body[i].conversion_factor;
						}
						frm.refresh_fields("uoms")
					}
				}

			})
		}
	}
})