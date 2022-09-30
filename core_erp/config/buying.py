from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Key Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Planning Report",
					"doctype": "Production Plan"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Analytics",
					"doctype": "Purchase Order"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Trends",
					"doctype": "Purchase Order"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Requested Items To Be Ordered",
					"doctype": "Purchase Order"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Address And Contacts",
					"doctype": "Address"
				}
			]
		}
	]
