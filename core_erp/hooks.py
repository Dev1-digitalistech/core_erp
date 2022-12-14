from . import __version__ as app_version

app_name = "core_erp"
app_title = "DFM Foods Customization"
app_publisher = "Extension Technologies"
app_description = "Buying & Manifacturing customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@extensionerp.com"
app_license = "MIT"

doc_events = {
	"Purchase Order": {
		"autoname": "core_erp.customizations.purchase_order.purchase_order.autoname"
	},
	# "Quality Inspection": {
	# 	"on_submit": "core_erp.customizations.quality_inspection.quality_inspection.on_submit"
	# },
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
		"validate": "core_erp.customizations.issue.issue.validate"
	}
}

# Issue only assign view permissions
permission_query_conditions = {
    "Issue":"core_erp.customizations.issue.issue.get_permission_query_condition"
}

# doctype_js = {
# 	"Budget": "customizations/budget/budget.js",
# 	"Workstation": "customizations/workstation/workstation.js",
# 	"Work Order": "customizations/work_order/work_order.js",
# 	"BOM": "customizations/bom/bom.js",
# 	"Quality Inspection": "customizations/quality_inspection/quality_inspection.js",
# 	"Material Request": "customizations/material_request/material_request.js",
# 	"Stock Entry": "customizations/stock_entry/stock_entry.js",
# 	"Item": "customizations/item/item.js",
# 	"Purchase Order": "customizations/purchase_order/purchase_order.js",
# 	"Payment Entry": "customizations/payment_entry/payment_entry.js",
# 	"Purchase Invoice" : "customizations/purchase_invoice/purchase_invoice.js",
# 	"Purchase Receipt": "customizations/purchase_receipt/purchase_receipt.js",
# 	"Delivery Note": "customizations/delivery_note/delivery_note.js",
# }

override_whitelisted_methods = {
    "erpnext.stock.doctype.material_request.material_request.make_stock_entry": "core_erp.customizations.material_request.material_request.make_stock_entry",
	"erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice" : "core_erp.customizations.purchase_receipt.purchase_receipt.make_purchase_invoice"

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


fixtures=[
	{"dt": "Report", "filters": [
				[
					"name", "=","FG Costing"
				]
			]}

]
