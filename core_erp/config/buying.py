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
				},
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
					"name": "Address And Contacts",
					"doctype": "Address"
				}
            ],
			"label": _("Other Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Supplier List DFM",
					"doctype": "Supplier"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "PO Reg",
					"doctype": "Purchase Order"
				}
			],
				"label": _("Custom Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "PO Re",
					"doctype": "Purchase Order"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Test1",
					"doctype": "Purchase Order"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Vendor FSSAI Expiry within 30 days",
					"doctype": "Supplier"
				}
			]
		}
	]
