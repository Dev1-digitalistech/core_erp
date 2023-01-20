frappe.ui.form.on('Material Request', {
	schedule_date(frm) {
		frm.set_value("transaction_date", cur_frm.doc.schedule_date)
	},
	setup(frm) {
		frm.set_query("line", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			};
		});
	}
})

frappe.ui.form.off('Material Request Item', 'qty')
frappe.ui.form.on('Material Request Item', {
	qty: function (frm, doctype, name) {
		var d = locals[doctype][name];
		if (flt(d.qty) < flt(d.min_order_qty)) {
			frappe.msgprint(__("Warning: Material Requested Qty is less than Minimum Order Qty"));
		}

		const item = locals[doctype][name];
		if (!frm.doc.material_request_type == "Material Transfer" ){
			frm.events.get_item_data(frm, item);
		}
	},

	item_code(frm, cdt, cdn) {
		if (frm.doc.material_request_type == "Material Transfer for Manufacture") {
			var warehouse;
			var d = frappe.model.get_doc(cdt, cdn);
			if (d.item_code) {
				if (frm.doc.line.match('W.I.P.')) {
					frappe.db.get_value('Company', frm.doc.company, 'wip_wh').then(({ message }) => {
						frappe.model.set_value(cdt, cdn, "warehouse", message['wip_wh']);
					})
				}
				else {
					let num = frm.doc.line.match(/\d+/g)[0]
					let wip = "wip_line_" + num
					frappe.db.get_value('Company', frm.doc.company, wip).then(({ message }) => {
						frappe.model.set_value(cdt, cdn, "warehouse", message[wip]);
					})
				}
			}
		}
	}
})