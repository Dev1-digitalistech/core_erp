from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Projects"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
                    "label":"Task Tree",
					"name": "Task",
					"route": "#Tree/Task",
					"description": _("Project activity / task."),
					"onboard": 1,
				},

			]
		}
    ]