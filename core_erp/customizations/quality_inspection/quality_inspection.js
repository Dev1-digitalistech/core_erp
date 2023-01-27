frappe.ui.form.off("Quality Inspection", "item_code");
frappe.ui.form.off("Quality Inspection", "quality_inspection_template");
frappe.ui.form.on("Quality Inspection", {
	item_code: function(frm) {
		if (frm.doc.item_code) {
			return frm.call({
				method: "get_quality_inspection_template",
				doc: frm.doc,
				callback: function() {
					refresh_field(['quality_inspection_template', 'readings','readings_2']);
				}
			});
		}
	},
	quality_inspection_template: function(frm) {
		if (frm.doc.quality_inspection_template && frm.doc.inspection_for_wip !=1) {
			return frm.call({
				method: "get_item_specification_details",
				doc: frm.doc,
				callback: function() {
					refresh_field('readings');
				}
			});
		}
		else{
                        return frm.call({
                        method:"get_wip_reading_template",
                        doc:frm.doc,
                        callback: function(){
                                refresh_field('readings_2')
                        }
                });
                }
	}
})

