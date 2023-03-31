import frappe
from frappe.utils import cint
from six import text_type
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname, revert_series_if_last
from frappe.utils import flt, cint, get_link_to_form
from frappe.utils.jinja import render_template
from frappe.utils.data import add_days
from six import string_types


# def before_insert(self, method=None):
# 	frappe.msgprint(str(self.reference_name))
# 	frappe.msgprint(str(self.expiry_date))
	
# 	self.expiry_date=data[0]['expiry_date']

def get_name_from_hash():
	"""
	Get a name for a Batch by generating a unique hash.
	:return: The hash that was generated.
	"""
	temp = None
	while not temp:
		temp = frappe.generate_hash()[:7].upper()
		if frappe.db.exists('Batch', temp):
			temp = None

	return temp


def before_naming(self,method=None):
	frappe.msgprint('naming function before naming')
	# frappe.msgprint(str(method))
	cc=str(frappe.db.get_value("Supplier",{"name":self.supplier},"supplier_name"))
	# frappe.msgprint(f'not working: {cc}')
	self.supp=cc[0:5]
	frappe.msgprint(str(self.name))
	data = frappe.db.sql(f"""SELECT expiry_date,item_code from `tabPurchase Receipt Item` where parent='{self.reference_name}' """,as_dict=1)
	# frappe.msgprint(str(data[0]['expiry_date']))
	for items in data:
		self.expiry_date=items['expiry_date']
		

def get_batch_naming_series():
	"""
	Get naming series key for a Batch.

	Naming series key is in the format [prefix].[#####]
	:return: The naming series or empty string if not available
	"""
	series = ''
	if batch_uses_naming_series():
		prefix = _get_batch_prefix()
		frappe.msgprint(str(prefix))
		key = _make_naming_series_key(prefix)
		series = key

	return series


def batch_uses_naming_series():
	"""
	Verify if the Batch is to be named using a naming series
	:return: bool
	"""
	
	use_naming_series = cint(frappe.db.get_single_value('Stock Settings', 'use_naming_series'))
	# frappe.msgprint(str(use_naming_series))
	return bool(use_naming_series)


def autoname(self, method=None):
	"""Generate random ID for batch if not specified"""
	if not self.batch_id:
		frappe.msgprint('helllo')
		create_new_batch, batch_number_series = frappe.db.get_value('Item', self.item,
			['create_new_batch', 'batch_number_series'])

		if create_new_batch:
			if batch_number_series:
				self.batch_id = make_autoname(batch_number_series)
			elif batch_uses_naming_series():
				self.batch_id = self.get_name_from_naming_series()
			else:
				self.batch_id = get_name_from_hash()
		else:
			frappe.throw(_('Batch ID is mandatory'), frappe.MandatoryError)
	if self.batch_id and frappe.db.get_value('Item', self.item,"item_group") == "Finished Item":
		self.name = self.batch_id
	if self.batch_id and frappe.db.get_value('Item', self.item,"item_group") == "Finished Goods":
		self.name = self.batch_id
	if self.batch_id and frappe.db.get_value('Item', self.item,"item_group") == "Semi-Finished Goods":
		self.name = self.batch_id

def before_save(self):
	has_expiry_date, shelf_life_in_days = frappe.db.get_value('Item', self.item, ['has_expiry_date', 'shelf_life_in_days'])
	if not self.expiry_date and has_expiry_date and shelf_life_in_days:
		self.expiry_date = add_days(self.manufacturing_date, shelf_life_in_days)
	# if has_expiry_date and not self.expiry_date:
	# 	frappe.throw(msg=_("Please set {0} for Batched Item {1}, which is used to set {2} on Submit.") \
	# 		.format(frappe.bold("Shelf Life in Days"),
	# 			get_link_to_form("Item", self.item),
	# 			frappe.bold("Batch Expiry Date")),
	# 		title=_("Expiry Date Mandatory"))

# @frappe.whitelist(allow_guest=True)
# def expiry_date(name,mrn):
# 	data = frappe.db.sql(f"""SELECT expiry_date from `tabPurchase Receipt Item` where batch_no='{name}' """,as_dict=0)
# 	return data
