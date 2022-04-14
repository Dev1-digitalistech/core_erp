from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.customizations.frappe import create_new_parent

from erpnext.stock.doctype.item.item import Item
from core_erp.customizations.item import custom_autoname

from core_erp.customizations.bom.bom import get_exploded_items
from erpnext.manufacturing.doctype.bom.bom import BOM


EmailAccount.create_new_parent = create_new_parent

Item.autoname = custom_autoname

BOM.get_exploded_items = get_exploded_items