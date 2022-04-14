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
	"Quality Inspection": {
		"on_submit": "core_erp.customizations.quality_inspection.quality_inspection.custom_on_submit"
	},
	"Purchase Invoice":{
		"on_submit": "core_erp.customizations.purchase_invoice.purchase_invoice.custom_on_submit"
	},
	"Workstation": {
		"autoname": "core_erp.customizations.workstation.workstation.autoname"
	},
	"Item": {
		"autoname": "core_erp.customizations.item.item.custom_autoname"
	},
	"Purchase Receipt": {
		"validate" : "core_erp.customizations.purchase_receipt.purchase_receipt.validate",
		"on_update" : "core_erp.customizations.purchase_receipt.purchase_receipt.on_update"
	},
	"Supplier":{
		"autoname": "core_erp.customizations.supplier.supplier.autoname"
	}
}

doctype_js = {
    "Workstation": "customizations/workstation/workstation.js",
	"Work Order": "customizations/work_order/work_order.js",
	"BOM": "customizations/bom/bom.js"
}

override_whitelisted_methods = {
    "erpnext.stock.doctype.material_request.material_request.make_stock_entry": "core_erp.customizations.material_request.material_request.make_stock_entry",
	"erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice" : "core_erp.customizations.purchase_receipt.purchase_receipt.make_purchase_invoice"
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"core_erp.tasks.all"
# 	],
 	"daily": [
 		"core_erp.customizations.purchase_order.purchase_order.auto_close",
		"core_erp.customizations.frappe.frappe.auto_disable_users"
 	]
# 	"hourly": [
# 		"core_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"core_erp.tasks.weekly"
# 	]
# 	"monthly": [
# 		"core_erp.tasks.monthly"
# 	]
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

fixtures = ["Custom Field","Property Setter"]
