from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Accounts Payable"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "GST Purchase Register Dup",
					"doctype": "Purchase Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "TDS Payable Monthly",
					"doctype": "Purchase Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "TDS Computation Summaryadmin",
					"doctype": "Purchase Invoice"
				}
               
			],
			
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Invoice Register DFM",
					"doctype": "Purchase Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Invoice Register Without GST",
					"doctype": "Purchase Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Debit Note Register DFM",
					"doctype": "Purchase Receipt"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Credit Note Register DFM",
					"doctype": "Purchase Receipt"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "MRN Register DFM",
					"doctype": "Purchase Receipt"
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
					"name": "Payment Entry- Register DFM",
					"doctype": "Payment Entry"
				},
                  {
					"type": "report",
					"is_query_report": True,
					"name": "Journal Entry Register -DFM",
					"doctype": "Journal Entry"
				}
               
			],
			
			"label": _("Custom Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Budget Report",
					"doctype": "Budget"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Journal Entry Register",
					"doctype": "Journal Entry"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "TDS Payable Monthly with Net Total",
					"doctype": "Purchase Invoice"
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
               
			]
	
		}
	]