import frappe

def validate(self,method=None):
    frappe.msgprint(self.supplier_bill_no)
    # frappe.throw('ruk jaa')
    if frappe.db.exists("Gate Entry", {"supplier":self.supplier, "supplier_bill_no":self.supplier_bill_no}):
        frappe.throw('Same bill with the Same Supllier Already Exist in Record.')

