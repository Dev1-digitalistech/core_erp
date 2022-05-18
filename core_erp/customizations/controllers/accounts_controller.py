import frappe,erpnext
from frappe.utils import flt, get_datetime, format_datetime
from frappe.model.meta import get_field_precision
from frappe.utils import (today, flt, cint, fmt_money, formatdate,
	getdate, add_days, add_months, get_last_day, nowdate, get_link_to_form)
from erpnext.accounts.doctype.pricing_rule.utils import (apply_pricing_rule_on_transaction,
	apply_pricing_rule_for_free_items, get_applied_pricing_rules)
from frappe import _, throw

def validate(self):
	if not self.get('is_return'):
		self.validate_qty_is_not_zero()

	if self.get("_action") and self._action != "update_after_submit":
		self.set_missing_values(for_validate=True)

	self.ensure_supplier_is_not_blocked()

	self.validate_date_with_fiscal_year()

	if self.meta.get_field("currency"):
		self.calculate_taxes_and_totals()

		if not self.meta.get_field("is_return") or not self.is_return:
			self.validate_value("base_grand_total", ">=", 0)

		validate_return(self)
		self.set_total_in_words()

	self.validate_all_documents_schedule()

	if self.meta.get_field("taxes_and_charges"):
		self.validate_enabled_taxes_and_charges()
		self.validate_tax_account_company()

	self.validate_party()
	self.validate_currency()

	if self.doctype == 'Purchase Invoice':
		self.calculate_paid_amount()

	if self.doctype in ['Purchase Invoice', 'Sales Invoice']:
		pos_check_field = "is_pos" if self.doctype=="Sales Invoice" else "is_paid"
		if cint(self.allocate_advances_automatically) and not cint(self.get(pos_check_field)):
			self.set_advances()

		if self.is_return:
			self.validate_qty()
		else:
			self.validate_deferred_start_and_end_date()

	validate_regional(self)
		
	validate_einvoice_fields(self)

	if self.doctype != 'Material Request':
		apply_pricing_rule_on_transaction(self)

def validate_qty_is_not_zero(self):
	if self.doctype != "Purchase Receipt":
		for item in self.items:
			if not item.qty and self.doctype != "Purchase Invoice":
				frappe.throw(_("Item quantity can not be zero"))

def validate_return(doc):
	if not doc.meta.get_field("is_return") or not doc.is_return:
		return

	if doc.return_against:
		validate_return_against(doc)
		validate_returned_items(doc)

def set_missing_values(self, for_validate=False):
		if frappe.flags.in_test:
			for fieldname in ["posting_date", "transaction_date"]:
				if self.meta.get_field(fieldname) and not self.get(fieldname):
					self.set(fieldname, today())
					break

def calculate_taxes_and_totals(self):
	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
	calculate_taxes_and_totals(self)

	if self.doctype in ["Quotation", "Sales Order", "Delivery Note", "Sales Invoice"]:
		self.calculate_commission()
		self.calculate_contribution()

def validate_date_with_fiscal_year(self):
	if self.meta.get_field("fiscal_year"):
		date_field = ""
		if self.meta.get_field("posting_date"):
			date_field = "posting_date"
		elif self.meta.get_field("transaction_date"):
			date_field = "transaction_date"

		if date_field and self.get(date_field):
			validate_fiscal_year(self.get(date_field), self.fiscal_year, self.company,
							 self.meta.get_label(date_field), self)

def validate_return_against(doc):
	if not frappe.db.exists(doc.doctype, doc.return_against):
			frappe.throw(_("Invalid {0}: {1}")
				.format(doc.meta.get_label("return_against"), doc.return_against))
	else:
		ref_doc = frappe.get_doc(doc.doctype, doc.return_against)

		party_type = "customer" if doc.doctype in ("Sales Invoice", "Delivery Note") else "supplier"

		if ref_doc.company == doc.company and ref_doc.get(party_type) == doc.get(party_type) and ref_doc.docstatus == 1:
			# validate posting date time
			return_posting_datetime = "%s %s" % (doc.posting_date, doc.get("posting_time") or "00:00:00")
			ref_posting_datetime = "%s %s" % (ref_doc.posting_date, ref_doc.get("posting_time") or "00:00:00")

			if get_datetime(return_posting_datetime) < get_datetime(ref_posting_datetime):
				frappe.throw(_("Posting timestamp must be after {0}").format(format_datetime(ref_posting_datetime)))

			# validate same exchange rate
			if doc.conversion_rate != ref_doc.conversion_rate:
				frappe.throw(_("Exchange Rate must be same as {0} {1} ({2})")
					.format(doc.doctype, doc.return_against, ref_doc.conversion_rate))

			# validate update stock
			if doc.doctype == "Sales Invoice" and doc.update_stock and not ref_doc.update_stock:
					frappe.throw(_("'Update Stock' can not be checked because items are not delivered via {0}")
						.format(doc.return_against))

def validate_returned_items(doc):
	from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

	valid_items = frappe._dict()

	select_fields = "item_code, qty, stock_qty, rate, parenttype, conversion_factor"
	if doc.doctype != 'Purchase Invoice':
		select_fields += ",serial_no, batch_no"

	if doc.doctype in ['Purchase Invoice', 'Purchase Receipt']:
		select_fields += ",rejected_qty, received_qty"

	for d in frappe.db.sql("""select {0} from `tab{1} Item` where parent = %s"""
		.format(select_fields, doc.doctype), doc.return_against, as_dict=1):
			valid_items = get_ref_item_dict(valid_items, d)

	if doc.doctype in ("Delivery Note", "Sales Invoice"):
		for d in frappe.db.sql("""select item_code, qty, serial_no, batch_no from `tabPacked Item`
			where parent = %s""".format(doc.doctype), doc.return_against, as_dict=1):
				valid_items = get_ref_item_dict(valid_items, d)

	already_returned_items = get_already_returned_items(doc)

	# ( not mandatory when it is Purchase Invoice or a Sales Invoice without Update Stock )
	warehouse_mandatory = not ((doc.doctype=="Purchase Invoice" or doc.doctype=="Sales Invoice") and not doc.update_stock)

	items_returned = False
	for d in doc.get("items"):
		if d.item_code and (flt(d.qty) < 0 or flt(d.get('received_qty')) < 0):
			if d.item_code not in valid_items:
				frappe.throw(_("Row # {0}: Returned Item {1} does not exist in {2} {3}")
					.format(d.idx, d.item_code, doc.doctype, doc.return_against))
			else:
				ref = valid_items.get(d.item_code, frappe._dict())
				validate_quantity(doc, d, ref, valid_items, already_returned_items)

				if ref.rate and doc.doctype in ("Delivery Note", "Sales Invoice") and flt(d.rate) > ref.rate:
					frappe.throw(_("Row # {0}: Rate cannot be greater than the rate used in {1} {2}")
						.format(d.idx, doc.doctype, doc.return_against))

				elif ref.batch_no and d.batch_no not in ref.batch_no:
					frappe.throw(_("Row # {0}: Batch No must be same as {1} {2}")
						.format(d.idx, doc.doctype, doc.return_against))

				elif ref.serial_no:
					if not d.serial_no:
						frappe.throw(_("Row # {0}: Serial No is mandatory").format(d.idx))
					else:
						serial_nos = get_serial_nos(d.serial_no)
						for s in serial_nos:
							if s not in ref.serial_no:
								frappe.throw(_("Row # {0}: Serial No {1} does not match with {2} {3}")
									.format(d.idx, s, doc.doctype, doc.return_against))

				if warehouse_mandatory and frappe.db.get_value("Item", d.item_code, "is_stock_item") \
					and not d.get("warehouse"):
						frappe.throw(_("Warehouse is mandatory"))

			items_returned = True

		elif d.item_name:
			items_returned = True

	if not items_returned:
		frappe.throw(_("Atleast one item should be entered with negative quantity in return document"))

def validate_quantity(doc, args, ref, valid_items, already_returned_items):
	fields = ['stock_qty']
	if doc.doctype in ['Purchase Receipt', 'Purchase Invoice']:
		fields.extend(['received_qty', 'rejected_qty'])

	already_returned_data = already_returned_items.get(args.item_code) or {}

	company_currency = erpnext.get_company_currency(doc.company)
	stock_qty_precision = get_field_precision(frappe.get_meta(doc.doctype + " Item")
			.get_field("stock_qty"), company_currency)

	for column in fields:
		returned_qty = flt(already_returned_data.get(column, 0)) if len(already_returned_data) > 0 else 0

		if column == 'stock_qty':
			reference_qty = ref.get(column)
			current_stock_qty = args.get(column)
		else:
			reference_qty = ref.get(column) * ref.get("conversion_factor", 1.0)
			current_stock_qty = args.get(column) * args.get("conversion_factor", 1.0)

		max_returnable_qty = flt(reference_qty, stock_qty_precision) - returned_qty
		label = column.replace('_', ' ').title()

		if reference_qty:
			if flt(args.get(column)) > 0:
				frappe.throw(_("{0} must be negative in return document").format(label))
			# elif returned_qty >= reference_qty and args.get(column):
			# 	frappe.throw(_("Item {0} has already been returned")
			# 		.format(args.item_code), StockOverReturnError)
			# elif abs(flt(current_stock_qty, stock_qty_precision)) > max_returnable_qty:
			# 	frappe.throw(_("Row # {0}: Cannot return more than {1} for Item {2}")
			# 		.format(args.idx, max_returnable_qty, args.item_code), StockOverReturnError)

def get_already_returned_items(doc):
	column = 'child.item_code, sum(abs(child.qty)) as qty, sum(abs(child.stock_qty)) as stock_qty'
	if doc.doctype in ['Purchase Invoice', 'Purchase Receipt']:
		column += """, sum(abs(child.rejected_qty) * child.conversion_factor) as rejected_qty,
			sum(abs(child.received_qty) * child.conversion_factor) as received_qty"""

	data = frappe.db.sql("""
		select {0}
		from
			`tab{1} Item` child, `tab{2}` par
		where
			child.parent = par.name and par.docstatus = 1
			and par.is_return = 1 and par.return_against = %s
		group by item_code
	""".format(column, doc.doctype, doc.doctype), doc.return_against, as_dict=1)

	items = {}

	for d in data:
		items.setdefault(d.item_code, frappe._dict({
			"qty": d.get("qty"),
			"stock_qty": d.get("stock_qty"),
			"received_qty": d.get("received_qty"),
			"rejected_qty": d.get("rejected_qty")
		}))

	return items

def get_ref_item_dict(valid_items, ref_item_row):
	from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

	valid_items.setdefault(ref_item_row.item_code, frappe._dict({
		"qty": 0,
		"rate": 0,
		"stock_qty": 0,
		"rejected_qty": 0,
		"received_qty": 0,
		"serial_no": [],
		"conversion_factor": ref_item_row.get("conversion_factor", 1),
		"batch_no": []
	}))
	item_dict = valid_items[ref_item_row.item_code]
	item_dict["qty"] += ref_item_row.qty
	item_dict["stock_qty"] += ref_item_row.get('stock_qty', 0)
	if ref_item_row.get("rate", 0) > item_dict["rate"]:
		item_dict["rate"] = ref_item_row.get("rate", 0)

	if ref_item_row.parenttype in ['Purchase Invoice', 'Purchase Receipt']:
		item_dict["received_qty"] += ref_item_row.received_qty
		item_dict["rejected_qty"] += ref_item_row.rejected_qty

	if ref_item_row.get("serial_no"):
		item_dict["serial_no"] += get_serial_nos(ref_item_row.serial_no)

	if ref_item_row.get("batch_no"):
		item_dict["batch_no"].append(ref_item_row.batch_no)

	return valid_items

@erpnext.allow_regional
def validate_regional(doc):
	pass

@erpnext.allow_regional
def validate_einvoice_fields(doc):
	pass