from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			
			"label": _("Custom Reports"),
			"items": [
				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Direct Order Status",
					"doctype": "Sales Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Pending Indent Status",
					"doctype": "Sales Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Update",
					"doctype": "Item"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Transit Report",
					"doctype": "Sales Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Dispatch Report",
					"doctype": "Sales Invoice"
				},				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Billing List",
					"doctype": "Sales Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Customer List for Power BI",
					"doctype": "Customer"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Customer List1",
					"doctype": "Customer"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Delivery Note List",
					"doctype": "Delivery Note"
				},
    
				{
					"type": "report",
					"is_query_report": True,
					"name": "Quotation List",
					"doctype": "Quotation"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order List",
					"doctype": "Sales Order"
				}
			],
			"label": _("Other Reports"),
			"items": [
					{
					"type": "report",
					"is_query_report": True,
					"name": "Address And Contacts",
					"doctype": "Address"
				},
				
    		],
			"label": _("Key Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Quotation Trends",
					"doctype": "Quotation"
				}
				
			]
		}
	]
