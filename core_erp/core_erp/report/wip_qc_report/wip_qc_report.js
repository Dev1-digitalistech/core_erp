frappe.query_reports["WIP QC Report"] = {
	"filters":[
		{
			"fieldname":"from",
			"label":"From Date",
			"fieldtype":"Date",
			"default":frappe.datetime.add_days(frappe.datetime.get_today(), -30)
		},
		{
			"fieldname":"to",
			"label":"To Date",
			"fieldtype":"Date",
			"default":frappe.datetime.get_today()
		},
		{
			"fieldname":"company",
			"label":__("Company"),
			"fieldtype":"Link",
			"options":"Company",
			"default":frappe.defaults.get_user_default("Company"),
			"reqd":1
		}
	]
};
