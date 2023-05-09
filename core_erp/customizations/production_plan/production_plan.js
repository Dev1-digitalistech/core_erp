frappe.ui.form.off("Production Plan", "get_items_for_mr")
frappe.ui.form.off("Production Plan", "download_materials_required")
frappe.ui.form.on("Production Plan", {
	refresh(frm){
		console.log('working refresh')
	},
    get_items_for_mr(frm) {
		console.log("working")
		const set_fields = ['actual_qty', 'item_code','item_name', 'description', 'uom',
			'min_order_qty', 'quantity', 'sales_order', 'warehouse', 'projected_qty', 'material_request_type'];
		frappe.call({
			method: "erpnext.manufacturing.doctype.production_plan.production_plan.get_items_for_material_requests",
			freeze: true,
			args: {doc: frm.doc},
			callback: function(r) {
				if(r.message) {
					frm.set_value('mr_items', []);
					$.each(r.message, function(i, d) {
						var item = frm.add_child('mr_items');
						for (let key in d) {
							if (d[key] && in_list(set_fields, key)) {
								item[key] = d[key];
							}
						}
					});
				}
				refresh_field('mr_items');
			}
		});
	},

	download_materials_required: function(frm) {
		let get_template_url = 'erpnext.manufacturing.doctype.production_plan.production_plan.download_raw_materials';
		open_url_post(frappe.request.url, { cmd: get_template_url, doc: frm.doc });
	},


})