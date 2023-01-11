// Copyright (c) 2016, Extension Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MRP Consumption Report"] = {
	"filters": [
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options":"Item Group",
			"reqd":1
		},
		{
			"fieldname":"item_sub_group",
			"label": __("Item SUb Group"),
			"fieldtype": "Link",
			"options":"Item Sub Group",
			"default": "Cereal",
			"reqd":1
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options":"Company",
			"default": "DFM Foods Ltd- G.Noida",
			"reqd":1
		}

	]
};
