import frappe
from frappe.utils import flt, add_days
from erpnext.accounts.utils import get_account_currency
from frappe import _
from six import iteritems
from datetime import datetime
from core_erp.utils import get_fiscal_abbr
from frappe.model.naming import make_autoname

def autoname(doc, method = None):
	fiscal_yr_abbr = get_fiscal_abbr(doc.posting_date)
	if doc.is_return:
		doc.name = make_autoname("PR/"+doc.abbr+"/"+fiscal_yr_abbr+"/.#####")
	else:
		doc.name = make_autoname("MRN/"+doc.abbr+"/"+fiscal_yr_abbr+"/.#####")

def validate(self, method = None):
	frappe.db.set_value("Gate Entry",self.gate_entry_no,"status","Closed")

def on_update(self, method = None):
	if self.workflow_state == "Pending For Quality":
		create_quality_inspection(self)

def create_quality_inspection(self):
	for d in self.items:
		qc = frappe.db.sql("""select name from `tabQuality Inspection` where item_code = %s and reference_name = %s and row_name = %s""",(d.item_code,self.name,d.name))
		if frappe.db.get_value("Item", d.item_code, "inspection_required_before_purchase") and not qc and not self.is_return:
			qi = frappe.new_doc('Quality Inspection')
			qi.inspection_type = "Incoming"
			qi.item_code = d.item_code
			qi.item_name = d.item_name
			qi.supplier = self.supplier
			qi.supplier_invoice_no = self.supplier_bill_no
			qi.supplier_invoice_date = self.date
			qi.inspected_by = frappe.session.user
			qi.reference_type = self.doctype
			qi.company = self.company
			qi.mrn_type = frappe.db.get_value("Purchase Order",d.purchase_order,"po_type")
			qi.abbr = self.abbr
			qi.reference_name = self.name
			qi.acc_qty = d.qty
			qi.row_name = d.name
			qi.sample_size = 0
			qi.insert()
			frappe.msgprint("Quality Inspection Created for " + str(d.item_code))

# patch
def po_required(self):
	if frappe.db.get_value("Buying Settings", None, "po_required") == 'Yes' and \
			frappe.db.get_value("Supplier", self.supplier, "is_po_not_required") == 0:
		for d in self.get('items'):
			if not d.purchase_order:
				frappe.throw(_("Purchase Order number required for Item {0}").format(d.item_code))

def get_item_account_wise_additional_cost(purchase_document):
	landed_cost_vouchers = frappe.get_all("Landed Cost Purchase Receipt", fields=["parent"],
		filters = {"receipt_document": purchase_document, "docstatus": 1})

	if not landed_cost_vouchers:
		return

	item_account_wise_cost = {}

	for lcv in landed_cost_vouchers:
		landed_cost_voucher_doc = frappe.get_doc("Landed Cost Voucher", lcv.parent)
		based_on_field = frappe.scrub(landed_cost_voucher_doc.distribute_charges_based_on)
		total_item_cost = 0

		for item in landed_cost_voucher_doc.items:
			total_item_cost += item.get(based_on_field)

		for item in landed_cost_voucher_doc.items:
			if item.receipt_document == purchase_document:
				for account in landed_cost_voucher_doc.taxes:
					item_account_wise_cost.setdefault((item.item_code, item.purchase_receipt_item), {})
					item_account_wise_cost[(item.item_code, item.purchase_receipt_item)].setdefault(account.expense_account, 0.0)
					item_account_wise_cost[(item.item_code, item.purchase_receipt_item)][account.expense_account] += \
						account.amount * item.get(based_on_field) / total_item_cost

	return item_account_wise_cost

def get_gl_entries(self, warehouse_account=None):
	from erpnext.accounts.general_ledger import process_gl_map

	stock_rbnb = self.get_company_default("stock_received_but_not_billed")
	stock_rbnb_currency = get_account_currency(stock_rbnb)
	landed_cost_entries = get_item_account_wise_additional_cost(self.name)
	expenses_included_in_valuation = self.get_company_default("expenses_included_in_valuation")

	gl_entries = []
	warehouse_with_no_account = []
	negative_expense_to_be_booked = 0.0
	stock_items = self.get_stock_items()
	for d in self.get("items"):
		if d.item_code in stock_items and flt(d.valuation_rate) and flt(d.qty):
			if warehouse_account.get(d.warehouse):
				stock_value_diff = frappe.db.get_value("Stock Ledger Entry",
					{"voucher_type": "Purchase Receipt", "voucher_no": self.name,
					"voucher_detail_no": d.name, "warehouse": d.warehouse}, "stock_value_difference")

				if not stock_value_diff:
					continue

				# If PR is sub-contracted and fg item rate is zero
				# in that case if account for shource and target warehouse are same,
				# then GL entries should not be posted
				if flt(stock_value_diff) == flt(d.rm_supp_cost) \
					and warehouse_account.get(self.supplier_warehouse) \
					and warehouse_account[d.warehouse]["account"] == warehouse_account[self.supplier_warehouse]["account"]:
						continue
				if self.transfer_type == "Internal Transfer":
					stock_rbnb = d.expense_account
				gl_entries.append(self.get_gl_dict({
					"account": warehouse_account[d.warehouse]["account"],
					"against": stock_rbnb,
					"cost_center": d.cost_center,
					"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
					"debit": stock_value_diff
				}, warehouse_account[d.warehouse]["account_currency"], item=d))

				# stock received but not billed
				if d.base_net_amount:
					gl_entries.append(self.get_gl_dict({
						"account": stock_rbnb,
						"against": warehouse_account[d.warehouse]["account"],
						"cost_center": d.cost_center,
						"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
						"credit": flt(d.base_net_amount, d.precision("base_net_amount")),
						"credit_in_account_currency": flt(d.base_net_amount, d.precision("base_net_amount")) \
							if stock_rbnb_currency==self.company_currency else flt(d.net_amount, d.precision("net_amount"))
					}, stock_rbnb_currency, item=d))

				negative_expense_to_be_booked += flt(d.item_tax_amount)

				# Amount added through landed-cost-voucher
				if d.landed_cost_voucher_amount and landed_cost_entries:
					for account, amount in iteritems(landed_cost_entries[(d.item_code, d.name)]):
						gl_entries.append(self.get_gl_dict({
							"account": account,
							"against": warehouse_account[d.warehouse]["account"],
							"cost_center": d.cost_center,
							"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
							"credit": flt(amount),
							"project": d.project
						}, item=d))

				# sub-contracting warehouse
				if flt(d.rm_supp_cost) and warehouse_account.get(self.supplier_warehouse):
					gl_entries.append(self.get_gl_dict({
						"account": warehouse_account[self.supplier_warehouse]["account"],
						"against": warehouse_account[d.warehouse]["account"],
						"cost_center": d.cost_center,
						"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
						"credit": flt(d.rm_supp_cost)
					}, warehouse_account[self.supplier_warehouse]["account_currency"], item=d))

				# divisional loss adjustment
				valuation_amount_as_per_doc = flt(d.base_net_amount, d.precision("base_net_amount")) + \
					flt(d.landed_cost_voucher_amount) + flt(d.rm_supp_cost) + flt(d.item_tax_amount)

				divisional_loss = flt(valuation_amount_as_per_doc - stock_value_diff,
					d.precision("base_net_amount"))

				if divisional_loss:
					if self.is_return or flt(d.item_tax_amount):
						loss_account = expenses_included_in_valuation
					else:
						cogs_account = self.get_company_default("default_expense_account")
						loss_account = cogs_account

					gl_entries.append(self.get_gl_dict({
						"account": loss_account,
						"against": warehouse_account[d.warehouse]["account"],
						"cost_center": d.cost_center,
						"remarks": self.get("remarks") or _("Accounting Entry for Stock"),
						"debit": divisional_loss,
						"project": d.project
					}, stock_rbnb_currency, item=d))

			elif d.warehouse not in warehouse_with_no_account or \
				d.rejected_warehouse not in warehouse_with_no_account:
					warehouse_with_no_account.append(d.warehouse)

	self.get_asset_gl_entry(gl_entries)
	# Cost center-wise amount breakup for other charges included for valuation
	valuation_tax = {}
	for tax in self.get("taxes"):
		if tax.category in ("Valuation", "Valuation and Total") and flt(tax.base_tax_amount_after_discount_amount):
			if not tax.cost_center:
				frappe.throw(_("Cost Center is required in row {0} in Taxes table for type {1}").format(tax.idx, _(tax.category)))
			valuation_tax.setdefault(tax.name, 0)
			valuation_tax[tax.name] += \
				(tax.add_deduct_tax == "Add" and 1 or -1) * flt(tax.base_tax_amount_after_discount_amount)

	if negative_expense_to_be_booked and valuation_tax:
		# Backward compatibility:
		# If expenses_included_in_valuation account has been credited in against PI
		# and charges added via Landed Cost Voucher,
		# post valuation related charges on "Stock Received But Not Billed"
		# introduced in 2014 for backward compatibility of expenses already booked in expenses_included_in_valuation account

		negative_expense_booked_in_pi = frappe.db.sql("""select name from `tabPurchase Invoice Item` pi
			where docstatus = 1 and purchase_receipt=%s
			and exists(select name from `tabGL Entry` where voucher_type='Purchase Invoice'
				and voucher_no=pi.parent and account=%s)""", (self.name, expenses_included_in_valuation))

		against_account = ", ".join([d.account for d in gl_entries if flt(d.debit) > 0])
		total_valuation_amount = sum(valuation_tax.values())
		amount_including_divisional_loss = negative_expense_to_be_booked
		i = 1
		for tax in self.get("taxes"):
			if valuation_tax.get(tax.name):

				if negative_expense_booked_in_pi:
					account = stock_rbnb
				else:
					account = tax.account_head

				if i == len(valuation_tax):
					applicable_amount = amount_including_divisional_loss
				else:
					applicable_amount = negative_expense_to_be_booked * (valuation_tax[tax.name] / total_valuation_amount)
					amount_including_divisional_loss -= applicable_amount

				gl_entries.append(
					self.get_gl_dict({
						"account": account,
						"cost_center": tax.cost_center,
						"credit": applicable_amount,
						"remarks": self.remarks or _("Accounting Entry for Stock"),
						"against": against_account
					}, item=tax)
				)

				i += 1

	if warehouse_with_no_account:
		frappe.msgprint(_("No accounting entries for the following warehouses") + ": \n" +
			"\n".join(warehouse_with_no_account))

	return process_gl_map(gl_entries)


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	from erpnext.accounts.party import get_payment_terms_template

	doc = frappe.get_doc('Purchase Receipt', source_name)
	returned_qty_map = get_returned_qty_map(source_name)
	invoiced_qty_map = get_invoiced_qty_map(source_name)
	cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
	due_date = add_days(doc.posting_date, 30)
	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("All items have already been Invoiced/Returned"))

		doc = frappe.get_doc(target)
		doc.ignore_pricing_rule = 1
		doc.due_date = due_date
		doc.payment_terms_template = get_payment_terms_template(source.supplier, "Supplier", source.company)
		doc.run_method("onload")
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty, returned_qty = get_pending_qty(source_doc)
		target_doc.cost_center = cost_center
		returned_qty_map[source_doc.name] = returned_qty

	def get_pending_qty(item_row):
		pending_qty = item_row.qty - invoiced_qty_map.get(item_row.name, 0)
		returned_qty = flt(returned_qty_map.get(item_row.name, 0))
		if returned_qty:
			if returned_qty >= pending_qty:
				pending_qty = 0
				returned_qty -= pending_qty
			else:
				pending_qty -= returned_qty
				returned_qty = 0
		return pending_qty, returned_qty


	doclist = get_mapped_doc("Purchase Receipt", source_name,	{
		"Purchase Receipt": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"supplier_warehouse":"supplier_warehouse",
				"is_return": "is_return",
				"supplier_bill_no":"bill_no",
				"supplier_invoice_date": "bill_date"
			},
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Purchase Receipt Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "pr_detail",
				"parent": "purchase_receipt",
				"purchase_order_item": "po_detail",
				"purchase_order": "purchase_order",
				"is_fixed_asset": "is_fixed_asset",
				"asset_location": "asset_location",
				"asset_category": 'asset_category'
			},
			"postprocess": update_item
#			"filter": lambda d: get_pending_qty(d)[0] <= 0 if not doc.get("is_return") else get_pending_qty(d)[0] > 0
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	return doclist

def get_invoiced_qty_map(purchase_receipt):
	"""returns a map: {pr_detail: invoiced_qty}"""
	invoiced_qty_map = {}

	for pr_detail, qty in frappe.db.sql("""select pr_detail, qty from `tabPurchase Invoice Item`
		where purchase_receipt=%s and docstatus=1""", purchase_receipt):
			if not invoiced_qty_map.get(pr_detail):
				invoiced_qty_map[pr_detail] = 0
			invoiced_qty_map[pr_detail] += qty

	return invoiced_qty_map

def get_returned_qty_map(purchase_receipt):
	"""returns a map: {so_detail: returned_qty}"""
	returned_qty_map = frappe._dict(frappe.db.sql("""select pr_item.purchase_receipt_item, abs(pr_item.qty) as qty
		from `tabPurchase Receipt Item` pr_item, `tabPurchase Receipt` pr
		where pr.name = pr_item.parent
			and pr.docstatus = 1
			and pr.is_return = 1
			and pr.return_against = %s
	""", purchase_receipt))

	return returned_qty_map