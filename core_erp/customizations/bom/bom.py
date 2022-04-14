import frappe
from frappe.utils import flt


def get_exploded_items(self):
	""" Get all raw materials including items from child bom"""
	self.cur_exploded_items = {}
	for d in self.get('items'):
		if d.bom_no and not frappe.db.get_value("BOM",d.bom_no,"disallow_explosion"):
			self.get_child_exploded_items(d.bom_no, d.stock_qty)
		else:
			self.add_to_cur_exploded_items(frappe._dict({
				'item_code'		: d.item_code,
				'item_name'		: d.item_name,
				'operation'		: d.operation,
				'source_warehouse': d.source_warehouse,
				'description'	: d.description,
				'image'			: d.image,
				'stock_uom'		: d.stock_uom,
				'stock_qty'		: flt(d.stock_qty),
				'rate'			: flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
				'include_item_in_manufacturing': d.include_item_in_manufacturing
			}))

@frappe.whitelist()
def set_uom_table(item):
	uom_table = []
	item_master = frappe.get_doc('Item',item)
	for s_item in item_master.uoms:
		temp = {}
		temp['uom'] = s_item.uom
		temp['conversion_factor'] = s_item.conversion_factor
		uom_table.append(temp)
	return uom_table
