// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Warehouse Linewise Report"] = {
	"filters": [
		{
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd":1
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd":1
                },
                {
                        "fieldname": "company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options":"Company",
                        "width": "80",
                        "reqd":1
                },

	]
};

