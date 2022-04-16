import frappe
from core_erp.utils import get_fiscal_abbr

def on_submit(self,method=None):
	if self.rejected_qty:
		frappe.db.set_value("Purchase Invoice", self.return_against, "rejected_qty", 1)
	if self.short_qty:
		frappe.db.set_value("Purchase Invoice", self.return_against, "short_qty", 1)
	if not self.is_return:
		for i in self.items:
			if i.rejected_qty > 0:
				if not self.rejected_qty:
					record=frappe.db.sql_list('''select name from `tabPurchase Invoice` where return_against = %(name)s and rejected_qty = 1 
						and docstatus = 1''',{"name":self.name})
					if not record:
						frappe.throw("Kindly check Debit Note for Rejected quantity is created or not")
			if i.short_quantity > 0:
				if not self.short_qty:
					record=frappe.db.sql_list('''select name from `tabPurchase Invoice` where return_against = %(name)s and short_qty = 1
                                                       and docstatus = 1''',{"name":self.name})
					if not record:
						frappe.throw("Kindly check Debit Note for short quantity is created or not")

def autoname(self,method):	
	fiscal_yr_abbr = get_fiscal_abbr(doc.posting_date)
	if doc.is_return:
		doc.name = make_autoname("DN/"+doc.abbr+"/"+fiscal_yr_abbr+"/.#####")
	else:
		doc.name = make_autoname("PI/"+doc.abbr+"/"+fiscal_yr_abbr+"/.#####")