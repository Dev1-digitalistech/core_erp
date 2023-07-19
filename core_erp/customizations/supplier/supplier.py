from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe import msgprint, _
from frappe.model.naming import set_name_by_naming_series

def autoname_dup(self,method=None):
	# pass
	supp_master_name = frappe.defaults.get_global_default('supp_master_name')
	if supp_master_name == 'Supplier Name':
		self.name = self.supplier_code
	else:
		set_name_by_naming_series(self)