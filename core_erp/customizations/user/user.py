from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from frappe.utils import now
from datetime import datetime



@frappe.whitelist()
def auto_disable_users():
    frappe.log_error("scheduler running", "scheduler running")
    subject = frappe.db.get_all('User Connection', ["name",'last_working_day'])
    for i in subject:
        if i['last_working_day']<=(datetime.now()).date():
            print(i)
            try:
                if frappe.get_doc("User",i["name"]):
                    
                    frappe.db.set_value('User', i["name"] , 'enabled', 0)
                    frappe.db.set_value('User', i["name"] , 'enabled', False)
            except:
                pass



# def auto_disable_users():
#     frappe.log_error("scheduler running", "scheduler running")
#     subjects = frappe.get_all('User Connection', filters={"last_working_day": ("<", datetime.now().date())}, fields=["name"])

#     for subject in subjects:
#         try:
#             user = frappe.get_doc("User", subject["name"])
#             user.enabled = 0
#             user.save()
#             frappe.db.set_value('User', subject["name"], 'enabled', False)
#             print(f"User {subject['name']} has been deactivated.")
#         except Exception as e:
#             print(f"Failed to deactivate User {subject['name']}: {str(e)}")

