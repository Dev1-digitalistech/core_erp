frappe.ui.form.on('Budget', {
	onload_post_render(frm){
	    frm.set_query("account", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
//					report_type: "Profit and Loss",
					is_group: 0
				}
			}
		})
	}
})