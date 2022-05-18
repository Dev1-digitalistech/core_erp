from frappe.email.doctype.email_account.email_account import EmailAccount
from core_erp.customizations.frappe.frappe import create_new_parent

# from erpnext.manufacturing.doctype.bom.bom import BOM
# from core_erp.customizations.bom.bom import get_exploded_items

from erpnext.stock.doctype.batch.batch import Batch
from core_erp.customizations.batch.batch import autoname

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from core_erp.customizations.purchase_receipt.purchase_receipt import po_required, get_gl_entries

from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection
from core_erp.customizations.quality_inspection.quality_inspection import get_item_specification_details, \
				get_quality_inspection_template, update_qc_reference

from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from core_erp.customizations.stock_entry.stock_entry import update_default_batch_in_item, validate_work_order, \
				set_basic_rate_for_finished_goods
				
from erpnext.accounts.doctype.budget.budget import Budget
from core_erp.customizations.budget.budget import autoname,validate_accounts

from erpnext.controllers.buying_controller import BuyingController
from core_erp.customizations.controllers.buying_controller import validate_budget

from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from core_erp.customizations.purchase_invoice.purchase_invoice import pr_required,set_tax_withholding

from erpnext.controllers.accounts_controller import AccountsController
from core_erp.customizations.controllers.accounts_controller import validate

from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from core_erp.customizations.controllers.taxes_and_totals import calculate_item_values,get_current_tax_amount

calculate_taxes_and_totals.calculate_item_values = calculate_item_values
calculate_taxes_and_totals.get_current_tax_amount = get_current_tax_amount

AccountsController.validate = validate

PurchaseInvoice.pr_required = pr_required
PurchaseInvoice.set_tax_withholding = set_tax_withholding

BuyingController.validate_budget = validate_budget

Budget.autoname = autoname
Budget.validate_accounts = validate_accounts

EmailAccount.create_new_parent = create_new_parent

# BOM.get_exploded_items = get_exploded_items

Batch.autoname = autoname

PurchaseReceipt.po_required = po_required
PurchaseReceipt.get_gl_entries = get_gl_entries

QualityInspection.get_item_specification_details = get_item_specification_details
QualityInspection.get_quality_inspection_template = get_quality_inspection_template
QualityInspection.update_qc_reference = update_qc_reference

StockEntry.update_default_batch_in_item = update_default_batch_in_item
StockEntry.validate_work_order = validate_work_order
StockEntry.set_basic_rate_for_finished_goods = set_basic_rate_for_finished_goods
