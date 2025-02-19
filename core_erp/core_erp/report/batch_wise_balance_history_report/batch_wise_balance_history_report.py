# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate
from frappe.utils import *

def execute(filters=None):
	if not filters: filters = {}
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision)
	data = []
	for item in sorted(iwb_map):
		for wh in sorted(iwb_map[item]):
			for batch in sorted(iwb_map[item][wh]):
				qty_dict = iwb_map[item][wh][batch]
                            #   posting_date = frappe.db.sql("""Select * from `tabBatch` where name = %s""",(batch), as_dict=1)
                            #   frappe.msgprint(str(posting_date))
				mfg_date = frappe.db.get_value("Batch",batch,"manufacturing_date")
				expiry_date = frappe.db.get_value("Batch",batch,"expiry_date")
				ref_lot_number=frappe.db.get_value("Batch",batch,"ref_lot_number")
				reference = frappe.db.get_value("Batch",batch,"reference_doctype")
				reference_name = frappe.db.get_value("Batch",batch,"reference_name")

				cur_date=frappe.utils.nowdate()
				days_left=date_diff(expiry_date,cur_date)
				bucket = ""
				if (days_left < 0):
					bucket="<0 Days"
				elif(days_left <= 15):
					bucket="0-15 Days"
				elif(days_left <= 30):
					bucket="16-30 Days"
				elif(days_left <= 45):
					bucket="30-45 Days"
				else:
					bucket=">45 Days"

				# frappe.msgprint(days_left)

				if ((qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty) and qty_dict.bal_qty > 0):
					# data.append([item, item_map[item]["item_name"], item_map[item]["description"], wh, batch,qty_dict.vendor_batch_no, mfg_date,expiry_date,ref_lot_number,
                    #                             flt(qty_dict.opening_qty, float_precision), flt(qty_dict.in_qty, float_precision),
                    #                             flt(qty_dict.out_qty, float_precision), flt(qty_dict.bal_qty, float_precision), reference,reference_name,
                    #                              item_map[item]["stock_uom"]
                    #                     ])
					data.append([item, item_map[item]["item_name"], item_map[item]["description"], wh, batch,qty_dict.vendor_batch_no, mfg_date,expiry_date, flt(qty_dict.bal_qty, float_precision),
                                                 item_map[item]["stock_uom"],days_left,bucket
                                        ])

	return columns, data



def execute(filters=None):
	if not filters: filters = {}

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

	
	data = []
#       frappe.msgprint(str(iwb_map))
	for item in sorted(iwb_map):
		for wh in sorted(iwb_map[item]):
			for batch in sorted(iwb_map[item][wh]):
				qty_dict = iwb_map[item][wh][batch]
                            #   posting_date = frappe.db.sql("""Select * from `tabBatch` where name = %s""",(batch), as_dict=1)
                            #   frappe.msgprint(str(posting_date))
				mfg_date = frappe.db.get_value("Batch",batch,"manufacturing_date")
				expiry_date = frappe.db.get_value("Batch",batch,"expiry_date")
				ref_lot_number=frappe.db.get_value("Batch",batch,"ref_lot_number")
				reference = frappe.db.get_value("Batch",batch,"reference_doctype")
				reference_name = frappe.db.get_value("Batch",batch,"reference_name")

				cur_date=frappe.utils.nowdate()
				days_left=date_diff(expiry_date,cur_date)
				bucket = ""
				if (days_left < 0):
					bucket="<0 Days"
				elif(days_left <= 15):
					bucket="0-15 Days"
				elif(days_left <= 30):
					bucket="16-30 Days"
				elif(days_left <= 45):
					bucket="30-45 Days"
				else:
					bucket=">45 Days"
				

				# frappe.msgprint(days_left)

				if ((qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty) and qty_dict.bal_qty > 0):
					# data.append([item, item_map[item]["item_name"], item_map[item]["description"], wh, batch,qty_dict.vendor_batch_no, mfg_date,expiry_date,ref_lot_number,
                    #                             flt(qty_dict.opening_qty, float_precision), flt(qty_dict.in_qty, float_precision),
                    #                             flt(qty_dict.out_qty, float_precision), flt(qty_dict.bal_qty, float_precision), reference,reference_name,
                    #                              item_map[item]["stock_uom"]
                    #                     ])
					data.append([item, item_map[item]["item_name"], item_map[item]["description"], wh, item_map[item]['mrp'], item_map[item]['shelf_life_in_days'], batch,qty_dict.vendor_batch_no, mfg_date,expiry_date, flt(qty_dict.bal_qty, float_precision),
                                                 item_map[item]["stock_uom"],days_left,bucket,qty_dict.valuation_rate
                                        ])

	return columns, data

def get_columns(filters):
	"""return columns based on filters"""

	columns = [_("Item") + ":Link/Item:100"] + [_("Item Name") + "::150"] + [_("Description") + "::150"] + \
        [_("Store/Stage Name") + ":Link/Warehouse:100"] + [_("MRP") + "::150"] + [_("Shelf Life In Days") + "::150"] + [_("Batch") + ":Link/Batch:100"] + [_("Vendor Batch No") + ":Data:100"] + [_("Manufacturing Date") + ":Date:100"] + [_("Expiry Date") + ":Date:100"]  + [_("Balance Qty") + ":Float:90"] + [_("UOM") + "::90"]+[_("Number Of Days Left") + "::90"]+[_("Bucket") + "::80"] + [_("Valuation Rate") + "::150"]


	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and posting_date <= '%s'" % filters["to_date"]
	else:
		frappe.throw(_("'To Date' is required"))

	for field in ["item_code", "warehouse", "batch_no", "company"]:
		if filters.get(field):
			conditions += " and sle.{0} = {1}".format(field, frappe.db.escape(filters.get(field)))

	return conditions

#get all details
def get_stock_ledger_entries(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
                select sle.item_code, sle.batch_no, sle.warehouse, sle.posting_date, sum(sle.actual_qty) as actual_qty, bat.vendor_batch_no, sle.valuation_rate
                from `tabStock Ledger Entry` sle left join `tabPurchase Receipt Item` bat on sle.voucher_detail_no=bat.name
                where sle.docstatus < 2 and ifnull(sle.batch_no, '') != '' %s
                group by sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse
                order by sle.item_code, sle.warehouse""" %
                conditions, as_dict=1)

def get_item_warehouse_batch_map(filters, float_precision):
	sle = get_stock_ledger_entries(filters)
	iwb_map = {}

	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])

	for d in sle:
		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {})\
			.setdefault(d.batch_no, frappe._dict({
                                "opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0, "vendor_batch_no": d.vendor_batch_no, "valuation_rate":d.valuation_rate
                        }))
		qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
		if d.posting_date < from_date:
			qty_dict.opening_qty = flt(qty_dict.opening_qty, float_precision) \
                                + flt(d.actual_qty, float_precision)
		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if flt(d.actual_qty) > 0:
				qty_dict.in_qty = flt(qty_dict.in_qty, float_precision) + flt(d.actual_qty, float_precision)
			else:
				qty_dict.out_qty = flt(qty_dict.out_qty, float_precision) \
                                        + abs(flt(d.actual_qty, float_precision))

		qty_dict.bal_qty = flt(qty_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

	return iwb_map

def get_item_details(filters):
	item_map = {}
	for d in frappe.db.sql("select name, item_name, mrp, shelf_life_in_days, description, stock_uom from tabItem", as_dict=1):
		item_map.setdefault(d.name, d)

	return item_map
