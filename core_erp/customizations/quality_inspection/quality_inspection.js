frappe.ui.form.on("Quality Inspection", {
	setup: function (frm) {
		frm.set_query('quality_inspection_template', () => {
			return {
				filters: { 'custom_disable': 0 }
			}
		})
	}
});