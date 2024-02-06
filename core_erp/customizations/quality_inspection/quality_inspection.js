frappe.ui.form.on("Quality Inspection", {
	setup: function (frm) {
		frm.set_query('quality_inspection_template', () => {
			return {
				filters: { 'custom_disable': 0 }
			}
		})
	},
	validate: function(frm) {
        frm.doc.readings.forEach(reading => {
			if (reading.reading_1 && /[a-zA-Z]/.test(reading.reading_1)) {
				if (reading.reading_1.toLowerCase() === 'ok') {
					frappe.model.set_value(reading.doctype, reading.name, 'status', 'Accepted');
				} else if (reading.reading_1.toLowerCase() === 'not ok') {
					frappe.model.set_value(reading.doctype, reading.name, 'status', 'Rejected');
				}
			}
        });
    }
});