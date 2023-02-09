# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	filters = frappe._dict(filters or {})
	data=get_data(filters)
	columns=get_columns()
	return columns, data

def get_columns():
	columns = [
			{
			"label": _("Item"),
			"options": "Item",
			"fieldname": "item",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Item Name"),
			"fieldname": "fg_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Company"),
			"options": "Company",
			"fieldname": "company",
			"fieldtype": "Link",
			"width": 150
		},	
		{
			"label": _("Weight Per Unit"),
			"fieldname": "weight_per_unit",
			"fieldtype": "Float",
			"width": 100
		},		
		{
			"label": _("Price Category"),
			"fieldname": "price_category",
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"label": _("Weight UOM"),
			"fieldname": "weight_uom",
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"label": _("UOM"),
			"fieldname": "fg_uom",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 100
		},		
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Float",
			"width": 100
		},		
		{
			"label": _("Rate of Material Based on"),
			"fieldname": "rm_cost_as_per",
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"label": _("With Operations"),
			"fieldname": "with_operations",
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"label": _("Inspection Required"),
			"fieldname": "inspection_required",
			"fieldtype": "Data",
			"width": 100
		},		
		{
			"label": _("Item Code"),
			"options": "Item",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"width": 100
		},		
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150
		},		
		{
			"label": _("Operation"),
			"fieldname": "operation",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("BOM no"),
			"options" : "BOM",
			"fieldname": "bom_no",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Net Qty"),
			"fieldname": "net_qty",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Gross Qty"),
			"fieldname": "qty",

			"fieldtype": "Float",

			"width": 100

		},

		{

			"label": _("UOM"),

			"fieldname": "uom",

			"fieldtype": "Data",

			"width": 100

		},

		{

			"label": _("Rate"),

			"fieldname": "rate",

			"fieldtype": "Float",

			"width": 100

		},

		{

			"label": _("Amount"),

			"fieldname": "amount",

			"fieldtype": "Float",

			"width": 100

		},

		{

			"label": _("Operating Cost"),

			"fieldname": "operating_cost",

			"fieldtype": "Float",

			"width": 100

		},

		{

			"label": _("Raw Material Cost"),

			"fieldname": "raw_material_cost",

			"fieldtype": "Float",

			"width": 100

		},

		{

			"label": _("Total Cost"),

			"fieldname": "total_cost",

			"fieldtype": "Float",

			"width": 100

		},
		{
			"label":_("Created By"),
			"fieldname":"owner",
			"fieldtype":"Data",
			"width":100
		},
		{
			"label":_("Creation Date"),
			"fieldname":"creation",
			"fieldtype":"Date",
			"width":100
		}
		]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and b.company = '%s'" % filters["company"]
	if filters.get("active_only") == 1:
		conditions += " and b.is_active = 1"
	if filters.get("is_default") == 1:
		conditions += " and b.is_default = 1"

	return conditions


def get_data(filters):
	conditions = get_conditions(filters)
	temp = frappe.db.sql("""select b.name, b.item,b.item_name as fg_name, b.company, b.weight_per_unit, b.price_category, b.weight_uom, b.uom as fg_uom, 
		b.quantity, b.currency, b.rm_cost_as_per, if(b.with_operations=1 ,'Yes','No'), if(b.inspection_required=1 ,"Yes","No"), 
		bi.item_code, bi.item_name, bi.operation, bi.bom_no, bi.description, bi.net_qty, bi.qty, bi.uom, bi.rate, b.creation,b.owner,
		bi.amount, b.operating_cost, b.raw_material_cost, b.total_cost, b.raw_material_cost 
		from `tabBOM` b ,`tabBOM Item` bi where bi.parent=b.name %s"""%conditions,as_dict=1)
	return temp
