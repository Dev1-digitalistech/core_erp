$(document).ready( function() {
    erpnext.show_serial_batch_selector = function(frm, d, callback, on_close, show_dialog) {
		frappe.require("assets/core_erp/js/SerialNoBatchSelector.js", function() {
			new erpnext.SerialNoBatchSelector({
				frm: frm,
				item: d,
				warehouse_details: {
					type: "Warehouse",
					name: d.warehouse
				},
				callback: callback,
				on_close: on_close
			}, show_dialog);
		});
	};
    console.log('custom batch selector running')
})