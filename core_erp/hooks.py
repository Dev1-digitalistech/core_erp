from . import __version__ as app_version

app_name = "core_erp"
app_title = "DFM Foods Customization"
app_publisher = "Extension Technologies"
app_description = "Buying & Manifacturing customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@extensionerp.com"
app_license = "MIT"

app_include_js = "assets/core_erp/js/batch_selector_overide.js"

doctype_js = {
	"Supplier": "customizations/purchase_invoice/purchase_invoice2.js"
}


doctype_tree_js = {
    "Task": "customizations/task/task_tree.js",
}

doc_events = {
	"Task":{
        "validate":"core_erp.customizations.task.task.validate"
        },
	"Purchase Order": {
		"autoname": "core_erp.customizations.purchase_order.purchase_order.autoname"
	},
	"Batch": {
        "autoname": "core_erp.customizations.batch.batch.autoname",
		"before_naming":"core_erp.customizations.batch.batch.before_naming",
		# "before_insert":"core_erp.customizations.batch.batch.before_insert"
		# "before_insert":"core_erp.customizations.batch.batch.before_insert"
        },
	"Quality Inspection": {
		"on_submit": "core_erp.customizations.quality_inspection.quality_inspection.on_submit"
	},
	"Purchase Invoice":{
		"on_submit": "core_erp.customizations.purchase_invoice.purchase_invoice.on_submit",
		"autoname": "core_erp.customizations.purchase_invoice.purchase_invoice.autoname",
		"validate": "core_erp.customizations.purchase_invoice.purchase_invoice.validate"
	},
	"Workstation": {
		"autoname": "core_erp.customizations.workstation.workstation.autoname"
	},
	"Item": {
		"autoname": "core_erp.customizations.item.item.custom_autoname"
	},
	"Purchase Receipt": {
		"validate" : "core_erp.customizations.purchase_receipt.purchase_receipt.validate",
		"on_update" : "core_erp.customizations.purchase_receipt.purchase_receipt.on_update",
		"autoname" : "core_erp.customizations.purchase_receipt.purchase_receipt.autoname"
	},
	"Supplier":{
		"autoname": "core_erp.customizations.supplier.supplier.autoname"
	},
	"Stock Entry": {
		"after_insert": "core_erp.customizations.stock_entry.stock_entry.after_insert",
		# "on_submit": "core_erp.customizations.stock_entry.stock_entry.on_submit",
		"autoname": "core_erp.customizations.stock_entry.stock_entry.autoname"
	},
	"Issue":{
		"validate": "core_erp.customizations.issue.issue.validate",
		"autoname": "core_erp.customizations.issue.issue.autoname"
	},
		"Stock":{
		"get_data":"core_erp.config.stock.get_data"
	},
#		"Gate Entry":{
#			"validate":"core_erp.customizations.gate_entry.gate_entry.validate"
#			
#		}
}

# Issue only assign view permissions
permission_query_conditions = {
    "Issue":"core_erp.customizations.issue.issue.get_permission_query_condition"
}

doctype_js = {
	"Budget": "customizations/budget/budget.js",
	"Workstation": "customizations/workstation/workstation.js",
	"Work Order": "customizations/work_order/work_order.js",
	"BOM": "customizations/bom/bom.js",
	"Quality Inspection": "customizations/quality_inspection/quality_inspection.js",
	"Material Request": "customizations/material_request/material_request.js",
	"Stock Entry": "customizations/stock_entry/stock_entry.js",
	"Item": "customizations/item/item.js",
	"Purchase Order": "customizations/purchase_order/purchase_order.js",
	"Payment Entry": "customizations/payment_entry/payment_entry.js",
	"Purchase Invoice" : "customizations/purchase_invoice/purchase_invoice2.js",
	"Purchase Receipt": "customizations/purchase_receipt/purchase_receipt.js",
	"Delivery Note": "customizations/delivery_note/delivery_note.js",
    "Production Plan":"customizations/production_plan/production_plan.js",
}

override_whitelisted_methods = {
    "erpnext.stock.doctype.material_request.material_request.make_stock_entry":"core_erp.customizations.material_request.material_request.make_stock_entry",
	"erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice" : "core_erp.customizations.purchase_receipt.purchase_receipt.make_purchase_invoice",
	"erpnext._co.doctype.purchase_order.purchase_order.make_purchase_receipt":"core_erp.customizations.purchase_order.purchase_order.make_purchase_receipt"

}



scheduler_events = {
 	"daily": [
 		"core_erp.customizations.purchase_order.purchase_order.auto_close",
		"core_erp.customizations.frappe.frappe.auto_disable_users"
 	]
}

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]


#class override
from erpnext.controllers.status_updater import StatusUpdater
from core_erp.customizations.controllers.status_updater import update_prevdoc_status
StatusUpdater.update_prevdoc_status = update_prevdoc_status

from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from core_erp.customizations.purchase_invoice.purchase_invoice import set_tax_withholding_dup
PurchaseInvoice.set_tax_withholding = set_tax_withholding_dup

from erpnext.controllers.stock_controller import StockController
from core_erp.customizations.controllers.stock_controller import validate_serialized_batch_dup
StockController.validate_serialized_batch=validate_serialized_batch_dup



from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from core_erp.customizations.stock_entry.stock_entry import validate_batch_dup
StockEntry.validate_batch= validate_batch_dup


