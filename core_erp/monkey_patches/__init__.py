from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.overrides.frappe import create_new_parent

from erpnext.stock.doctype.item.item import Item
from core_erp.overrides.item import custom_autoname


EmailAccount.create_new_parent = create_new_parent

Item.autoname = custom_autoname