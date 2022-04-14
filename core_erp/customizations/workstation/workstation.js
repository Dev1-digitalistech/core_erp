frappe.ui.form.on('Workstation', {
	setup(frm) {
	    frm.set_query("wip_warehouse", function() {
    		return {
    			"filters": {
    				"company": frm.doc.company
    			}
    		};
    	});
    	frm.set_query("target_warehouse", function() {
    		return {
    			"filters": {
    				"company": frm.doc.company
    			}
    		};
    	});
	}
})