// Copyright (c) 2016, Extension Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Issues Action Tracker"] = {
	"filters": [
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
		"fieldname":"ticket_type",
		"label": __("Ticket Type"),
		"fieldtype": "Link",
		"options": "Ticket Type",
		"reqd":1
	},

	]
};
