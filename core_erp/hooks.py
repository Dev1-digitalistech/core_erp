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
		"on_submit": "core_erp.customizations.quality_inspection.custom_on_submit"
	},
	"Purchase Invoice":{
		"on_submit": "core_erp.customizations.purchase_invoice.custom_on_submit"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"core_erp.tasks.all"
# 	],
 	"daily": [
 		"core_erp.customizations.purchase_order.auto_close",
		"core_erp.customizations.frappe.auto_disable_users"
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
