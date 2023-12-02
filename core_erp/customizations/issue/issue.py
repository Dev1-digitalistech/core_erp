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
	
	elif self.to_email_account == "extcrm":
		self.ticket_type = "IT Support"

def autoname(self,method=None):
	if self.to_email_account=="IT Support":
		self.name=make_autoname("ITST/22-23/.#####")
	
	elif self.to_email_account=="extcrm":
		self.name=make_autoname("ITST/22-23/.#####")

	elif self.ticket_type=="ERP SUPPORT":
		self.name = make_autoname("ITST/22-23/.#####")

	elif self.to_email_account=="BIZOM-Support":
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

	elif self.ticket_type=="Distributor Feedback":
		self.name=make_autoname("DF/22-23/.#####.")

	elif self.to_email_account=="ERP SUPPORT":
		self.name=make_autoname("ERP/22-23/.#####.")

# assignment permission
# def get_permission_query_condition(user):
# 	if "Support Manager" in frappe.get_roles(user):
# 			return None
# 	else:
# 		return """ `tabIssue`._assign='{user}' """.format(user=user)
	# else:
	# 		return """tabIssue.owner={user} or
	# 				(tabIssue.name in (select i.name from `tabIssue` i ,tabToDo td where td.reference_type="Issue" and td.owner={user} and
	# 				td.reference_name=i.name and td.status="Open"))""".format(user=frappe.db.escape(user))

def permission_query(user):
    # frappe.msgprint(str(frappe.get_roles(user)))
	if "Support Manager" in frappe.get_roles(user):
		return None
	# if "Website Manager" in frappe.get_roles(user):
		# return """`tabLead`._assign is null""".format(user=user)
	# if "Sales Manager" in frappe.get_roles(user):
	else:
		return """`tabIssue`.to_email_account='{user}' or `tabIssue`.owner='{user}' or `tabIssue`._assign like '%{user}%'""".format(user=user)



def make_issue_from_communication(communication, ignore_communication_links=False):
	"""raise a issue from email"""

	doc = frappe.get_doc("Communication", communication)
	issue = frappe.get_doc(
		{
			"doctype": "Issue",
			"subject": doc.subject,
			"communication_medium": doc.communication_medium,
			"raised_by": doc.sender or "",
			"raised_by_phone": doc.phone_no or "",
			"email_account": doc.to_email_account
		}
	).insert(ignore_permissions=True)

	link_communication_to_document(doc, "Issue", issue.name, ignore_communication_links)

	return issue.name
