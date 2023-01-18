from __future__ import unicode_literals
from unicodedata import category
import frappe
import frappe.defaults
import re
from frappe.utils import now
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
import frappe, erpnext
import frappe.defaults
from frappe import _
from frappe.utils import cstr, cint, flt, comma_or, getdate, nowdate, formatdate, format_time, get_link_to_form
from erpnext.stock.utils import get_incoming_rate
from erpnext.stock.stock_ledger import get_previous_sle, NegativeStockError, get_valuation_rate
from erpnext.stock.get_item_details import get_bin_details, get_default_cost_center, get_conversion_factor, get_reserved_qty_for_so
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.setup.doctype.brand.brand import get_brand_defaults
from erpnext.stock.doctype.batch.batch import get_batch_no, set_batch_nos, get_batch_qty
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.manufacturing.doctype.bom.bom import validate_bom_no, add_additional_cost
from erpnext.stock.utils import get_bin
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate,add_days
from erpnext.stock.doctype.serial_no.serial_no import update_serial_nos_after_submit, get_serial_nos
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import OpeningEntryAccountError
from frappe.model.naming import make_autoname
import json
from six import string_types, itervalues, iteritems

# def autoname(doc, method = None):
# 	yr_abbr = get_fiscal_abbr(doc.posting_date)
# 	entry_type = frappe.db.get_value('Stock Entry Type',doc.stock_entry_type,doc.abbr)
# 	frappe.msgprint(str(entry_type))
# 	if not entry_type:
# 		frappe.throw('Kindly fill Abbreviation in Stock Entry Type')

# 	doc.name = make_autoname(f"{entry_type}/{doc.abbr}/{yr_abbr}/.#####")

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
# def on_submit(doc, method = None):
# 	if doc.stock_entry_type == "Material Transfer" and doc.reason=="SND Transfer":
# 		send_to_snd(doc)

def on_submit_dup(self):

	self.update_stock_ledger()

	update_serial_nos_after_submit(self, "items")
	self.update_work_order()
	self.validate_purchase_order()
	if self.purchase_order and self.purpose == "Send to Subcontractor":
		self.update_purchase_order_supplied_items()
	self.make_gl_entries()
	self.update_cost_in_project()
	self.validate_reserved_serial_no_consumption()
	self.update_transferred_qty()
	self.update_quality_inspection()
	if self.work_order and self.purpose == "Manufacture":
		self.update_so_in_serial_number()
	# if self.stock_entry_type == "Material Transfer" and self.reason=="SND Transfer":
	# 	self.send_to_snd()


def validate(self):
	self.pro_doc = frappe._dict()
	if self.work_order:
		self.pro_doc = frappe.get_doc('Work Order', self.work_order)

	self.validate_posting_time()
	self.validate_purpose()
	self.validate_item()
	self.validate_customer_provided_item()
	self.set_transfer_qty()
	self.validate_uom_is_integer("uom", "qty")
	self.validate_uom_is_integer("stock_uom", "transfer_qty")
	self.validate_warehouse()
	self.validate_work_order()
	self.validate_bom()
	self.validate_finished_goods()
	self.validate_with_material_request()
	self.validate_batch()
	self.validate_inspection()
	self.validate_fg_completed_qty()
	self.validate_difference_account()
	self.set_job_card_data()
	self.set_purpose_for_stock_entry()

	if not self.from_bom:
		self.fg_completed_qty = 0.0

	if self._action == 'submit':
		self.make_batches('t_warehouse')
	else:
		set_batch_nos(self, 's_warehouse')

	self.set_incoming_rate()
	self.validate_serialized_batch()
	self.set_actual_qty()
	self.calculate_rate_and_amount(update_finished_item_rate=False)
	if self.stock_entry_type=="Material Transfer" and self.reason=="SND Transfer":
		self.data_push=1



# def send_to_snd(doc):
# 	doc.data_push=1
# 	push_data_to_snd(doc)

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
	itm = frappe.get_doc("Item",item)
	company = frappe.get_doc("Company",doc.company)
	frappe.msgprint(str(doc.posting_date) +  ' - date')
	d = frappe.utils.formatdate(doc.posting_date, 'ddMMyy')
	batchid = str(item) + company.auto_batch + str(line) + str(d)
	btch = frappe.db.sql("""select name from `tabBatch` where name = %s""",batchid,as_dict=1)
	if not btch:
		batch = frappe.new_doc("Batch")
		batch.manufacturing_date = datetime.date.today()
		batch.expiry_date = frappe.utils.add_days(datetime.date.today(),itm.shelf_life_in_days)
		batch.reference_doctype = 'Stock Entry'
		batch.reference_name = doc.name
		batch.item = item
		batch.batch_id = batchid
		batch.save()
		cnt = 0
		for i in doc.items:
			if i.item_code == item:
				doc.items[cnt].batch_no = batch.name
			cnt = cnt + 1
	else:
		cnt = 0
		for i in doc.items:
			if i.item_code == item:
			        doc.items[cnt].batch_no = btch[0].name
			cnt = cnt + 1
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
   
   

@frappe.whitelist()
def new_function(doc,company,date,bom):
    com = company
    subject = frappe.db.get_value('BOM', bom, 'item')
    data = frappe.db.get_value('Item',subject,['item_group','item_sub_group','product_category','category','price_category','mrp'])
    var = data[0]
    var2= data[1]
    var3 = data[2]
    var4 = data[3]
    var5 = data[4]
    var6 = data[5]

    data2 = frappe.db.sql(f""" select rate,expense_account,from_date,to_date,company
                        	from `tabAdditional Cost` where item_group = '{var}' and
                         	item_sub_group = '{var2}' and product_category = '{var3}' and
                          	category = '{var4}' and price_category = '{var5}' and 
                           	mrp = '{var6}' """,as_dict=1)
  
    from_date = frappe.utils.formatdate(data2[0].from_date, 'dd/MM/yy')
    to_date = frappe.utils.formatdate(data2[0].to_date, 'dd/MM/yy')
    today = frappe.utils.formatdate(now(), 'dd/MM/yy')
    frm_comp = data2[0].company
    
    if com==frm_comp:
        if from_date < today < to_date:
            return data2
        else:
            frappe.throw("Date Have Been Expired")
    else:
        frappe.throw("Companies Are Not Same")
   
def validate_with_material_request(self):
	for item in self.get("items"):
		if item.material_request:
			mreq_item = frappe.db.get_value("Material Request Item",
				{"name": item.material_request_item, "parent": item.material_request},
				["item_code", "warehouse", "idx"], as_dict=True)
			if mreq_item.item_code != item.item_code or \
			mreq_item.warehouse != (item.s_warehouse if self.purpose== "Material Issue" else item.t_warehouse):
				frappe.throw(_("Item or Warehouse for row {0} does not match Material Request").format(item.idx),
					frappe.MappingMismatchError)


def get_transfered_raw_materials(self):
	transferred_materials = frappe.db.sql("""
		select
			item_name, original_item, item_code, sum(qty) as qty, sed.t_warehouse as warehouse,
			description, stock_uom, expense_account, cost_center
		from `tabStock Entry` se,`tabStock Entry Detail` sed
		where
			se.name = sed.parent and se.docstatus=1 and se.purpose='Material Transfer for Manufacture'
			and se.work_order= %s and ifnull(sed.t_warehouse, '') != ''
		group by sed.item_code, sed.t_warehouse
	""", self.work_order, as_dict=1)

	materials_already_backflushed = frappe.db.sql("""
		select
			item_code, sed.s_warehouse as warehouse, sum(qty) as qty
		from
			`tabStock Entry` se, `tabStock Entry Detail` sed
		where
			se.name = sed.parent and se.docstatus=1
			and (se.purpose='Manufacture' or se.purpose='Material Consumption for Manufacture')
			and se.work_order= %s and ifnull(sed.s_warehouse, '') != ''
		group by sed.item_code, sed.s_warehouse
	""", self.work_order, as_dict=1)

	backflushed_materials= {}
	for d in materials_already_backflushed:
		backflushed_materials.setdefault(d.item_code,[]).append({d.warehouse: d.qty})

	po_qty = frappe.db.sql("""select qty, produced_qty, material_transferred_for_manufacturing from
		`tabWork Order` where name=%s""", self.work_order, as_dict=1)[0]

	manufacturing_qty = flt(po_qty.qty)
	produced_qty = flt(po_qty.produced_qty)
	trans_qty = flt(po_qty.material_transferred_for_manufacturing)

	for item in transferred_materials:
		qty= item.qty
		item_code = item.original_item or item.item_code
		req_items = frappe.get_all('Work Order Item',
			filters={'parent': self.work_order, 'item_code': item_code},
			fields=["required_qty", "consumed_qty"]
			)
		if not req_items:
			frappe.msgprint(_("Did not found transfered item {0} in Work Order {1}, the item not added in Stock Entry")
				.format(item_code, self.work_order))
			continue

		req_qty = flt(req_items[0].required_qty)
		req_qty_each = flt(req_qty / manufacturing_qty)
		consumed_qty = flt(req_items[0].consumed_qty)

		if trans_qty and manufacturing_qty > (produced_qty + flt(self.fg_completed_qty)):
			if qty >= req_qty:
				qty = (req_qty/trans_qty) * flt(self.fg_completed_qty)
			else:
				qty = qty - consumed_qty

			if self.purpose == 'Manufacture':
				# If Material Consumption is booked, must pull only remaining components to finish product
				if consumed_qty != 0:
					remaining_qty = consumed_qty - (produced_qty * req_qty_each)
					exhaust_qty = req_qty_each * produced_qty
					if remaining_qty > exhaust_qty :
						if (remaining_qty/(req_qty_each * flt(self.fg_completed_qty))) >= 1:
							qty =0
						else:
							qty = (req_qty_each * flt(self.fg_completed_qty)) - remaining_qty
				else:
					qty = req_qty_each * flt(self.fg_completed_qty)

		elif backflushed_materials.get(item.item_code):
			for d in backflushed_materials.get(item.item_code):
				if d.get(item.warehouse):
					if (qty > req_qty):
						qty = (qty/trans_qty) * flt(self.fg_completed_qty)

					if consumed_qty:
						qty -= consumed_qty

		if cint(frappe.get_cached_value('UOM', item.stock_uom, 'must_be_whole_number')):
			qty = frappe.utils.ceil(qty)

		if qty > 0:
			self.add_to_stock_entry_detail({
				item.item_code: {
					"from_warehouse": item.warehouse,
					"to_warehouse": "",
					"qty": qty,
					"item_name": item.item_name,
					"description": item.description,
					"stock_uom": item.stock_uom,
					"expense_account": item.expense_account,
					"cost_center": item.buying_cost_center,
					"original_item": item.original_item
				}
			})

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
		#frappe.msgprint(str(item))
		if qty > 0:
			self.add_to_stock_entry_detail({
				item.item_code: {
				#	"from_warehouse": wo.wip_warehouse,
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

def get_item_details(self, args=None, for_update=False):
	item = frappe.db.sql("""select i.name, i.stock_uom, i.description, i.image, i.item_name, i.item_group,
			i.has_batch_no, i.sample_quantity, i.has_serial_no, i.allow_alternative_item,
			id.expense_account, id.buying_cost_center
		from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
		where i.name=%s
			and i.disabled=0
			and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
		(self.company, args.get('item_code'), nowdate()), as_dict = 1)

	if not item:
		frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

	item = item[0]
	item_group_defaults = get_item_group_defaults(item.name, self.company)
	brand_defaults = get_brand_defaults(item.name, self.company)

	ret = frappe._dict({
		'uom'			      	: item.stock_uom,
		'stock_uom'				: item.stock_uom,
		'description'		  	: item.description,
		'image'					: item.image,
		'item_name' 		  	: item.item_name,
		'cost_center'			: get_default_cost_center(args, item, item_group_defaults, brand_defaults, self.company),
		'qty'					: args.get("qty"),
		'transfer_qty'			: args.get('qty'),
		'conversion_factor'		: 1,
		'batch_no'				: '',
		'actual_qty'			: 0,
		'basic_rate'			: 0,
		'serial_no'				: '',
		'has_serial_no'			: item.has_serial_no,
		'has_batch_no'			: item.has_batch_no,
		'sample_quantity'		: item.sample_quantity
	})

	if self.purpose == 'Send to Subcontractor':
		ret["allow_alternative_item"] = item.allow_alternative_item

	# update uom
	if args.get("uom") and for_update:
		ret.update(get_uom_details(args.get('item_code'), args.get('uom'), args.get('qty')))
	if self.purpose == 'Material Issue' or self.purpose == "Manufacture":
		ret["expense_account"] = (item.get("expense_account") or
			item_group_defaults.get("expense_account") or
			frappe.get_cached_value('Company',  self.company,  "default_expense_account"))
	for company_field, field in {'stock_adjustment_account': 'expense_account',
		'cost_center': 'cost_center'}.items():
		if not ret.get(field):
			ret[field] = frappe.get_cached_value('Company',  self.company,  company_field)

	args['posting_date'] = self.posting_date
	args['posting_time'] = self.posting_time

	stock_and_rate = get_warehouse_details(args) if args.get('warehouse') else {}
	ret.update(stock_and_rate)

	# automatically select batch for outgoing item
	if (args.get('s_warehouse', None) and args.get('qty') and
		ret.get('has_batch_no') and not args.get('batch_no')):
		args.batch_no = get_batch_no(args['item_code'], args['s_warehouse'], args['qty'])

	if self.purpose == "Send to Subcontractor" and self.get("purchase_order") and args.get('item_code'):
		subcontract_items = frappe.get_all("Purchase Order Item Supplied",
			{"parent": self.purchase_order, "rm_item_code": args.get('item_code')}, "main_item_code")

		if subcontract_items and len(subcontract_items) == 1:
			ret["subcontracted_item"] = subcontract_items[0].main_item_code

	return ret


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



# def update_stock_ledger(self):
# 	sl_entries = []

# 	# make sl entries for source warehouse first, then do for target warehouse
# 	for d in self.get('items'):
# 		if cstr(d.s_warehouse):
# 			sl_entries.append(self.get_sl_entries(d, {
# 				"warehouse": cstr(d.s_warehouse),
# 				"actual_qty": -flt(d.transfer_qty),
# 				"incoming_rate": 0
# 			}))

# 	for d in self.get('items'):
# 		if cstr(d.t_warehouse):
# 			sl_entries.append(self.get_sl_entries(d, {
# 				"warehouse": cstr(d.t_warehouse),
# 				"actual_qty": flt(d.transfer_qty),
# 				"incoming_rate": flt(d.valuation_rate)
# 			}))

# 	# On cancellation, make stock ledger entry for
# 	# target warehouse first, to update serial no values properly

# 		# if cstr(d.s_warehouse) and self.docstatus == 2:
# 		# 	sl_entries.append(self.get_sl_entries(d, {
# 		# 		"warehouse": cstr(d.s_warehouse),
# 		# 		"actual_qty": -flt(d.transfer_qty),
# 		# 		"incoming_rate": 0
# 		# 	}))

# 	if self.docstatus == 2:
# 		sl_entries.reverse()

# 	self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')
