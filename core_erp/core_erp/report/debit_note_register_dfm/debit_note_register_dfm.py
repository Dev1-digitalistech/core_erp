# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors

# For license information, please see license.txt



from __future__ import unicode_literals

import frappe

from frappe import _

from frappe.utils import getdate



def execute(filters=None):

        if not filters:

                filters = {}

        if filters.from_date>filters.to_date:

                frappe.throw(_("From Date Must Be Before To Date "))

        columns, data=[],[]

        columns=get_columns()

        data=get_data(filters)

        return columns, data

def get_columns():

        return [

                {"label": _("Debit Note"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},

                {"label": _("Debit Note Date"), "fieldname": "posting_date","fieldtype":"Date", "width": 100},

                {"label": _("Purchase Order"), "fieldname": "purchase_order","fieldtype":"Link","options":"Purchase Order", "width": 200},

                {"label": _("Purchase Order Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},

                {"label": _("MRN No"), "fieldname": "mrn_number", "fieldtype": "Link","options":"Purchase Receipt", "width": 100},

                {"label": _("MRN Date"), "fieldname": "mrn_date", "fieldtype": "Date", "width": 100},

                {"label": _("Company"), "fieldname": "company", "fieldtype": "Data", "width": 100},

                {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},

                {"label": _("Supplier Address"), "fieldname": "address_display", "fieldtype": "Data", "width": 120},

                {"label": _("Supplier GST"), "fieldname": "supplier_gstin", "fieldtype": "Data",  "width": 100},

                {"label": _("Place Of Supply"), "fieldname": "place_of_supply", "fieldtype": "Data", "width": 100},

                {"label": _("State Code"), "fieldname":"state_code", "fieldtype":"Data", "width":100},

                {"label": _("Bill No"), "fieldname": "bill_no", "fieldtype": "Data", "width": 100, },

                {"label": _("Bill Date"), "fieldname": "bill_date", "fieldtype": "Date", "width": 110,},

                {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link","options":"Item", "width": 100},

                {"label": _("Item Name"), "fieldname": "item_name","fieldtype": "Data", "width": 100},

                {"label": _("Item Group"), "fieldname": "item_group","fieldtype":"Data","width":100},

                {"label": _("Item Category"),"fieldname":"category","fieldtype":"Data","width":100},

                {"label": _("HSN Code"), "fieldname": "gst_hsn_code", "fieldtype": "Data","width": 100},

                {"label": _("Rate"), "fieldname": "rate_s", "fieldtype": "Float","width": 100, },

                {"label": _("UOM"), "fieldname": "weight_uom", "fieldtype": "Link","options":"UOM", "width": 100},

                {"label": _("Billing Qty"), "fieldname": "invoice_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},

                {"label": _("Rejected Qty"), "fieldname": "rej_qty", "fieldtype": "Float", "width": 100, "convertible": "rejected_qty"},

                {"label": _("Received Qty"), "fieldname": "recv_qty", "fieldtype": "Float", "width": 100, "convertible": "received_qty"},

                {"label": _("Short Qty"), "fieldname": "short_qty", "fieldtype": "Float", "width": 100, "convertible": "short_quantity"},

                {"label": _("Item Tax Template"), "fieldname": "item_tax_template", "fieldtype": "Link","options":"Item Tax Template", "width": 100},

                {"label": _("Amount"), "fieldname": "amt", "fieldtype":"Float", "width":100},

                {"label": _("IGST"), "fieldname": "igst", "fieldtype": "Data", "width": 100},

                {"label": _("IGST Amount"),"fieldname":"igst_amount","fieldtype":"Currency","width":100},

                {"label": _("CGST"), "fieldname": "cgst", "fieldtype": "Data", "width": 100},

                {"label": _("CGST Amount"),"fieldname":"cgst_amount","fieldtype":"Currency","width":100},

                {"label": _("SGST"),"fieldname":"sgst","fieldtype":"Data","width":100},

                {"label": _("SGST Amount"),"fieldname":"sgst_amount","fieldtype":"Currency","width":100},

                {"label":_("TCS Receivable"),"fieldname":"tcs","fieldtype":"Currency","width":100},

                {"label":_("TDS Receivable"),"fieldname":"tds","fieldtype":"Currency","width":100},

                {"label": _("Gross Amount"),"fieldname":"gross_amt","fieldtype":"Currency","width":200},

                {"label":_("Grand Total Amount"),"fieldname":"round_total","fieldtype":"Currency","width":200}

        ]



def get_data(filters):

        conditions=""

        if filters:

                if filters.get('company'):

                        conditions= conditions + "and pi.company= %s"%(frappe.db.escape(filters.get("company")))

                if filters.get('to_date'):

                        if filters.get('from_date'):

                                conditions= conditions + "and pi.posting_date between %s and %s"%(frappe.db.escape(filters.get("from_date")),frappe.db.escape(filters.get("to_date")))

        all_data=frappe.db.sql('''select pi.name,pi.posting_date as posting_date,pi.purchase_order,po.transaction_date as transaction_date,pi.mrn_number,pi.mrn_date,pi.company,pi.supplier,pi.address_display,pi.supplier_gstin,ads.gst_state as place_of_supply,ads.gst_state_number as state_code,pi.bill_no,

        pi.bill_date,pit.item_code,pit.item_name,item.item_group,item.category,pit.gst_hsn_code,pit.rate_s,item.stock_uom as weight_uom,pit.invoice_quantity as invoice_qty,

        pit.rejected_qty as rej_qty,pit.received_qty as recv_qty,pit.short_quantity as short_qty,pit.item_tax_template,pit.amount_s as amt,iit.tax_print,

        pit.amount_s*iit.tax_print as amount, pi.rounded_total as round_total

        from `tabPurchase Invoice` pi

                left join `tabPurchase Invoice Item` pit on pit.parent=pi.name

                left join `tabItem Tax Template` iit on pit.item_tax_template=iit.name

                left join `tabPurchase Order` po on pi.purchase_order=po.name

                left join `tabItem` item on pit.item_name=item.item_name

                left join `tabAddress` ads on  pi.supplier_address=ads.name

                where pi.docstatus=1 and pi.is_return=1 %s'''%conditions,as_dict=1)

        temp =  frappe.db.sql('''select pi.name,pi.taxes_and_charges_added ,tc.account_head,tc.tax_amount from `tabPurchase Invoice` pi,`tabPurchase Taxes and Charges` tc

                where tc.parent=pi.name and tc.account_head like "TCS%" and tc.account_head like "TDS%" and pi.is_return = 1''',as_dict=1)

        ignore_list = []

        temp_dict = {}

        for i in temp:

                temp_dict[i['name']]= i['tax_amount']

                if i['taxes_and_charges_added']==i['tax_amount']:

                        ignore_list.append(i['name'])

        if all_data:

                for data in all_data:

                        if data["amt"]<0:

                                data["amt"]=data["amt"]*-1

                        else:

                                data["amt"]=data["amt"]

                        if data.item_tax_template:

                                if data['name'] in temp_dict:

                                        data['tcs'] = temp_dict[data['name']]

                                        data['tds'] = temp_dict[data['name']]

                        if data['name'] not in ignore_list:

                                if data.item_tax_template:

                                        if "Outstate" in data.item_tax_template:

                                                data['igst']=data['tax_print']

                                                data['igst_amount']=data['amount']/100

                                                if data['igst_amount']<0:

                                                        data['igst_amount']=data['igst_amount']*-1

                                                else:

                                                        data['igst_amount']=data['igst_amount']
#                                                        data['igst_amount'] = 0

                                                data['gross_amt']=data["amt"]+data['igst_amount']

                                                if data['gross_amt']<0:

                                                        data['gross_amt']=data['gross_amt']*-1

                                                else:

                                                        data['gross_amt']=data['gross_amt']

                                        elif "Instate" in data.item_tax_template:

                                                data['cgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"

                                                data['cgst_amount']=((data['amount']/100)/2)

                                                if data['cgst_amount']<0:

                                                        data['cgst_amount']=data['cgst_amount']*-1

                                                else:

                                                        data['cgst_amount']=data['cgst_amount']

                                                data['sgst']=str(int(data['tax_print'].translate({ord('%'): None}))/2)+"%"

                                                data['sgst_amount']=((data['amount']/100)/2)

                                                if data['sgst_amount']<0:

                                                        data['sgst_amount']=data["sgst_amount"]*-1

                                                else:

                                                        data['sgst_amount']=data["sgst_amount"]

                                                data['gross_amt']=data["amt"]+data['sgst_amount']+data['cgst_amount']

                                                if data['gross_amt']<0:

                                                        data['gross_amt']=data['gross_amt']*-1

                                                else:

                                                        data['gross_amt']=data['gross_amt']



                        else:

                                data['gross_amount'] = data['taxes_and_charges_added']

                        if data["invoice_qty"]<0:

                                data["invoice_qty"]=data["invoice_qty"]*-1

                        else:

                                data["invoice_qty"]=data["invoice_qty"]

                        if data["rej_qty"]<0:

                                data["rej_qty"]=data["rej_qty"]*-1

                        else:

                                data["rej_qty"]=data["rej_qty"]

                        if data["recv_qty"]<0:

                                data["recv_qty"]=data["recv_qty"]*-1

                        else:

                                data["recv_qty"]=data["recv_qty"]

                        if data["short_qty"]<0:

                                data["short_qty"]=data["short_qty"]*-1

                        else:

                                data["short_qty"]=data["short_qty"]

                        if data["round_total"]<0:

                                data["round_total"]=data["round_total"]*-1

                        else:

                                data["round_total"]=data["round_total"]



        return all_data
