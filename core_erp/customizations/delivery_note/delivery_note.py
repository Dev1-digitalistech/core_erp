import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.doctype.item.item import get_item_defaults

@frappe.whitelist(allow_guest=True)
def make_purchase_receipt(source_name, target_doc=None, ignore_permissions=False):
	def update_item(obj,target,source_parent):
		item_defaults = get_item_defaults(target.item_code, source_parent.customer).get('item_defaults')
		for i in item_defaults:
			if i.company == source_parent.customer:
				target.warehouse = i.default_warehouse
	def set_missing_values(source,target):
		pass

	doclist = get_mapped_doc("Delivery Note", source_name, {
                        "Delivery Note": {
                                "doctype": "Purchase Receipt",
                                "validation": {
                                        "docstatus": ["=", 1]
                                },
		"field_no_map": ['company']
                        },
                        "Delivery Note Item": {
                                "doctype": "Purchase Receipt Item",
                                "field_map": [
                                        ["name", "prevdoc_detail_docname"],
                                        ["parent", "prevdoc_docname"],
                                        ["parenttype", "prevdoc_doctype"],
                                        ["uom", "stock_uom"],
                                        ["uom", "uom"],
					["delivery_note","parent"],
					["batch_no","batch_no"]
                                ],
		"postprocess" : update_item
                        },
                }, target_doc, ignore_permissions=ignore_permissions)
	return doclist