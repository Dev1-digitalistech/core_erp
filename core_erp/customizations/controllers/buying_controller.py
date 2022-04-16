import frappe
from core_erp.customizations.budget.budget import validate_expense_against_budget

def validate_budget(self):
		if self.docstatus == 1:
			for data in self.get('items'):
				args = data.as_dict()
				args.update({
					'doctype': self.doctype,
					'company': self.company,
					'posting_date': (self.schedule_date
						if self.doctype == 'Material Request' else self.transaction_date)
				})

				validate_expense_against_budget(args)