frappe.query_reports["Issue Test"] = {
	"filters": [
			{
					"fieldname": "from",
					"fieldtype": "Date",
					"label": __("From Date"),
					"default": frappe.datetime.month_start()
			},
			{
					"fieldname": "to",
					"fieldtype": "Date",
					"label": __("To Date"),
					"default": frappe.datetime.month_end()
			},
			{
					"fieldname": "ticket_type",
					"fieldtype": "Link",
					"label": __("Ticket type"),
					"options":"Ticket Type",
					"default": "IT Support"
			}
]
};


