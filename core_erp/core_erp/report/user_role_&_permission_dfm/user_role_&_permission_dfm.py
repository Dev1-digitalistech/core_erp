from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate
from frappe.permissions import get_all_perms
from datetime import datetime

def execute(filters=None):
	if not filters: filters = {}
	data = []
	columns = get_columns(filters)
	user_data = get_data(filters)
	for usr in user_data:
		perms = get_all_perms(usr.role)
		for p in perms:
			data.append([
				usr['modified'],usr['department'],usr['username'],usr['creation'],usr['created_time'],usr['status'],usr['email'], usr['full_name'], usr['role'],
				p['parent'], p['read'], p['write'], p['create'], p['submit'], p['cancel'], p['delete'], p['amend'], p['report'], p['export'],
				p['import'], p['share'], p['print'], p['email'], p['if_owner'], p['set_user_permissions'],usr['last_working_day'],usr['department'],
				usr['last_login'],usr['last_active']
			])
			
	return columns, data
	
	
def get_columns(filters):
	"""return columns based on filters"""
	columns = [
		{"label":_("Modified Date"),"fieldname":"modified","fieldtype":"Date","width":100},
		{"label": _("UserName"), "fieldname": "username", "fieldtype": "Data", "width": 100},
		{"label": _("department"), "fieldname": "department", "fieldtype": "Data", "width": 100},
		{"label":_("Creation Date"),"fieldname":"creation","fieldtype":"Date","width":100},
		{"label":_("Created Time"),"fieldname":"created_time","fieldtype":"Data","width":100},
		{"label":_("Status"),"fieldname":"status","fieldtype":"Data","width":100},
		{"label": _("User Email"), "fieldname": "Email", "fieldtype": "Data", "width": 150},
		{"label": _("Full Name"), "fieldname": "full_name","fieldtype": "Data", "width": 150},
		{"label": _("Role Access"), "fieldname": "role", "fieldtype": "Data", "width": 150},
		{"label": _("Doctypes"), "fieldname": "doctype", "fieldtype": "Data", "width": 150},
		{"label": _("Read"), "fieldname": "read", "fieldtype": "Check", "width": 80},
		{"label": _("write"), "fieldname": "write", "fieldtype": "Check", "width": 80},
		{"label": _("create"), "fieldname": "create", "fieldtype": "Check", "width": 80},
		{"label": _("submit"), "fieldname": "submit", "fieldtype": "Check", "width": 80},
		{"label": _("cancel"), "fieldname": "cancel", "fieldtype": "Check", "width": 80},
		{"label": _("delete"), "fieldname": "delete", "fieldtype": "Check", "width": 80},
		{"label": _("amend"), "fieldname": "amend", "fieldtype": "Check", "width": 80},
		{"label": _("report"), "fieldname": "report", "fieldtype": "Check", "width": 80},
		{"label": _("export"), "fieldname": "export", "fieldtype": "Check", "width": 80},
		{"label": _("import"), "fieldname": "import", "fieldtype": "Check", "width": 80},
		{"label": _("share"), "fieldname": "share", "fieldtype": "Check", "width": 80},
		{"label": _("print"), "fieldname": "print", "fieldtype": "Check", "width": 80},
		{"label": _("email"), "fieldname": "email", "fieldtype": "Check", "width": 80},
		{"label": _("if_owner"), "fieldname": "if_owner", "fieldtype": "Check", "width": 80},
		{"label": _("set_user_permissions"), "fieldname": "set_user_permissions", "fieldtype": "Check", "width": 80},
		{"label": _("Last Working Days"), "fieldname": "last_working_day", "fieldtype": "Data", "width": 80},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Data", "width": 140},
		{"label": _("Last Login"), "fieldname": "last_login", "fieldtype": "Data", "width": 140},
		{"label": _("Last Acite"), "fieldname": "last_active", "fieldtype": "Data", "width": 140}
	]

	return columns
	
def get_conditions(filters):
	conditions = ""

	for field in ["username", "email"]:
		if filters.get(field):
			conditions += " and {0} = {1}".format(field, frappe.db.escape(filters.get(field)))

	return conditions
	
def get_data(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""SELECT
                                tu.modified,
                                tu.department,
                                tu.email,
                                DATE(tu.creation) AS "creation",
                                TIME(tu.creation) AS "created_time",
                                tu.full_name,
                                tu.username,
								tu.last_login,
								tu.last_active,
                                hs.role,
                                u.last_working_day,
								u.department,
                                CASE
                                    WHEN tu.enabled = 1 THEN "Active"
                                    ELSE "Inactive"
                                END AS "status"
                            FROM `tabUser` AS tu
                            JOIN `tabHas Role` AS hs ON tu.name = hs.parent
                            LEFT JOIN `tabUser Connection` AS u ON tu.username = u.user
                            where hs.parent=tu.name %s""" % conditions, as_dict=1)
