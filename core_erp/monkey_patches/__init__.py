from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.customizations.frappe import create_new_parent

from core_erp.customizations.bom.bom import get_exploded_items
from erpnext.manufacturing.doctype.bom.bom import BOM


EmailAccount.create_new_parent = create_new_parent

BOM.get_exploded_items = get_exploded_items