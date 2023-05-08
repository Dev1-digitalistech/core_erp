frappe.ui.form.off("Producton Plan", "get_items_for_mr")
frappe.ui.form.on('Production Plan', {
    get_items_for_mr(frm) {
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

})