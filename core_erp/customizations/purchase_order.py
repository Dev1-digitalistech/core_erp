import frappe
from datetime import datetime

@frappe.whitelist()
def auto_close():
	start_date = datetime.today()
	frappe.db.sql("""Update `tabPurchase Order` set status = 'Closed' where schedule_date < %s and docstatus = 1 and status != 'Closed'""",(datetime.date(start_date)))
