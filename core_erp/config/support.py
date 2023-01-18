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
					"name": "Issue Action Tracker",
					"doctype": "Issue"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Support Ticket Report",
					"doctype": "Issue"
				}
				
			]

	
		},
		


	]