from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			
			"label": _("Stock Transactions"),
			"items": [
				
				{
					"type": "doctype",
					"name": "Gate Entry",
					"onboard": 1,
					"dependencies": ["Supplier"],
				},
				
			]

	
		},
		{
			
			"label": _("Custom Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "debit note test",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item List for analytics",
					"doctype": "Item"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "In-transit Report",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item Batch Expiry Status DFM",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "MRN Register with Approval Date",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Pending Reciept-In Transit",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "SND Transfer",
					"doctype": "Stock Entry"
				},
               
			],
	
		},
		{
			
			"label": _("Stock Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Balance 2",
					"doctype": "Stock Ledger Entry"
				},
               
			],
	
		},
		{
			"label": _("Other Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item Batch Expiry Within 15 days DFM",
					"doctype": "Stock Ledger Entry"
                },
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item Batch Expiry Within 7 Days DFM",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item Batch Expiry Within 16 - 30 days DFM",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch-Wise Balance History Report",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"MRN Register DFM",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"RM_PM Mat Issue",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"PO Register DFM",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"PO Reg",
					"doctype": "Purchase Order"
				},

				{
					"type": "report",
					"is_query_report": True,
					"name":"Material Request DFM",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Material Transfer DFM",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Material Issue DFM",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Material Transfer for MFG DFM",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Stock Balance without WIP",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Production Consumption Report DFM",
					"doctype": "Stock Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Plant Transfer DFM",
					"doctype": "Delivery Note"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Quality Inspection DFM",
					"doctype": "Quality Inspection"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name":"Gate Entry Register DFM",
					"doctype": "Gate Entry"
				},
				{
					"type":"report",
					"is_query_report":True,
					"name":"Warehouse Linewise Report",
					"doctype":"Stock Entry"
				},
				{
					"type":"report",
					"is_query_report":True,
					"name":"WIP QC Report",
					"doctype":"Quality Inspection"
				},

			]
		},
		{
			"label": _("Key Reports"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch Status",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Ledger for Store",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Stock Ledger for Accounts Summary",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Store Stock",
					"doctype": "Stock Ledger Entry"
				},
			]
		},


	]