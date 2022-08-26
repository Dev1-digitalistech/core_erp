import frappe
from datetime import datetime
from core_erp.utils import get_fiscal_abbr
from frappe.model.naming import make_autoname

def autoname(doc, method = None):
	fiscal_yr_abbr = get_fiscal_abbr(doc.transaction_date)
	doc.name = make_autoname("PO."+doc.ins+ "/" +doc.abbr+"/"+fiscal_yr_abbr+"/.#####")

@frappe.whitelist()
def auto_close():
	start_date = datetime.today()
	frappe.db.sql("""Update `tabPurchase Order` set status = 'Closed' where schedule_date < %s and docstatus = 1 and status != 'Closed'""",(datetime.date(start_date)))
