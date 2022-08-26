from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	temp_data = get_data(filters)
	#print(temp_data[0])
	data = []
	for d in temp_data:
		#print(d)
		for item in d[d['work_order']]:
			data.append([d['company'], d['production_plan'], d['work_order'], d['bom_no'], d['fg_item'],d['fg_name'], d['fg_qty'], d['produced_qty'], item, d[d['work_order']][item]['item_name'],
			d[d['work_order']][item]['stock_entry'],d[d['work_order']][item]['net_qty'], d[d['work_order']][item]['stock_qty'], d[d['work_order']][item]['consumed_qty'], d[d['work_order']][item]['yield']  
			])

	return columns, data

def get_columns(filters):
	"""return columns"""
	columns = [
		{"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": "Production Plan", "fieldname": "production_plan", "fieldtype": "Link", "options": "Production Plan", "width": 150},
		{"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 150},
		{"label": "BOM No.", "fieldname": "bom_no", "fieldtype": "Link", "options": "BOM", "width": 150},
		{"label": "FG Item", "fieldname": "fg_item", "fieldtype": "Data", "width": 120},
		{"label": "FG Name", "fieldname": "fg_name", "fieldtype": "Data", "width": 180},
		{"label": "FG Item Qty", "fieldname": "fg_qty", "fieldtype": "Float", "width": 100},
		{"label": "FG Produced Qty", "fieldname": "produced_qty", "fieldtype": "Float", "width": 100},
		{"label": "Consumed Items", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 100},
		{"label": "Stock Entry", "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 150},
		{"label": "Net Qty", "fieldname": "net_qty", "fieldtype": "Float", "width": 100},
		{"label": "Gross Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
		{"label": "Consumed Qty", "fieldname": "consumed_qty", "fieldtype": "Float", "width": 100},
		{"label": "% Yield", "fieldname": "yield", "fieldtype": "Float", "width": 100}
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and date <= '%s'" % filters["to_date"]

	if filters.get("company"):
		conditions += " and company = '%s'" % filters["company"]
	else:
		frappe.throw('Please Select company first')
	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	d = frappe.db.sql("""SELECT company, production_plan ,name as work_order ,qty as fg_qty, produced_qty,
		production_item as fg_item, item_name as fg_name, bom_no FROM `tabWork Order` where docstatus = 1 and produced_qty > 0 %s """%conditions,as_dict=1)
	for r in d:
		r[r['work_order']] = get_exploded_items(r['bom_no'],{},r['fg_qty'],r['fg_qty'])
		se_name = frappe.get_list('Stock Entry',{'work_order': r['work_order']},'name')
		for se in se_name:
			temp=frappe.db.sql("""select item_code,sum(qty) as qty from `tabStock Entry Detail` sed, `tabStock Entry` se where sed.parent=%s and sed.parent = se.name and se.docstatus=1 and item_group!='Finished Goods' group by item_code""",se['name'],as_dict=1)
			for t in temp:
				try:
					r[r['work_order']][t['item_code']]['stock_entry'] = se['name']
					r[r['work_order']][t['item_code']]['consumed_qty'] = t['qty']
					r[r['work_order']][t['item_code']]['yield'] = (t['qty']/r[r['work_order']][t['item_code']]['stock_qty'])*100 
				except:
					pass
	return d


def get_exploded_items(bom,raw = {},s_q=0,n_q=0):
	bom_q = frappe.db.get_value('BOM',bom,'quantity')
	""" Get all raw materials including items from child bom"""
	items = frappe.db.sql("""select bi.item_code, bi.item_name, bi.bom_no, bi.stock_uom, bi.stock_qty, bi.net_qty, 
				bi.stock_qty / ifnull(%s, 1) AS stock_qty_consumed_per_unit, bi.net_qty / ifnull(%s, 1) AS net_qty_consumed_per_unit,
				 bi.include_item_in_manufacturing from `tabBOM Item` bi where bi.parent = %s"""%(bom_q,bom_q,frappe.db.escape(bom)), as_dict=1 )
	for d in items:
		if d['bom_no']:
			raw = get_exploded_items(d['bom_no'],raw,(s_q*d['stock_qty_consumed_per_unit']),(n_q*d['net_qty_consumed_per_unit']))
			#frappe.msgprint(str(raw))
		else:
			if d['item_code'] in raw:
				#frappe.msgprint(str(d['item_code']))
				raw[d['item_code']] = {
					'stock_entry'				: '',
					'item_name'				: d['item_name'],
					'stock_uom'				: d['stock_uom'],
					'stock_qty'				: raw[d['item_code']]['stock_qty'] + d['stock_qty_consumed_per_unit'] * s_q,
					'net_qty'				: raw[d['item_code']]['net_qty']  + d['net_qty_consumed_per_unit'] * n_q,
					'consumed_qty'                          : 0,
					'yield'					: 0,
					'include_item_in_manufacturing': d.get('include_item_in_manufacturing', 0)
				}
				#frappe.msgprint(str(raw[d['item_code']]))

			else:
				raw[d['item_code']] = {
					'stock_entry'				: '',
					'item_name'				: d['item_name'],
					'stock_uom'				: d['stock_uom'],
					'stock_qty'				: d['stock_qty_consumed_per_unit'] * s_q,
					'net_qty'				: d['net_qty_consumed_per_unit'] * n_q,
					'consumed_qty'				: 0,
					'yield'					: 0,
					'include_item_in_manufacturing': d.get('include_item_in_manufacturing', 0)
                                }
				#frappe.msgprint(str(raw[d['item_code']]))

	return raw

