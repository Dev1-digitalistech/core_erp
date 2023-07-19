import frappe

def validate(self,method=None):
	# frappe.msgprint(self.supplier_bill_no)
	if not self.gate_entry_type == "Sales Inward":

		if frappe.db.exists("Gate Entry", {"supplier":self.supplier, "supplier_bill_no":self.supplier_bill_no, 'docstatus':1}):
			
			frappe.throw('Same bill with the Same Supplier Already Exist in Record.')

