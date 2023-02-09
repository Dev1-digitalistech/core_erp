frappe.query_reports["BOM List"] = {
	"filters": [
			{
					"fieldname":"company",
					"label": __("Company"),
					"fieldtype": "Link",
					"options":"Company"
		},
	{
		"fieldname" : "active_only",
		"label": __("Active Only"),
		"fieldtype": "Check"
	},
	{
		"fieldname" : "is_default",
		"label": __("Is Default"),
		"fieldtype": "Check"
	}
],
};


