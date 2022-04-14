import frappe
import json

@frappe.whitelist()
def create_quality_inspection(self):
	self = frappe.get_doc("Purchase Receipt",self)
	for d in self.items:
		frappe.msgprint(str(d.item_code))
		qc = frappe.db.sql("""select name from `tabQuality Inspection` where item_code = %s and reference_name = %s and row_name = %s""",(d.item_code,self.name,d.name))
		if frappe.db.get_value("Item", d.item_code, "inspection_required_before_purchase") and not qc and not self.is_return:
			qi = frappe.new_doc('Quality Inspection')
			qi.inspection_type = "Incoming"
			qi.item_code = d.item_code
			qi.item_name = d.item_name
			qi.supplier = self.supplier
			qi.supplier_invoice_no = self.supplier_bill_no
			qi.supplier_invoice_date = self.date
			qi.inspected_by = frappe.session.user
			qi.reference_type = self.doctype
			qi.company = self.company
			qi.mrn_type = frappe.db.get_value("Purchase Order",d.purchase_order,"po_type")
			qi.abbr = self.abbr
			qi.reference_name = self.name
			qi.acc_qty = d.qty
			qi.row_name = d.name
			qi.sample_size = 0
			qi.insert()
			frappe.msgprint("Quality Inspection Created for " + str(d.item_code))

