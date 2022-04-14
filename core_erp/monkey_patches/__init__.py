from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.customizations.frappe.frappe import create_new_parent

from erpnext.manufacturing.doctype.bom.bom import BOM
from core_erp.customizations.bom.bom import get_exploded_items

from erpnext.stock.doctype.batch.batch import Batch
from core_erp.customizations.batch.batch import autoname

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from core_erp.customizations.purchase_receipt.purchase_receipt import po_required, get_gl_entries


EmailAccount.create_new_parent = create_new_parent

BOM.get_exploded_items = get_exploded_items

Batch.autoname = autoname

PurchaseReceipt.po_required = po_required
PurchaseReceipt.get_gl_entries = get_gl_entries