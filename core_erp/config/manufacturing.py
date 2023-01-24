from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "FG Production",
					"reference_doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM vs Actual",
					"reference_doctype": "Production Plan"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM List",
					"reference_doctype": "BOM"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Pending PO Quatity",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Consumption 3",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Balance 2",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM Vs Actual",
					"reference_doctype": "Production Plan"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM Vs Actual 2",
					"doctype": "Production Plan"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "FG production new",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Semi Finished Production",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch-Wise Balance History",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "SND Transfer",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Planning Report",
					"doctype": "Production Plan"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Consumption Report DFM",
					"doctype": "Stock Entry"
				},
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
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM vs Actual Duplicate",
					"doctype": "Production Plan"
				},
				
			]
		},
	]