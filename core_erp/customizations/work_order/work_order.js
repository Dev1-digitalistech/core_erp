frappe.ui.form.on('Work Order', {
	setup(frm) {
		frm.set_query("work_station", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			};
		});
	},
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Create Material Request'), () => {
				frappe.call({
					method: "core_erp.customizations.work_order.work_order.make_mr",
					args: {
						'source_name': frm.doc.name,
						'purpose': 'Material Transfer for Manufacture'
					},
					callback: function (r) {
						console.log("call")
						var doclist = frappe.model.sync(r.message);
						frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
					}
				});
			}).addClass('btn-primary');
		}
	}
})