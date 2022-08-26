// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM vs Actual"] = {
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
					"fieldname":"company",
					"label": __("Company"),
					"fieldtype": "Link",
					"options":"Company",
					"reqd":1
	}
],
};


