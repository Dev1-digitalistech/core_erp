from __future__ import unicode_literals
import frappe
import json
from frappe.model.naming import make_autoname

def validate(self,method):
    if self.to_email_account=="IT Support":
		self.ticket_type="IT Support"

	elif self.to_email_account=="BIZOM Support":
		self.ticket_type="BIZOM-Support"

	elif self.to_email_account=="Care":
		self.ticket_type="Customer Care"

	elif self.to_email_account == "ERP SUPPORT":
		self.ticket_type = "ERP SUPPORT"

def autoname(self):
	if self.to_email_account=="IT Support":
		self.name=make_autoname("ITST/22-23/.#####.")

	elif self.ticket_type=="IT Support":
		self.name = make_autoname("ITST/22-23/.#####.")

	elif self.to_email_account=="BIZOM Support":
		self.name=make_autoname("BST/22-23/.#####.")

	elif self.ticket_type=="BIZOM-Support":
		self.name = make_autoname("BST/22-23/.#####.")

	elif self.to_email_account=="Care":
		self.name=make_autoname("CCT/22-23/.#####.")

	elif self.ticket_type=="Customer Care":
		self.name=make_autoname("CCT/22-23/.#####.")

	elif self.ticket_type=="CMS(Change Management System)":
		self.name=make_autoname("CMS/22-23/.#####.")

	elif self.ticket_type=="ERP SUPPORT":
		self.name=make_autoname("ERP/22-23/.#####.")

	elif self.to_email_account=="ERP SUPPORT":
		self.name=make_autoname("ERP/22-23/.#####.")

# assignment permission
def get_permission_query_condition(user):
        if "Support Manager" in frappe.get_roles(user):
                return None
        else:
                return """tabIssue.owner={user} or
                        (tabIssue.name in (select i.name from `tabIssue` i ,tabToDo td where td.reference_type="Issue" and td.owner={user} and
                        td.reference_name=i.name and td.status="Open"))""".format(user=frappe.db.escape(user))

