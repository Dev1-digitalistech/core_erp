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
					"name": "Purchase Order Register Report",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Pending PO Quantity",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "RM_PM Mat Issue",
					"doctype": "Stock Entry"
				},
				
				
			]

	
		},
		{
			"label": _("Other Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Supplier List DFM",
					"reference_doctype": "Supplier"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "PO Reg",
					"reference_doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "MRP Consumption Report",
					"reference_doctype": "Stock Entry"
				},


			]
		},

		

	]