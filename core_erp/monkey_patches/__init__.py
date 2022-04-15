from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.customizations.frappe.frappe import create_new_parent

from erpnext.manufacturing.doctype.bom.bom import BOM
from core_erp.customizations.bom.bom import get_exploded_items

from erpnext.stock.doctype.batch.batch import Batch
from core_erp.customizations.batch.batch import autoname

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from core_erp.customizations.purchase_receipt.purchase_receipt import po_required, get_gl_entries

from erpnext.accounts.doctype.budget.budget import Budget
from core_erp.customizations.budget.budget import autoname,validate_accounts

from erpnext.controllers.buying_controller import BuyingController
from core_erp.customizations.controllers.buying_controller import validate_budget

BuyingController.validate_budget = validate_budget

Budget.autoname = autoname
Budget.validate_accounts = validate_accounts

EmailAccount.create_new_parent = create_new_parent

BOM.get_exploded_items = get_exploded_items

Batch.autoname = autoname

PurchaseReceipt.po_required = po_required
PurchaseReceipt.get_gl_entries = get_gl_entries