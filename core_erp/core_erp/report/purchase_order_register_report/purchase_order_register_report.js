

frappe.query_reports["Purchase Order Register Report"] = {

	"filters": [

{

					"fieldname":"company",

					"label": __("Company"),

					"fieldtype": "Link", 

					"options": "Company",

					"width": "80",

					"default": "DFM Foods- Corporate Office"



			},

			{

					"fieldname":"from_date",

					"label": __("From Date"),

					"fieldtype": "Date",

					"width": "80",

					"default": frappe.datetime.add_days(frappe.datetime.get_today(),-7),

			},
	{

					"fieldname":"to_date",

					"label": __("To Date"),

					"fieldtype": "Date",

					"width": "80",

					"default": frappe.datetime.get_today()

			}

	]

};


