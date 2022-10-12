from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Issues Action Tracker",
					"doctype": "Issue"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Support Ticket Report",
					"doctype": "Issue"
				}
			],
   "label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Product For Ticket",
					
				},
                {
					"type": "doctype",
					"name": "Product Variants For Ticket",
					
				},
                {
					"type": "doctype",
					"name": "Ticket Type",
					
				}
			]
		}
	]
