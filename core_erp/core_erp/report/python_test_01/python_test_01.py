
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters={}
	columns, data = [], []
	columns=get_columns()
	data=get_data(filters)
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
		{"label": _("Supplier Address"), "fieldname": "address_display", "fieldtype": "Data", "width": 120},
		{"label": _("Supplier GST"), "fieldname": "supplier_gstin", "fieldtype": "Data",  "width": 100},
		{"label": _("Place Of Supply"), "fieldname": "place_of_supply", "fieldtype": "Data", "width": 100},
		{"label": _("State Code"), "fieldname":"state_code", "fieldtype":"Data", "width":100},
		{"label": _("Bill No"), "fieldname": "bill_no", "fieldtype": "Data", "width": 100, },
		{"label": _("Bill Date"), "fieldname": "bill_date", "fieldtype": "Date", "width": 110},
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link","options":"Item", "width": 100},
		{"label": _("Item Name"), "fieldname": "item_name","fieldtype": "Data", "width": 100},
		{"label": _("Item Group"), "fieldname":"item_group","fieldtype":"Data", "width":100},
		{"label": _("Item Category"), "fieldname": "item_category", "fieldtype":"Data", "width":100},
		{"label": _("HSN Code"), "fieldname": "gst_hsn_code", "fieldtype": "Data","width": 100,},
		{"label": _("Rate"), "fieldname": "rate_s", "fieldtype": "Float","width": 100 },
		{"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Link","options":"UOM", "width": 100},
		{"label": _("Billing Qty"), "fieldname": "invoice_quantity", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Item Tax Template"), "fieldname": "item_tax_template", "fieldtype": "Link","options":"Item Tax Template", "width": 100},
		{"label": _("Amount"), "fieldname": "amt", "fieldtype":"Float", "width":100},
		{"label": _("CGST"), "fieldname": "cgst", "fieldtype": "Data", "width": 100},
		{"label":_("CGST Amount"),"fieldname":"cgst_amount","fieldtype":"Currency","width":100},
		{"label":_("SGST"),"fieldname":"sgst","fieldtype":"Data","width":100},
		{"label":_("SGST Amount"),"fieldname":"sgst_amount","fieldtype":"Currency","width":100},
		{"label":_("IGST"),"fieldname":"igst","fieldtype":"Data","width":100},
		{"label":_("IGST Amount"),"fieldname":"igst_amount","fieldtype":"Currency","width":100},
		{"label":_("TCS Receivable"),"fieldname":"tcs","fieldtype":"Currency","width":100},
		{"label":_("TDS Receivable"),"fieldname":"tds","fieldtype":"Currency","width":100},
		{"label":_("Gross Amount"),"fieldname":"gross_amount","fieldtype":"Currency","width":100},
		{"label":_("Grand Total Amount"),"fieldname":"grand_total","fieldtype":"Currency","width":100}
	]
def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and posting_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += " and posting_date <= '%s'" % filters["to_date"]

	if filters.get("company"):
		conditions += " and company <= '%s'" % filters["company"]

	return conditions

def get_data(filters):
	conditions = get_conditions(filters)
	all_data=frappe.db.sql('''select pi.name,pi.posting_date as posting_date,pi.purchase_order,po.transaction_date as transaction_date,pi.mrn_number,pi.mrn_date,
	pi.supplier,pi.address_display,pi.supplier_gstin,ads.gst_state as place_of_supply,ads.gst_state_number as state_code,pi.bill_no,pi.taxes_and_charges_added,
	pi.bill_date,pit.item_code,pit.item_name,item.item_group,item.category as item_category, pit.gst_hsn_code,pit.rate_s,item.stock_uom,pit.invoice_quantity,
	pit.item_tax_template,pit.amount_s as amt,iit.tax_print,pit.amount_s*iit.tax_print as amount,pi.grand_total
	from `tabPurchase Invoice` pi
		left join `tabPurchase Invoice Item` pit on pit.parent=pi.name
		left join `tabItem Tax Template` iit on  pit.item_tax_template=iit.name
		left join `tabPurchase Order` po on pi.purchase_order=po.name
		left join `tabItem` item on pit.item_name=item.item_name
		left join `tabAddress` ads on pi.supplier_address=ads.name
		where pi.docstatus=1 and pi.is_return=0 and pit.name is not NULL ''',as_dict=1)
	items_count=frappe.db.sql("""select pi.name, count(pi.name) as count from `tabPurchase Invoice` pi, `tabPurchase Invoice Item` pc
		where pc.parent = pi.name and pi.is_return = 0 group by pi.name""",as_dict=1)
	temp =  frappe.db.sql('''select pi.name,pi.taxes_and_charges_added ,tc.account_head,tc.tax_amount from `tabPurchase Invoice` pi,
		`tabPurchase Taxes and Charges` tc where tc.parent=pi.name and tc.account_head like "TCS%"and tc.account_head like "TDS%" and pi.is_return = 0''',as_dict=1)
	ignore_list = []
	temp_dict = {}
	for i in temp:
		temp_dict[i['name']]= i['tax_amount']
		if i['taxes_and_charges_added']==i['tax_amount']:
			ignore_list.append(i['name'])
	if all_data:
		for data in all_data:
			if data.item_tax_template:
				if data['name'] in temp_dict:
					data['tcs'] = temp_dict[data['name']]/[x.count for x in items_count if x.name == data['name']][0]
				if data['taxes_and_charges_added'] and data['name'] not in ignore_list:
					if "Outstate" in data.item_tax_template:
						data['igst']=data['tax_print']
						data['igst_amount']=data['amount']/100
						data['gross_amount']=data['igst_amount']+data['amt']
					elif "Instate" in data.item_tax_template:
						data['cgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"
						data['cgst_amount']=((data['amount']/100)/2)
						data['sgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"
						data['sgst_amount']=((data['amount']/100)/2)
						data['gross_amount']=data['amt']+data['sgst_amount'] + data['cgst_amount']
				else:
					data['gross_amount'] = data['taxes_and_charges_added']
	extra = frappe.db.sql("""select pi.name,pi.posting_date as posting_date,pit.purchase_order,po.transaction_date as transaction_date,pi.mrn_number,pi.mrn_date,
		pi.supplier,pi.address_display,pi.supplier_gstin,pi.bill_no,pi.bill_date,pi.taxes_and_charges_added ,pit.item_code,
		pit.item_name,pit.gst_hsn_code,pit.rate,pit.stock_uom,pit.qty,pit.item_tax_template,pit.amount as amount,pi.grand_total
		from `tabPurchase Invoice` pi, `tabPurchase Order` po,`tabPurchase Invoice Item` pit
			where pi.docstatus=1 and pi.is_return=0 and pit.purchase_order=po.name and pit.parent=pi.name and pit.item_tax_template is NULL %s"""%conditions,as_dict=1)
	for e in extra:
		if e['name'] in temp_dict:
			e['tcs'] = temp_dict[e['name']]/[x.count for x in items_count if x.name == e['name']][0]
			e['tds'] = temp_dict[e['name']]/[x.count for x in items_count if x.name == e['name']][0]
		e['gross_amount']=e['amount']
	all_data=all_data+extra

	return all_data
