frappe.ui.form.on('Work Order', {
	setup(frm) {
		frm.set_query("work_station", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			};
		});
		const slab = getSlab(frappe.datetime.now_date());

		frm.set_query("production_plan", function () {
			return {
				filters: {
					company: frm.doc.company,
					plan_date: ["between", [slab.monthStart, slab.monthEnd]],
					plan_to: ["between", [slab.monthStart, slab.monthEnd]],
					docstatus: 1,
					plan_type: "10 days-Production plan",
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


function getSlab(date) {
	const currentDate = new Date(date);
	const currentYear = currentDate.getFullYear();
	const currentMonth = currentDate.getMonth() + 1; // Months are zero-indexed

	// Calculate the first day and last day of the current month
	const monthStart = `${currentYear}-${currentMonth.toString().padStart(2, '0')}-01`;
	const monthEnd = `${currentYear}-${currentMonth.toString().padStart(2, '0')}-${new Date(currentYear, currentMonth, 0).getDate()}`;

	return {
		monthStart,
		monthEnd
	};
}
