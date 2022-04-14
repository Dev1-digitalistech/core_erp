import frappe
from frappe.model.naming import make_autoname

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

def batch_uses_naming_series():
	"""
	Verify if the Batch is to be named using a naming series
	:return: bool
	"""
	use_naming_series = cint(frappe.db.get_single_value('Stock Settings', 'use_naming_series'))
	return bool(use_naming_series)


def autoname(self):
	"""Generate random ID for batch if not specified"""
	if not self.batch_id:
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