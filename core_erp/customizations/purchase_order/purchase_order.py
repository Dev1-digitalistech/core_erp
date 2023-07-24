import frappe
from datetime import datetime
from core_erp.utils import get_fiscal_abbr
from frappe.model.naming import make_autoname
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, cint

def autoname(doc, method = None):
	fiscal_yr_abbr = get_fiscal_abbr(doc.transaction_date)
	doc.name = make_autoname("PO."+doc.ins+ "/" +doc.abbr+"/"+fiscal_yr_abbr+"/.#####")

@frappe.whitelist()
def auto_close():
	start_date = datetime.today()
	frappe.db.sql("""Update `tabPurchase Order` set status = 'Closed' where schedule_date < %s and docstatus = 1 and status != 'Closed'""",(datetime.date(start_date)))



@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.qty = flt(obj.qty) - flt(obj.received_qty)
		target.pending_qty = flt(obj.qty) - flt(obj.received_qty)
		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (flt(obj.qty) - flt(obj.received_qty)) * \
			flt(obj.rate) * flt(source_parent.conversion_rate)

	doc = get_mapped_doc("Purchase Order", source_name,	{
		"Purchase Order": {
			"doctype": "Purchase Receipt",
			"field_map": {
				"per_billed": "per_billed",
				"supplier_warehouse":"supplier_warehouse",
				"po_type":"mrn_type"
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Purchase Order Item": {
			"doctype": "Purchase Receipt Item",
			"field_map": {
				"name": "purchase_order_item",
				"parent": "purchase_order",
				"bom": "bom",
				"rate":'rate_s',
				"material_request": "material_request",
				"material_request_item": "material_request_item"
			},
			"postprocess": update_item,
			"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty) and doc.delivered_by_supplier!=1
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	return doc


def set_missing_values(source, target):
	target.ignore_pricing_rule = 1
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")

