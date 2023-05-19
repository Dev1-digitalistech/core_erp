import frappe

def before_insert(self, method=None):
    if(self.reference_doctype == "Issue"): 
        frappe.db.set_value('Issue', self.reference_name, {
            'to_email_account': self.email_account
        })