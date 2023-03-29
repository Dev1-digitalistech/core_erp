import frappe
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_mr(source_name,purpose,target_doc=None):
	def update_item_quantity(source, target, source_parent):
		pending_to_issue = flt(source.required_qty) - flt(source.transferred_qty)
#		desire_to_transfer = flt(source.required_qty) / max_finished_goods_qty * flt(for_qty)

		qty = 0
		if pending_to_issue > 0:
			qty = pending_to_issue

		if qty:
			target.qty = qty
			target.stock_qty = qty
			# target.warehouse= source_parent.wip_wh
			target.uom = frappe.get_value('Item', source.item_code, 'stock_uom')
			target.stock_uom = target.uom
			target.conversion_factor = 1
	def postprocess(source, target_doc):
		target_doc.material_request_type = purpose

	doc = get_mapped_doc('Work Order', source_name, {
                'Work Order': {
                        'doctype': 'Material Request',
                        'validation': {
                                'docstatus': ['=', 1]
                        }
                },
                'Work Order Item': {
                        'doctype': 'Material Request Item',
			'postprocess': update_item_quantity,
                        'condition': lambda doc: abs(doc.transferred_qty) < abs(doc.required_qty)
                },
        }, target_doc,postprocess)
	return doc
