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
		"fieldname":"issue_type",
		"label": __("Issue Type"),
		"fieldtype": "Link",
		"options": "Issue Type",
		"reqd":1
	},

	]
};
