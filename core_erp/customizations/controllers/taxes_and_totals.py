import frappe
from frappe.utils import flt, cint, nowdate
from frappe.utils import flt
def calculate_item_values(self):
	if not self.discount_amount_applied:
		for item in self.doc.get("items"):
			self.doc.round_floats_in(item)

			if item.discount_percentage == 100:
				item.rate = 0.0
			elif item.price_list_rate:
				if not item.rate or (item.pricing_rules and item.discount_percentage > 0):
					item.rate = flt(item.price_list_rate *
						(1.0 - (item.discount_percentage / 100.0)), item.precision("rate"))
					item.discount_amount = item.price_list_rate * (item.discount_percentage / 100.0)
				elif item.discount_amount and item.pricing_rules:
					item.rate =  item.price_list_rate - item.discount_amount

			if item.doctype in ['Quotation Item', 'Sales Order Item', 'Delivery Note Item', 'Sales Invoice Item']:
				item.rate_with_margin, item.base_rate_with_margin = self.calculate_margin(item)
				if flt(item.rate_with_margin) > 0:
					item.rate = flt(item.rate_with_margin * (1.0 - (item.discount_percentage / 100.0)), item.precision("rate"))
					item.discount_amount = item.rate_with_margin - item.rate
				elif flt(item.price_list_rate) > 0:
					item.discount_amount = item.price_list_rate - item.rate
			elif flt(item.price_list_rate) > 0 and not item.discount_amount:
				item.discount_amount = item.price_list_rate - item.rate

			item.net_rate = item.rate

			if not item.qty and self.doc.get("is_return"):
				item.amount = flt(-1 * item.rate, item.precision("amount"))
			else:
				item.amount = flt(item.rate * item.qty,	item.precision("amount"))

#				item.net_amount = item.amount
			if self.doc.doctype == "Purchase Invoice":
				item.net_amount = item.amount_s
			else:
				item.net_amount = item.amount

			self._set_in_company_currency(item, ["price_list_rate", "rate", "net_rate", "amount", "net_amount"])

			item.item_tax_amount = 0.0

def get_current_tax_amount(self, item, tax, item_tax_map):
	tax_rate = self._get_tax_rate(tax, item_tax_map)
	current_tax_amount = 0.0

	if tax.charge_type == "Actual":
			# distribute the tax amount proportionally to each item row
		actual = flt(tax.tax_amount, tax.precision("tax_amount"))
		current_tax_amount = item.net_amount*actual / self.doc.net_total if self.doc.net_total else 0.0

	elif tax.charge_type == "On Net Total":
		if self.doc.doctype == "Purchase Invoice" and not self.doc.is_return and self.doc.total_invoice_amount:
			current_tax_amount = (tax_rate / 100.0) * item.amount_s
		else:
			current_tax_amount = (tax_rate / 100.0) * item.net_amount
	elif tax.charge_type == "On Previous Row Amount":
		current_tax_amount = (tax_rate / 100.0) * \
			self.doc.get("taxes")[cint(tax.row_id) - 1].tax_amount_for_current_item
	elif tax.charge_type == "On Previous Row Total":
		current_tax_amount = (tax_rate / 100.0) * \
			self.doc.get("taxes")[cint(tax.row_id) - 1].grand_total_for_current_item
	elif tax.charge_type == "On Item Quantity":
		current_tax_amount = tax_rate * item.qty

	self.set_item_wise_tax(item, tax, tax_rate, current_tax_amount)

	return current_tax_amount