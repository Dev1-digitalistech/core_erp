# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_data()
	return columns, data
def get_columns():
	return [
                {"label": _("Purchase Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
                {"label": _("Purchase Invoice Date"), "fieldname": "posting_date","fieldtype":"Date", "width": 100},
                {"label": _("Purchase Order"), "fieldname": "purchase_order","fieldtype":"Link","options":"Purchase Order", "width": 200},
                {"label": _("Purchase Order Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
		{"label":_("MRN Number"),"fieldname":"mrn_number","fieldtype":"Link","options":"Purchase Receipt","width":100},
		{"label":_("MRN Date"),"fieldname":"mrn_date","fieldtype":"Date","width":100},
                {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
                {"label": _("Supplier Address"), "fieldname": "shipping_address_display", "fieldtype": "Data", "width": 120},
                {"label": _("Supplier GST"), "fieldname": "supplier_gstin", "fieldtype": "Data",  "width": 100},
                {"label": _("Place Of Supply"), "fieldname": "place_of_supply", "fieldtype": "Data", "width": 100},
                {"label": _("Bill No"), "fieldname": "bill_no", "fieldtype": "Data", "width": 100, },
                {"label": _("Bill Date"), "fieldname": "bill_date", "fieldtype": "Date", "width": 110,},
                {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link","options":"Item", "width": 100},
                {"label": _("Item Name"), "fieldname": "item_name","fieldtype": "Data", "width": 100},
                {"label": _("HSN Code"), "fieldname": "gst_hsn_code", "fieldtype": "Data","width": 100,},
                {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float","width": 100, },
                {"label": _("UOM"), "fieldname": "weight_uom", "fieldtype": "Link","options":"UOM", "width": 100},
                {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("Item Tax Template"), "fieldname": "item_tax_template", "fieldtype": "Link","options":"Item Tax Template", "width": 100},
                {"label": _("CGST"), "fieldname": "cgst", "fieldtype": "Data", "width": 100},
                {"label":_("CGST Amount"),"fieldname":"cgst_amount","fieldtype":"Currency","width":100},
                {"label":_("SGST"),"fieldname":"sgst","fieldtype":"Data","width":100},
                {"label":_("SGST Amount"),"fieldname":"sgst_amount","fieldtype":"Currency","width":100},
		{"label":_("IGST"),"fieldname":"igst","fieldtype":"Data","width":100},
                {"label":_("IGST Amount"),"fieldname":"igst_amount","fieldtype":"Currency","width":100},
		{"label":_("Gross Amount"),"fieldname":"gross_amount","fieldtype":"Currency","width":100}
        ]

def get_data():
	all_data=frappe.db.sql('''select pi.name,pi.posting_date as posting_date,pi.purchase_order,po.transaction_date as transaction_date,pi.mrn_number,pi.mrn_date,
	pi.supplier,pi.shipping_address_display,pi.supplier_gstin,pi.place_of_supply,pi.bill_no,pi.taxes_and_charges_added,
	pi.bill_date,pit.item_code,pit.item_name,pit.gst_hsn_code,pit.rate,pit.weight_uom,pit.qty,pit.item_tax_template,iit.tax_print,pit.amount*iit.tax_print as amount
	from `tabPurchase Invoice` pi,`tabPurchase Order` po,`tabPurchase Invoice Item` pit,`tabItem Tax Template` iit
	where pi.docstatus=1 and pi.is_return=0 and pi.purchase_order=po.name and pit.parent=pi.name and pit.item_tax_template=iit.name''',as_dict=1)
	if all_data:
		for data in all_data:
			if data['taxes_and_charges_added']:
				if "Outstate" in data.item_tax_template:
					data['igst']=data['tax_print']
					data['igst_amount']=data['amount']/100
					data['gross_amount']=data['igst_amount']
				elif "Instate" in data.item_tax_template:
					data['cgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"
					data['cgst_amount']=((data['amount']/100)/2)
					data['sgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"
					data['sgst_amount']=((data['amount']/100) /2)
					data['gross_amount']=data['sgst_amount'] + data['cgst_amount']
	return all_data

