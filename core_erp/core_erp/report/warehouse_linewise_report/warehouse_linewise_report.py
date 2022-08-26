# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now, date_diff

def execute(filters=None):
	columns, data = [], []
	data=get_items(filters)
	columns=get_columns()
	return columns, data

def get_columns():
	return [
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 100},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 100},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
		{"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 120, "convertible": "qty"},
		{"label": _("Return To Store"), "fieldname": "store_return", "fieldtype": "Float", "width": 120, "convertible": "qty"},
		{"label": _("Receipt"), "fieldname": "receipt", "fieldtype": "Float", "width": 120, "convertible": "qty"},
		{"label": _("Transfer to Another Line"), "fieldname": "transfer_to_another", "fieldtype": "Float", "width": 120, "convertible": "qty"},
		{"label":_("Receipt from Another Line"),"fieldname":"receipt_from_another","fieldtype":"Float","width":120,"convertible":"qty"},
		{"label":_("Consumption"),"fieldname":"consumed","fieldtype":"Float","width":120,"convertible":"qty"},
		{"label":_("Closing"),"fieldname":"closing","fieldtype":"Float","width":120,"convertible":"qty"}
		]

def get_item_opening(filters,items):
	conditions=""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " sle.posting_date <= %s and sle.company=%s"%(frappe.db.escape(filters.get("to_date")),frappe.db.escape(filters.get("company")))
	else:
		frappe.throw(_("'To Date' is required"))
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))
	item_conditions_sql=''

	sle=frappe.db.sql("""select sle.posting_date,sle.actual_qty,sle.qty_after_transaction, sle.item_code,sle.warehouse from `tabStock Ledger Entry` sle where %s 
				order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty"""%conditions,as_dict=1)
	open={}
	closing={}
	for d in sle:
		try:
			if open[f"{d.item_code}{d.warehouse}"]:
				if d.posting_date < from_date:
					open[f"{d.item_code}{d.warehouse}"]+=d.actual_qty
		except:
			open[f"{d.item_code}{d.warehouse}"]=d.actual_qty
		try:
			if closing[f"{d.item_code}{d.warehouse}"]:
				closing[f"{d.item_code}{d.warehouse}"]+=d.actual_qty
		except:
			closing[f"{d.item_code}{d.warehouse}"]=d.actual_qty

	return {"open":open,"closing":closing}

def get_stock_entries(filters,items):
	conditions=""
	conditions="and se.posting_date between %s and %s and se.company=%s"%(frappe.db.escape(filters.get("from_date")),frappe.db.escape(filters.get("to_date")),frappe.db.escape(filters.get("company")))
	entries=frappe.db.sql('''select se.name,se.stock_entry_type,sed.s_warehouse,sed.t_warehouse,sed.item_code,sed.qty from `tabStock Entry` se,`tabStock Entry Detail` sed where
			sed.parent=se.name and se.docstatus=1 %s'''%conditions,as_dict=1)
	
	receipt={}
	store_return={}
	transfer_to_another={}
	receipt_from_another={}
	consumed={}
	for entry in entries:
		if entry.t_warehouse and (entry.stock_entry_type=="Material Receipt" or entry.stock_entry_type=="Material Transfer for Manufacture" or entry.stock_entry_type=="Material Transfer"):
			try:
				receipt[f"{entry.item_code}{entry.t_warehouse}"]+=entry.qty
			except:
				receipt[f"{entry.item_code}{entry.t_warehouse}"]=entry.qty
		if entry.s_warehouse and entry.stock_entry_type=="Material Transfer" and not "Work in Progress" in entry.t_warehouse:
			try:
				store_return[f"{entry.item_code}{entry.s_warehouse}"]+=entry.qty
			except:
				store_return[f"{entry.item_code}{entry.s_warehouse}"]=entry.qty
		if entry.s_warehouse and entry.stock_entry_type=="Material Transfer":
			try:
				transfer_to_another[f"{entry.item_code}{entry.s_warehouse}"]+=entry.qty
			except:
				transfer_to_another[f"{entry.item_code}{entry.s_warehouse}"]=entry.qty
		if entry.stock_entry_type=="Material Transfer" and "Progress-Line" in entry.s_warehouse and entry.t_warehouse :
			try:
				receipt_from_another[f"{entry.item_code}{entry.t_warehouse}"]+=entry.qty
			except:
				receipt_from_another[f"{entry.item_code}{entry.t_warehouse}"]=entry.qty
		if "PDE" in entry.name or (entry.stock_entry_type=="Material Issue" and entry.s_warehouse):
			try:
				consumed[f"{entry.item_code}{entry.s_warehouse}"]+=entry.qty
			except:
				consumed[f"{entry.item_code}{entry.s_warehouse}"]=entry.qty
	return {"receipt":receipt,"store_return":store_return,"transfer_to_another":transfer_to_another,"receipt_another":receipt_from_another,"consumed":consumed}


def get_items(filters):
	items_conditions=""
	if filters.get("company"):
		items_conditions="and se.company=%s"%frappe.db.escape(filters.get("company"))
	all_items=frappe.db.sql('''select sed.item_code,sed.item_name,sed.item_group,if(sed.s_warehouse is not null,sed.s_warehouse,sed.t_warehouse) as warehouse,
				sed.stock_uom,sed.parent,se.company from `tabStock Entry Detail` sed,`tabStock Entry` se where sed.parent=se.name and se.docstatus=1 %s
				group by warehouse,sed.item_code '''%items_conditions,as_dict=1)
	op_close=get_item_opening(filters,all_items)
	entries=get_stock_entries(filters,all_items)
	for item in all_items:
		try:
			item.opening_qty=op_close["open"][f"{item.item_code}{item.warehouse}"]
		except:
			item.opening_qty=0
		try:
			item.receipt=entries["receipt"][f"{item.item_code}{item.warehouse}"]
		except:
			item.receipt=0
		try:
			item.store_return=entries["store_return"][f"{item.item_code}{item.warehouse}"]
		except:
			item.store_return=0
		try:
			item.transfer_to_another=entries["transfer_to_another"][f"{item.item_code}{item.warehouse}"]
		except:
			item.transfer_to_another=0
		try:
			item.receipt_from_another=entries["receipt_from_another"][f"{item.item_code}{item.warehouse}"]
		except:
			item.receipt_from_another=0
		try:
			item.consumed=entries["consumed"][f"{item.item_code}{item.warehouse}"]
		except:
			item.consumed=0
		try:
			item.closing=op_close["closing"][f"{item.item_code}{item.warehouse}"]
		except:
			item.closing=0
	return all_items
