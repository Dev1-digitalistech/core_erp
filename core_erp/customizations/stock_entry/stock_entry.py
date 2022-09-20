from __future__ import unicode_literals
import frappe
import frappe.defaults
import re
import datetime
from frappe import _
from frappe.utils import flt
from erpnext.stock.utils import get_incoming_rate
from erpnext.stock.stock_ledger import get_previous_sle
from erpnext.stock.get_item_details import get_conversion_factor
from core_erp.custom_integrations.snd.snd_integration import push_data_to_snd
import json
from six import string_types
from core_erp.utils import get_fiscal_abbr
from erpnext.stock.doctype.stock_entry.stock_entry import get_item_defaults
from frappe.model.naming import make_autoname

def autoname(doc, method = None):
	yr_abbr = get_fiscal_abbr(doc.posting_date)
	entry_type = frappe.db.get_value('Stock Entry Type',doc.stock_entry_type,'abbreviation')
	if not entry_type:
		frappe.throw('Kindly fill Abbreviation in Stock Entry Type')

	doc.name = make_autoname(f"{entry_type}/{doc.abbr}/{yr_abbr}/.#####")

def after_insert(doc, method = None):
	if doc.stock_entry_type == 'Manufacture':
		if doc.work_order:
			wo = frappe.get_doc("Work Order",doc.work_order)
			item = wo.production_item
			itm = frappe.get_doc("Item",item)
			if itm.item_group in ["Finished Goods","Semi-Finished Goods"] :
				auto_batch(doc)
				doc.save()

#not in use anymore
def on_submit(doc, method = None):
	if doc.stock_entry_type == "Material Transfer" and doc.reason=="SND Transfer":
		send_to_snd(doc)

def send_to_snd(doc):
	doc.data_push=1
	push_data_to_snd(doc)

def update_default_batch_in_item(self):
	for item in self.items:
		if item.s_warehouse:
			temp = frappe.db.sql(f"""select sle.batch_no, round(sum(sle.actual_qty),2)
				from `tabStock Ledger Entry` sle
				INNER JOIN `tabBatch` batch on sle.batch_no = batch.name
				where batch.disabled = 0
				and sle.item_code = '{item.item_code}'
				and sle.warehouse like '%{item.s_warehouse}%'
				and batch.docstatus < 2
				and (batch.expiry_date is null or batch.expiry_date >= '{self.posting_date}')
				group by batch_no having sum(sle.actual_qty) > {item.qty}
				order by batch.expiry_date, sle.batch_no desc
				limit 1""",as_dict = 1)
			if temp:
				item.batch_no = temp[0]['batch_no']

def validate_work_order(self):
	if self.purpose in ("Manufacture", "Material Transfer for Manufacture", "Material Consumption for Manufacture"):
		# check if work order is entered

		if (self.purpose=="Manufacture" or self.purpose=="Material Consumption for Manufacture") \
				and self.work_order:
			if not self.fg_completed_qty:
				frappe.throw(_("For Quantity (Manufactured Qty) is mandatory"))
			self.check_if_operations_completed()
			self.check_duplicate_entry_for_work_order()
	elif self.purpose not in ("Material Transfer", "Material Issue", "Material Receipt"):
		self.work_order = None

def set_basic_rate_for_finished_goods(self, raw_material_cost=0, scrap_material_cost=0):
	total_fg_qty = 0
	if not raw_material_cost and self.get("items"):
		raw_material_cost = sum([flt(row.basic_amount) for row in self.items
			if row.s_warehouse and not row.t_warehouse])

		total_fg_qty = sum([flt(row.qty) for row in self.items
			if row.t_warehouse and not row.s_warehouse])

	if self.purpose in ["Manufacture", "Repack"]:
		for d in self.get("items"):
			if (d.transfer_qty and (d.bom_no or d.t_warehouse)
				and (getattr(self, "pro_doc", frappe._dict()).scrap_warehouse != d.t_warehouse)):

				if (self.work_order and self.purpose == "Manufacture"
					and frappe.db.get_single_value("Manufacturing Settings", "material_consumption")):
					bom_items = self.get_bom_raw_materials(d.transfer_qty)
					raw_material_cost=0.0
					for item in self.items:
						if not item.t_warehouse:
							raw_material_cost+=item.basic_amount
						else:
							fg_item_qty=item.qty
					#raw_material_cost = sum([flt(row.qty)*flt(row.rate) for row in bom_items.values()])

				if raw_material_cost and self.purpose == "Manufacture":
					d.basic_rate=flt(raw_material_cost/fg_item_qty)
					d.basic_amount=flt(raw_material_cost)
					#d.basic_rate = flt((raw_material_cost - scrap_material_cost) / flt(d.transfer_qty), d.precision("basic_rate"))
					#d.basic_amount = flt((raw_material_cost - scrap_material_cost), d.precision("basic_amount"))
				elif self.purpose == "Repack" and total_fg_qty and not d.set_basic_rate_manually:
					d.basic_rate = flt(raw_material_cost) / flt(total_fg_qty)
					d.basic_amount = d.basic_rate * flt(d.qty)


@frappe.whitelist()
def auto_batch(doc):
	wo = frappe.get_doc("Work Order",doc.work_order)
	ln = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", doc.line)
	line = ln[0]
	item = wo.production_item
	itm_shelf_life = frappe.db.get_value("Item",item, "shelf_life_in_days")
	#company = frappe.get_doc("Company",doc.company)
	company_abbr = frappe.db.get_value('Company',doc.company, "auto_batch")
	frappe.msgprint(str(doc.posting_date) +  ' - date')
	d = frappe.utils.formatdate(doc.posting_date, 'ddMMyy')
	batchid = str(item) + company_abbr + str(line) + str(d)
	btch = frappe.db.sql("""select name from `tabBatch` where name = %s""",batchid,as_dict=1)
	if not btch:
		batch = frappe.new_doc("Batch")
		batch.manufacturing_date = datetime.date.today()
		batch.expiry_date = frappe.utils.add_days(datetime.date.today(),itm_shelf_life)
		batch.reference_doctype = 'Stock Entry'
		batch.reference_name = doc.name
		batch.item = item
		batch.batch_id = batchid
		batch.save()
		for i in doc.items:
			if i.item_code == item:
				i.batch_no = batch.name
	else:
		for i in doc.items:
			if i.item_code == item:
				i.batch_no = btch[0].name

	return ''

@frappe.whitelist()
def get_uom_details(item_code, uom, qty):
	"""Returns dict `{"conversion_factor": [value], "transfer_qty": qty * [value]}`

	:param args: dict with `item_code`, `uom` and `qty`"""
	conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor")

	if not conversion_factor:
		frappe.msgprint(_("UOM coversion factor required for UOM: {0} in Item: {1}")
			.format(uom, item_code))
		ret = {'uom' : ''}
	else:
		ret = {
			'conversion_factor'		: flt(conversion_factor),
			'transfer_qty'			: flt(qty) * flt(conversion_factor)
		}
	return ret

@frappe.whitelist()
def get_warehouse_details(args):
	if isinstance(args, string_types):
		args = json.loads(args)

	args = frappe._dict(args)

	ret = {}
	if args.warehouse and args.item_code:
		args.update({
			"posting_date": args.posting_date,
			"posting_time": args.posting_time,
		})
		ret = {
			"actual_qty" : get_previous_sle(args).get("qty_after_transaction") or 0,
			"basic_rate" : get_incoming_rate(args)
		}
	return ret

def get_unconsumed_raw_materials(self):
	wo = frappe.get_doc("Work Order", self.work_order)
	wo_items = frappe.get_all('Work Order Item',
		filters={'parent': self.work_order},
		fields=["item_code", "item_name", "required_qty", "consumed_qty", "transferred_qty"]
		)

	work_order_qty = wo.material_transferred_for_manufacturing or wo.qty
	for item in wo_items:
		item_account_details = get_item_defaults(item.item_code, self.company)
		# Take into account consumption if there are any.

		wo_item_qty = item.transferred_qty or item.required_qty

		req_qty_each = (
			(flt(wo_item_qty) - flt(item.consumed_qty)) /
				(flt(work_order_qty) - flt(wo.produced_qty))
		)

		qty = req_qty_each * flt(self.fg_completed_qty)
		if qty > 0:
			self.add_to_stock_entry_detail({
				item.item_code: {
					"from_warehouse": wo.wip_wh,
					"to_warehouse": "",
					"qty": qty,
					"item_name": item.item_name,
					"description": item.description,
					"stock_uom": item_account_details.stock_uom,
					"expense_account": item_account_details.get("expense_account"),
					"cost_center": item_account_details.get("buying_cost_center"),
				}
			})