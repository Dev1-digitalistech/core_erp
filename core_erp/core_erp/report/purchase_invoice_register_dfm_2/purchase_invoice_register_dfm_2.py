# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_columns(filters)
	data=get_data(filters)
	return columns, data
def get_columns(filters):
	return [
                
                {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 140},
                {"label": _("PO Type"), "fieldname": "po_type", "fieldtype": "Link", "options": "PO Type", "width": 120},
                {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 140},
                {"label": _("Purchase Order"), "fieldname": "purchase_order","fieldtype":"Link","options":"Purchase Order", "width": 200},
                {"label": _("PO Created On"), "fieldname": "po_creation","fieldtype":"Date", "width": 150},
                {"label": _("PO Status"), "fieldname": "state","fieldtype":"Data", "width": 120},
                {"label": _("PO Item Code"), "fieldname": "po_item_code", "fieldtype": "Link","options":"Item", "width": 100},
                {"label": _("PO Item Name"), "fieldname": "po_item_name","fieldtype": "Data", "width": 100},
                {"label": _("PO Qty"), "fieldname": "po_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("PO UOM"), "fieldname": "uom", "fieldtype": "Link","options":"UOM", "width": 85},
                {"label": _("PO Rate"), "fieldname": "po_rate", "fieldtype": "Float","width": 100, },
                {"label": _("PO Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
                {"label": _("PO Approved By Manager Procurement"), "fieldname": "","fieldtype":"Data", "width": 150},
                {"label": _("PO Approved By Controller"), "fieldname": "","fieldtype":"Data", "width": 150},
                {"label": _("PO Approved By CPO"), "fieldname": "","fieldtype":"Data", "width": 150},
                {"label": _("PO Approved By IT-Pre Approval"), "fieldname": "","fieldtype":"Data", "width": 150},
                {"label": _("PO Approved By Purchase Manager"), "fieldname": "","fieldtype":"Data", "width": 150},
	             	{"label":_("MRN Number"),"fieldname":"mrn_number","fieldtype":"Link","options":"Purchase Receipt","width":100},
                {"label": _("MRN Status"), "fieldname": "pr_workflow_state","fieldtype":"Data", "width": 150},
		            {"label":_("MRN Date"),"fieldname":"mrn_date","fieldtype":"Date","width":100},
                {"label":_("MRN Created On"),"fieldname":"mrn_create","fieldtype":"Date","width":100},
                {"label": _("MRN Approval Date"), "fieldname": " ","fieldtype":"Date", "width": 150},
                {"label": _("MRN Rcvd Qty"), "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
                {"label": _("MRN Acc Qty"), "fieldname": "mrn_qty", "fieldtype": "Float", "width": 100},
                {"label": _("MRN UOM"), "fieldname": "mrn_uom", "fieldtype": "Link","options":"UOM", "width": 100},
                {"label": _("MRN Rate"), "fieldname": "mrn_rate", "fieldtype": "Float","width": 100},
                {"label": _("Purchase Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
                {"label": _("PI Created On"), "fieldname": "creation","fieldtype":"Date", "width": 150},
                {"label": _("PI Approval Date"), "fieldname": " ","fieldtype":"Date", "width": 150},
                {"label": _("PI Date"), "fieldname": "posting_date","fieldtype":"Date", "width": 100},
                {"label": _("PI Item Code"), "fieldname": "item_code", "fieldtype": "Link","options":"Item", "width": 100},
                {"label": _("PI Item Name"), "fieldname": "item_name","fieldtype": "Data", "width": 100},
                {"label": _("PI Item Group"), "fieldname": "item_group","fieldtype": "Data", "width": 100},
                {"label": _("PI Rate"), "fieldname": "rate", "fieldtype": "Float","width": 100, },
                {"label": _("PI UOM"), "fieldname": "weight_uom", "fieldtype": "Link","options":"UOM", "width": 100},
                {"label": _("PI Bill Qty"), "fieldname": "invoice_quantity", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("PI Actual Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("PI Rejected Qty"), "fieldname": "rejected_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("PI Short Qty"), "fieldname": "short_quantity", "fieldtype": "Float", "width": 100, "convertible": "qty"},
                {"label": _("PI Amount"), "fieldname": "amt", "fieldtype": "Currency", "width": 100},
                {"label": _("Payment Entry No"), "fieldname": "pe_name", "fieldtype": "Data", "width": 100},
                {"label": _("PE Date"), "fieldname": "pe_date", "fieldtype": "Date", "width": 100},              
        ]

def get_data(filters):
  cond=get_conditions(filters)
  all_data=frappe.db.sql('''select pi.name,po.company,po.po_type,po.supplier,po.creation as po_creation,pi.creation as creation,po.workflow_state as state,poi.item_code as po_item_code,poi.item_name as po_item_name,poi.uom,poi.po_qty,poi.rate as po_rate,pi.posting_date as posting_date,pi.purchase_order,po.transaction_date as transaction_date, pi.mrn_number,pi.mrn_date,pr.creation as mrn_create,pr.workflow_state as pr_workflow_state,pri.qty as mrn_qty,pri.received_qty,pri.rate as mrn_rate,pri.uom as mrn_uom,pit.weight_uom,pit.amount as amt,i.item_group,pe.name as pe_name,pe.posting_date as pe_date, pit.item_code, pit.item_name, i.item_group,pit.rate,pit.invoice_quantity,pit.qty,pit.rejected_qty,pit.short_quantity, iit.tax_print,pit.amount*iit.tax_print as amount
  from `tabPurchase Invoice` pi,`tabPurchase Order` po,`tabPurchase Order Item` poi,`tabPurchase Invoice Item` pit,`tabItem Tax Template` iit, `tabItem` i, `tabAddress` a,`tabPurchase Receipt` pr , `tabPurchase Receipt Item` pri, `tabPayment Entry` pe, `tabPayment Entry Reference` per
	where pi.docstatus=1 and pi.is_return=0 and pi.purchase_order=po.name and poi.parent=po.name and pit.parent=pi.name and pit.item_tax_template=iit.name and pit.item_code=i.name and pi.supplier_address=a.name and pi.mrn_number=pr.name and per.parent=pe.name and per.reference_name =pi.name and pri.parent=pr.name %s'''%cond,as_dict=1)
  return all_data
 
def get_conditions(filters):
  conditions = ""
  if filters.get("company"):
    conditions += "and po.company=%s"%frappe.db.escape(filters.get("company"))
  return conditions


