frappe.ui.form.on('Item', {
	item_group(frm) {
		if (frm.doc.item_group == 'Finished Goods') {
			cur_frm.set_df_property("weight_per_unit", "reqd", 1);
		}
	},
	validate(frm, cdt, cdn) {
		if (frm.doc.item_group == "Finished Goods" && frm.doc.weight_per_unit) {
			$.each(frm.doc.uoms || [], function (i, d) {
				if (i == 1) {
					frm.set_value("weight_per_box", frm.doc.weight_per_unit * flt(d.conversion_factor))
				}
			})

		}
	}

})
