frappe.query_reports['Quotation Comparison'] = {
	filters: [
		{
		"fieldname":"item",
		"label": __("Item"),
		"fieldtype": "Link",
		"options":"Item",
		"reqd":1
        }
    ]
}
