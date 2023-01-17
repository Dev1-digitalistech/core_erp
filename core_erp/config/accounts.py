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
					"name": "Journal Entry Register",
					"doctype": "Journal Entry"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Testing",
					"doctype": "Account"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Testing 2",
					"doctype": "Account"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Trial Balance with Group & Ledger Bifurcation",
					"doctype": "GL Entry"
				}
               
			],
	
		},
		{
			"label": _("Accounts Payable"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "TDS Payable Monthly",
					"doctype": "Purchase Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Monthly TDS Payable",
					"doctype": "GL Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "GST Purchase Register Dup",
					"doctype": "Purchase Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Overhead Expense",
					"doctype": "GL Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "TDS Computation Summary",
					"doctype": "Purchase Invoice"
				},

			],
		},
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "FG Costing",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"name": "Purchase Invoice Register DFM",
					"doctype": "Purchase Invoice",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Purchase Invoice Register Without GST",
					"doctype": "Purchase Invoice",
					"is_query_report": True,
				},

				{
					"type": "report",
					"name": "Debit Note Register DFM",
					"doctype": "Purchase Receipt",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Credit Note Register DFM",
					"doctype": "Purchase Receipt",
					"is_query_report": True,
                },
				{
					"type": "report",
					"name": "MRN Register DFM",
					"doctype": "Purchase Receipt",
					"is_query_report": True,
                },

				{
					"type": "report",
					"name": "GIN Register DFM",
					"doctype": "Purchase Receipt",
					"is_query_report": True,
                },
				{
					"type":"report",
					"name":"Payment Entry- Register DFM",
					"doctype":"Payment Entry"
				},
				{
					"type":"report",
					"name":"Journal Entry Register -DFM",
					"doctype":"Journal Entry"
				}

				

			],
		}
	]