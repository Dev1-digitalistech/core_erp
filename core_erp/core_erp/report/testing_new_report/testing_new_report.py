# Copyright (c) 2023, Extension Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data


def get_columns():
	return [
		{"label":"Work Order","fieldname":"name","fieldtype":"Data","width":100},
		{"label":"Bom","fieldname":"bom_no","fieldtype":"Data","width":100},
		{"label":"Qty","fieldname":"net_qty","fieldtype":"Data","width":100},
	]

def get_data():
	data = frappe.db.sql("""select name,bom_no from `tabWork Order` """, as_dict=1)
	# list = []
	for row in data:
		# frappe.msgprint(str(row['bom_no']))
		var = frappe.db.sql(f"""select parent,net_qty from `tabBOM Item` where parent = '{row['bom_no']}' """,as_dict=1)
	frappe.msgprint(str(var))
		# for items in var:
		# 	if row['bom_no']==items['parent']:
		# 		row['net_qty']=items['net_qty']
	frappe.msgprint(str(data))

	return data