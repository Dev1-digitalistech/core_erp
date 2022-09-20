frappe.query_reports['PO Reg'] = {
	filters: [
	{
					"fieldname":"from_date",
					"label": __("From Date"),
					"fieldtype": "Date",
					"width": "80",
					"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1)
			},
			{
					"fieldname":"to_date",
					"label": __("To Date"),
					"fieldtype": "Date",
					"width": "80",
					"default": frappe.datetime.get_today()
			},
			{
					"fieldname":"company",
					"label":__("Company"),
					"fieldtype": "Link",
					"options":"Company",
					"width":100,
					"reqd":1
			},
			{
					"fieldname":"po_type",
					"label":__("Po Type"),
					"fieldtype":"Link",
					"options":"PO Type",
					"reqd":1
			}
]
}
