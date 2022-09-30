from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Stock Transactions"),
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
					"doctype": "Purchase Invoice"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Credit Note Register DFM",
					"doctype": "Purchase Invoice"
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
					"name": "Production Planning Report",
					"doctype": "Production Plan"
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
					"name": "Production Planning Report",
					"doctype": "Production Plan"
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
					"name": "Production Planning Report",
					"doctype": "Production Plan"
				},
                {
					"type": "report",
					"is_query_report": True,
					"name": "Production Planning Report",
					"doctype": "Production Plan"
				},
			]
		}
	]