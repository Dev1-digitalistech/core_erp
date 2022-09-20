frappe.query_reports["Completed Work Orders Dup"] = {
	"filters": [
			{
					fieldname:"from_date",
					label: __("From Date"),
					fieldtype: "Date",
					width: "80",
					default: frappe.sys_defaults.year_start_date,
			},
			{
					fieldname:"to_date",
					label: __("To Date"),
					fieldtype: "Datetime",
					width: "80",
					default: frappe.datetime.get_today()
			},
			{
					fieldname: "company",
					label: __("Company"),
					fieldtype: "Link",
					options: "Company",
					default: frappe.defaults.get_user_default("Company"),
					reqd: 1
			}
]
}

