# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt, cint, getdate, now, date_diff
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition

from six import iteritems

def execute(filters=None):
	if not filters: filters = {}

	from_date = filters.get('from_date')
	to_date = filters.get('to_date')

	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	columns = get_columns(filters)
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	# if no stock ledger entry found return
	if not sle:
		return columns, []

	iwb_map = get_item_map(filters, sle)
	item_map = get_item_details(items, sle, filters)

	data = []
	conversion_factors = {}

	_func = lambda x: x[1]


	for (company, item) in sorted(iwb_map):
		if item_map.get(item):
			qty_dict = iwb_map[(company, item)]

			report_data = {
				'currency': company_currency,
				'item_code': item,
				'company': company
			}
			report_data.update(item_map[item])
			report_data.update(qty_dict)
			
			data.append(report_data)

	return columns, data

def get_columns(filters):
	"""return columns"""
	columns = [
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
		{"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Opening Value"), "fieldname": "opening_val", "fieldtype": "Currency", "width": 110, "options": "currency"},
		{"label": _("Purchase Qty"), "fieldname": "pur_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Purchase Value"), "fieldname": "pur_amt", "fieldtype": "Currency", "width": 110, "options": "currency"},
		{"label": _("Consumed Qty"), "fieldname": "cons_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Consumed Value"), "fieldname": "cons_amt", "fieldtype": "Currency", "width": 100, "options": "currency"},
		{"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Balance Value"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 100, "options": "currency"},
		{"label": _("Valuation Rate"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 90, "convertible": "rate", "options": "currency"},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 100}
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("company"):
		conditions += " and sle.company = %s" % frappe.db.escape(filters.get("company"))

	return conditions

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join([frappe.db.escape(i, percent=False) for i in items]))

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
			sle.item_code as name, sle.voucher_no
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty""" % #nosec
		(item_conditions_sql, conditions), as_dict=1)

def get_item_map(filters, sle):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	for d in sle:
		key = (d.company, d.item_code)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0,
				"pur_qty": 0.0,
				"pur_amt": 0.0,
				"cons_qty": 0.0
			})

		qty_dict = iwb_map[(d.company, d.item_code)]

		
		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)
		if d.posting_date < from_date:
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if flt(qty_diff, float_precision) >= 0:
				# qty_dict.in_qty += qty_diff
				# qty_dict.in_val += value_diff
				if d.voucher_type == 'Purchase Receipt':
					qty_dict.pur_qty += qty_diff
					qty_dict.pur_amt += value_diff
			else:
				# qty_dict.out_qty += abs(qty_diff)
				# qty_dict.out_val += abs(value_diff)
				if d.voucher_type == 'Purchase Receipt':
					qty_dict.pur_qty += qty_diff
					qty_dict.pur_amt += value_diff

		qty_dict.val_rate = d.valuation_rate
		
		qty_dict.bal_val += value_diff
		qty_dict.cons_qty = qty_dict.opening_qty + qty_dict.pur_qty - qty_dict.bal_qty
		qty_dict.cons_amt = qty_dict.opening_val + qty_dict.pur_amt - qty_dict.bal_val
		qty_dict.bal_qty += qty_diff
		final_qty = flt(qty_dict.bal_qty,2)
		final_val_rate = flt(d.valuation_rate,2)
		qty_dict.bal_val = final_qty * final_val_rate

	iwb_map = filter_items_with_no_transactions(iwb_map, float_precision)

	return iwb_map

def filter_items_with_no_transactions(iwb_map, float_precision):
	for (company, item) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item)]

		no_transactions = True
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			iwb_map.pop((company, item))

	return iwb_map

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))

	if not items:
		return item_details

	cf_field = cf_join = ""

	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom %s
		from
			`tabItem` item
			%s
		where
			item.name in (%s)
	""" % (cf_field, cf_join, ','.join(['%s'] *len(items))), items, as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details