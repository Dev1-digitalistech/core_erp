# from __future__ import unicode_literals
# import frappe
# import json
# from frappe.model.naming import make_autoname


# def before_insert(self, method=None):
#     if(self.reference_doctype == "Issue"):
#         frappe.db.set_value('Issue', self.reference_name, {
#             'to_email_account': self.email_account
#         })
#         if self.email_account=='extcrm':
#             frappe.db.set_value('Issue', self.reference_name, {
#             'ticket_type': "IT Support"
#         })
#         frappe.db.set_value('Issue', self.reference_name, {
#             'name': make_autoname("ITST/23-24/.#####.")
#         })
