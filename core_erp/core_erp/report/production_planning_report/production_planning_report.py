# Copyright (c) 2013, Extension Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns= get_columns(filters)
	data = get_data(filters)
	return columns,data

def get_columns(filters):
	columns =  [
		{"label":"Company","fieldname":"Company","fieldtype":"Link","options":"Purchase Order","width":150},
		{"label":"Planned Date","fieldname":"Planned Date","fieldtype":"Date","width":150},
		{"label":"Planned from","fieldname":"Planned from","fieldtype":"Data","width":100},
		{"label":"Planned to","fieldname":"Planned to","fieldtype":"Link","options":"Company","width":100},
		{"label":"Item Name:","fieldname":"Item Name","fieldtype":"Data","width":100},
		{"label":"Item Code","fieldname":"Item Code","fieldtype":"Data","width":150},
		{"label":"Planned Quantity","fieldname":"Planned Quantity","fieldtype":"float","width":150}
		]
	return columns

def get_condition(filters):
	cond=''
	if filters.get("from_date"):
		cond += "`tabProduction Plan`.posting_date>= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		cond += " and `tabProduction Plan`.posting_date <= '%s'" % filters["to_date"]

	if filters.get("company"):
		cond += "and `tabProduction Plan`.company = '%s'" % filters["company"]

	if filters.get("company"):
		cond += "and `tabProduction Plan Item`.item_code = '%s'" % filters["company"]

	return cond

def get_data(filters):
	cond=get_condition(filters)
	data=frappe.db.sql(f"""select `tabProduction Plan`.company as "Company",
		`tabProduction Plan`.posting_date as "Planned Date",
		`tabProduction Plan`.date_from as "Planned from",
		`tabProduction Plan`.date_to as "Planned to",
		`tabProduction Plan Item`.item_code as "Item code",
		`tabProduction Plan Item`.item_name as "Item name",
		`tabProduction Plan Item`.planned_qty as "Planned Quantity"

		from `tabProduction Plan`

		left join `tabProduction Plan Item` on`tabProduction Plan Item`.parent=`tabProduction Plan`.name
		where %s"""%cond,as_dict=1)
		
	return data
