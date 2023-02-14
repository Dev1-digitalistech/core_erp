from __future__ import unicode_literals
from frappe import _

def get_data():
	return [

		
		{
			"label": _("Permissions"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "User Role & Permission DFM",
					"doctype": "User"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "User Activity Log Report",
					"doctype": "Activity Log"
				},
				
				
			]
		},
	]