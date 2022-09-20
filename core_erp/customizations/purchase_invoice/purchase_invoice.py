import frappe, erpnext,datetime
from core_erp.utils import get_fiscal_abbr
from frappe import _
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import flt, get_link_to_form
from frappe.model.naming import make_autoname
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category \
    import get_tax_withholding_details, get_tax_row, get_advance_vouchers, is_valid_certificate, \
        get_ltds_amount, get_debit_note_amount

def on_submit(self,method=None):
	if self.rejected_qty:
		frappe.db.set_value("Purchase Invoice", self.return_against, "rejected_qty", 1)
	if self.short_qty:
		frappe.db.set_value("Purchase Invoice", self.return_against, "short_qty", 1)
	if not self.is_return:
		for i in self.items:
			if i.rejected_qty > 0:
				if not self.rejected_qty:
					record=frappe.db.sql_list('''select name from `tabPurchase Invoice` where return_against = %(name)s and rejected_qty = 1 
						and docstatus = 1''',{"name":self.name})
					if not record:
						frappe.throw("Kindly check Debit Note for Rejected quantity is created or not")
			if i.short_quantity > 0:
				if not self.short_qty:
					record=frappe.db.sql_list('''select name from `tabPurchase Invoice` where return_against = %(name)s and short_qty = 1
                                                       and docstatus = 1''',{"name":self.name})
					if not record:
						frappe.throw("Kindly check Debit Note for short quantity is created or not")

def autoname(self,method):	
	fiscal_yr_abbr = get_fiscal_abbr(self.posting_date)
	if self.is_return:
		self.name = make_autoname("DN/"+self.abbr+"/"+fiscal_yr_abbr+"/.#####")
	else:
		self.name = make_autoname("PI/"+self.abbr+"/"+fiscal_yr_abbr+"/.#####")

def validate(self,method):
	if self.mrn_number:
		frappe.db.set_value("Purchase Receipt", self.mrn_number,"pi",1)

def pr_required(self):
	stock_items = self.get_stock_items()
	if frappe.db.get_value("Buying Settings", None, "pr_required") == 'Yes':

		if frappe.get_value('Supplier', self.supplier, 'allow_purchase_invoice_creation_without_purchase_receipt'):
			return

		for d in self.get('items'):
			if not d.purchase_receipt and d.item_code in stock_items and not self.po_type == "Normal":
				frappe.throw(_("""Purchase Receipt Required for item {0}
					To submit the invoice without purchase receipt please set
					{1} as {2} in {3}""").format(frappe.bold(d.item_code), frappe.bold(_('Purchase Receipt Required')),
					frappe.bold('No'), get_link_to_form('Buying Settings', 'Buying Settings', 'Buying Settings')))

def set_tax_withholding(self):
	if not self.apply_tds:
		return

	tax_withholding_details = get_party_tax_withholding_details(self, self.tax_withholding_category)
	if not tax_withholding_details:
		return

	accounts = []
	for d in self.taxes:
		if d.account_head == tax_withholding_details.get("account_head"):
			d.update(tax_withholding_details)
		accounts.append(d.account_head)

	if not accounts or tax_withholding_details.get("account_head") not in accounts:
#			frappe.msgprint(str(tax_withholding_details))
		self.append("taxes", tax_withholding_details)

	to_remove = [d for d in self.taxes
		if not d.tax_amount and d.account_head == tax_withholding_details.get("account_head")]

	for d in to_remove:
		self.remove(d)
		# calculate totals again after applying TDS
	self.calculate_taxes_and_totals()

def get_party_tax_withholding_details(ref_doc, tax_withholding_category=None):

	pan_no = ''
	suppliers = []

	if not tax_withholding_category:
		tax_withholding_category, pan_no = frappe.db.get_value('Supplier', ref_doc.supplier, ['tax_withholding_category', 'pan'])

	if not tax_withholding_category:
		return

	if not pan_no:
		pan_no = frappe.db.get_value('Supplier', ref_doc.supplier, 'pan')

	# Get others suppliers with the same PAN No
	if pan_no:
		suppliers = [d.name for d in  frappe.get_all('Supplier', fields=['name'], filters={'pan': pan_no})]

	if not suppliers:
		suppliers.append(ref_doc.supplier)

	fy = get_fiscal_year(ref_doc.posting_date, company=ref_doc.company)
	tax_details = get_tax_withholding_details(tax_withholding_category, fy[0], ref_doc.company)
	if not tax_details:
		frappe.throw(_('Please set associated account in Tax Withholding Category {0} against Company {1}')
			.format(tax_withholding_category, ref_doc.company))

	tds_amount = get_tds_amount(suppliers, ref_doc.net_total, ref_doc.company,
		tax_details, fy,  ref_doc.posting_date, pan_no)

	tax_row = get_tax_row(tax_details, tds_amount)

	return tax_row

def get_tds_amount(suppliers, net_total, company, tax_details, fiscal_year_details, posting_date, pan_no=None):
	fiscal_year, year_start_date, year_end_date = fiscal_year_details
	if fiscal_year == "2021-22":
		year_start_date = "2021-12-01"
	tds_amount = 0
	tds_deducted = 0

	def _get_tds(amount, rate):
#		if amount <= 0:
#			return 0
		frappe.msgprint(str(amount))
		return amount * rate / 100

	ldc_name = frappe.db.get_value('Lower Deduction Certificate',
		{
			'pan_no': pan_no,
			'fiscal_year': fiscal_year
		}, 'name')
	ldc = ''

	if ldc_name:
		ldc = frappe.get_doc('Lower Deduction Certificate', ldc_name)
	if net_total >= 0:
		entries = frappe.db.sql("""
			select voucher_no, credit
			from `tabGL Entry`
			where company = %s and
			party in %s and fiscal_year=%s and posting_date between %s and %s and credit > 0
			and is_opening = 'No'
		""", (company, tuple(suppliers), fiscal_year,year_start_date, year_end_date), as_dict=1)
#		""", (company, tuple(suppliers), fiscal_year), as_dict=1)
	else:
		entries = frappe.db.sql("""

                       select voucher_no, credit

                       from `tabGL Entry`

                       where company = %s and

                       party in %s and fiscal_year=%s and credit > 0

                       and is_opening = 'No'

               """, (company, tuple(suppliers), fiscal_year), as_dict=1)

	vouchers = [d.voucher_no for d in entries]
	advance_vouchers = get_advance_vouchers(suppliers, fiscal_year=fiscal_year, company=company)

	tds_vouchers = vouchers + advance_vouchers

	if tds_vouchers:
		tds_deducted = frappe.db.sql("""
			SELECT sum(credit) FROM `tabGL Entry`
			WHERE
				account=%s and fiscal_year=%s and credit > 0
				and voucher_no in ({0})""". format(','.join(['%s'] * len(tds_vouchers))),
				((tax_details.account_head, fiscal_year) + tuple(tds_vouchers)))

		tds_deducted = tds_deducted[0][0] if tds_deducted and tds_deducted[0][0] else 0

	if tds_deducted:
		if ldc:
			limit_consumed = frappe.db.get_value('Purchase Invoice',
				{
					'supplier': ('in', suppliers),
					'apply_tds': 1,
					'docstatus': 1
				}, 'sum(net_total)')

		if ldc and is_valid_certificate(ldc.valid_from, ldc.valid_upto, posting_date, limit_consumed, net_total,
			ldc.certificate_limit):

			tds_amount = get_ltds_amount(net_total, limit_consumed, ldc.certificate_limit, ldc.rate, tax_details)
		else:
			tds_amount = _get_tds(net_total, tax_details.rate)
	else:
		supplier_credit_amount = frappe.get_all('Purchase Invoice',
			fields = ['sum(net_total)'],
			filters = {'name': ('in', vouchers), 'docstatus': 1, "apply_tds": 1}, as_list=1)

		supplier_credit_amount = (supplier_credit_amount[0][0]
			if supplier_credit_amount and supplier_credit_amount[0][0] else 0)

		jv_supplier_credit_amt = frappe.get_all('Journal Entry Account',
			fields = ['sum(credit_in_account_currency)'],
			filters = {
				'parent': ('in', vouchers), 'docstatus': 1,
				'party': ('in', suppliers),
				'reference_type': ('not in', ['Purchase Invoice'])
			}, as_list=1)

		supplier_credit_amount += (jv_supplier_credit_amt[0][0]
			if jv_supplier_credit_amt and jv_supplier_credit_amt[0][0] else 0)

		supplier_credit_amount += net_total

		debit_note_amount = get_debit_note_amount(suppliers, year_start_date, year_end_date)
		supplier_credit_amount -= debit_note_amount
		if ((tax_details.get('threshold', 0) and supplier_credit_amount >= tax_details.threshold)
			or (tax_details.get('cumulative_threshold', 0) and supplier_credit_amount >= tax_details.cumulative_threshold)):

			if ldc and is_valid_certificate(ldc.valid_from, ldc.valid_upto, posting_date, tds_deducted, net_total,
				ldc.certificate_limit):
				tds_amount = get_ltds_amount(supplier_credit_amount, 0, ldc.certificate_limit, ldc.rate,
					tax_details)
			else:
				tds_amount = _get_tds(supplier_credit_amount, tax_details.rate)
		elif (tax_details.get('threshold', 0) and supplier_credit_amount <= tax_details.threshold):
			tds_amount = _get_tds(supplier_credit_amount, tax_details.rate)

	return tds_amount

@frappe.whitelist()
def make_debit_note(source_name, target_doc=None):
	#from erpnext.controllers.sales_and_purchase_return import make_return_doc
	return make_return_doc("Purchase Invoice", source_name, target_doc)


@frappe.whitelist()
def make_debit_note_for_reject(source_name, target_doc=None):
	#from erpnext.controllers.sales_and_purchase_return import make_return_doc_for_reject
	return make_return_doc_for_reject("Purchase Invoice", source_name, target_doc)

@frappe.whitelist()
def make_debit_note_for_shortqty(source_name, target_doc=None):
	#from erpnext.controllers.sales_and_purchase_return import make_return_doc_for_shortqty
	return make_return_doc_for_shortqty("Purchase Invoice", source_name, target_doc)

@frappe.whitelist(allow_guest=True)
def tally_integration():
	data_list=[]
	today_date=datetime.date.today()
	#today_date = getdate('2022-01-20')
	prev_date=datetime.date.today()-datetime.timedelta(days=25)
	#prev_date = getdate('2022-01-01')
#	all_data=frappe.db.sql('''select * from `tabPurchase Invoice` where docstatus=1 and posting_date between %s and 
#		%s'''%(frappe.db.escape(prev_date),frappe.db.escape(today_date)),as_dict=1)
	all_data = frappe.db.sql('''select distinct pi.* from `tabPurchase Invoice` as pi,`tabPurchase Invoice Item` as pii where pi.docstatus =1 
		and pii.item_group in ('Raw Material','Packaging Material','Gift Material') and pi.name = pii.parent 
		and posting_date between %s and 
               %s'''%(frappe.db.escape(prev_date),frappe.db.escape(today_date)),as_dict=1)
	#all_data=frappe.get_all("Purchase Invoice",filters={'docstatus':1,'posting_date':['>','2021-03-31']},fields=['*'])
	for data in all_data:
		payload={}
		payload['company_name']=data.company
		payload['invoice_no']=data.name
		payload['invoice_date']=data.posting_date
		payload['supplier_name']=data.supplier
		payload['supplier_tally_name']=frappe.db.get_value("Supplier",data.supplier,'name_in_tally')
		payload['supplier_address']=data.address_display
		doc=frappe.db.get_value("Address",data.supplier_address,['state','gstin'],as_dict=1)
		if doc:
			payload['supplier_state']=doc.state
			payload['supplier_gstin']=doc.gstin
		payload['supplier_invoice_no']=data.bill_no
		payload['supplier_invoice_date']=data.bill_date
		payload['invoice_amount']=data.net_total
		if data.is_return==1:
			payload['is_debit_note']=True
		else:
			payload['is_debit_note']=False
		payload['tax_category']=data.tax_category
		payload['narration']=data.narration
		doc=frappe.get_doc("Purchase Invoice",data.name)
		item_ledger_list=[]
		gst_list=[]
		for item in doc.items:
			item_purchase_head=frappe.get_all("Item Default",filters={"parent":item.item_code,"company":data.company},fields={'purchase_head'})
			item_ledger={}
			#item_ledger['ledger_name']=item.expense_account
			item_ledger['amount']=round(float(item.amount_s),2)
			frappe.log_error(item_purchase_head,'item purch head')
			if item_purchase_head:
				frappe.log_error(item_purchase_head,'iph if')
				item_ledger['ledger_name']=item_purchase_head[0]['purchase_head']
			else:
				purchase_head_grp=frappe.get_all("Item Default",filters={"parent":item.item_group,"company":data.company},fields={'purchase_head'})
				if purchase_head_grp:
					item_ledger['ledger_name']=purchase_head_grp[0]['purchase_head']
			item_ledger_list.append(item_ledger)
		payload['item_ledger_list']=item_ledger_list
		tax_ledger1={}
		tax_ledger2={}
		tax_ledger3={}
		tax_ledger4={}
		tax_ledger5={}
		tax_ledger6={}
		for row in doc.taxes:
			if row.tax_amount:
				if "IGST" in row.account_head:
					try:
						if tax_ledger1['gl_name']:
							tax_ledger1['amount']+=float(row.tax_amount)
					except:
						tax_ledger1['gl_name']=row.tally_ledger_head
						tax_ledger1['amount']=float(row.tax_amount)
					tax_ledger1['has_debit']=True if row.add_deduct_tax=="Add" and not data.is_return==1 else False
				elif "CGST" in row.account_head:
					try:
						if tax_ledger2['gl_name']:
							tax_ledger2['amount']+=float(row.tax_amount)
					except:
						tax_ledger2['gl_name']=row.tally_ledger_head
						tax_ledger2['amount']=float(row.tax_amount)
					tax_ledger2['has_debit']=True if row.add_deduct_tax=="Add" and not data.is_return==1 else False
				elif "SGST" in row.account_head:
					try:
						if tax_ledger3['gl_name']:
							tax_ledger3['amount']+=float(row.tax_amount)
					except:
						tax_ledger3['gl_name']=row.tally_ledger_head
						tax_ledger3['amount']=float(row.tax_amount)
					tax_ledger3['has_debit']=True if row.add_deduct_tax=="Add" and not data.is_return==1 else False
				elif "TCS" in row.account_head:
					try:
						if tax_ledger4['gl_name']:
							tax_ledger4['amount']+=float(row.tax_amount)
					except:
						if row.tally_ledger_head:
							tax_ledger4['gl_name']=row.tally_ledger_head
						else:
							tax_ledger4['gl_name']=row.account_head
						tax_ledger4['amount']=float(row.tax_amount)
					tax_ledger4['has_debit']=True if row.add_deduct_tax=="Add" and not data.is_return==1 else False
				elif "TDS" in row.account_head:
					try:
						if tax_ledger5['gl_name']:
							tax_ledger5['amount']+=float(row.tax_amount)
					except:
						if row.tally_ledger_head:
							tax_ledger5['gl_name']=row.tally_ledger_head
						else:
							tax_ledger5['gl_name']=row.account_head
						tax_ledger5['amount']=float(row.tax_amount)
					tax_ledger5['has_debit']=True if data.is_return==1 else False
		if tax_ledger1:
			gst_list.append(tax_ledger1)
		if tax_ledger2:
			gst_list.append(tax_ledger2)
		if tax_ledger3:
			gst_list.append(tax_ledger3)
		if tax_ledger4:
			gst_list.append(tax_ledger4)
		if tax_ledger5:
			gst_list.append(tax_ledger5)
		tax_ledger6['gl_name']="round_off"
		tax_ledger6['amount']=round(float(data.rounded_total)-float(data.total_taxes_and_charges)-float(data.net_total),2)
		gst_list.append(tax_ledger6)
		payload['other_charges']=gst_list
		payload['total_gst_amount']=data.total_taxes_and_charges
		payload['grand_total']=data.rounded_total
		data_list.append(payload)
	return data_list

@frappe.whitelist(allow_guest=True)
def tally_new_integration():
	data_list=[]
	all_data=frappe.get_all("Purchase Invoice",filters={'docstatus':1,'posting_date':['>','2021-03-31']},fields=['*'])
	for data in all_data:
		payload={}
		payload['company_name']=data.company
		payload['invoice_no']=data.name
		payload['invoice_date']=data.posting_date
		payload['supplier_name']=data.supplier
		payload['supplier_tally_name']=data.supplier_tally_name
		payload['supplier_address']=data.address_display
		doc=frappe.db.get_value("Address",data.supplier_address,['state','gstin'],as_dict=1)
		if doc:
			payload['supplier_state']=doc.state
			payload['supplier_gstin']=doc.gstin
		payload['supplier_invoice_no']=data.bill_no
		payload['supplier_invoice_date']=data.bill_date
		payload['invoice_amount']=data.net_total
		if data.is_return==1:
			payload['is_debit_note']=True
		else:
			payload['is_debit_note']=False
		payload['tax_category']=data.tax_category
		payload['narration']=data.narration
		doc=frappe.get_doc("Purchase Invoice",data.name)
		item_ledger_list=[]
		gst_list=[]
		for item in doc.items:
			item_ledger={}
			item_ledger['ledger_name']=item.expense_account
			item_ledger['amount']=item.amount_s
			item_ledger_list.append(item_ledger)
		payload['item_ledger_list']=item_ledger_list
		tax_ledger1={}
		tax_ledger2={}
		tax_ledger3={}
		tax_ledger4={}
		tax_ledger5={}
		tax_ledger6={}
		for row in doc.taxes:
			if row.tax_amount:
				if "IGST" in row.account_head:
					try:
						if tax_ledger1['gl_name']:
							tax_ledger1['amount']+=float(row.tax_amount)
					except:
						tax_ledger1['gl_name']=row.tally_ledger_head
						tax_ledger1['amount']=float(row.tax_amount)
					tax_ledger1['has_debit']=True if row.add_deduct_tax=="Add" else False
				elif "CGST" in row.account_head:
					try:
						if tax_ledger2['gl_name']:
							tax_ledger2['amount']+=float(row.tax_amount)
					except:
						tax_ledger2['gl_name']=row.tally_ledger_head
						tax_ledger2['amount']=float(row.tax_amount)
					tax_ledger2['has_debit']=True if row.add_deduct_tax=="Add" else False
				elif "SGST" in row.account_head:
					try:
						if tax_ledger3['gl_name']:
							tax_ledger3['amount']+=float(row.tax_amount)
					except:
						tax_ledger3['gl_name']=row.tally_ledger_head
						tax_ledger3['amount']=float(row.tax_amount)
					tax_ledger3['has_debit']=True if row.add_deduct_tax=="Add" else False
				elif "TCS" in row.account_head:
					try:
						if tax_ledger4['gl_name']:
							tax_ledger4['amount']+=(int(row.tax_amount*100)/100)
					except:
						if row.tally_ledger_head:
							tax_ledger4['gl_name']=row.tally_ledger_head
						else:
							tax_ledger4['gl_name']=row.account_head
						
						tax_ledger4['amount']=(int(row.tax_amount*100)/100)
					tax_ledger4['has_debit']=True if row.add_deduct_tax=="Add" else False
				elif "TDS" in row.account_head:
					try:
						if tax_ledger5['gl_name']:
							tax_ledger5['amount']+=(int(row.tax_amount*100)/100)
					except:
						if row.tally_ledger_head:
							tax_ledger5['gl_name']=row.tally_ledger_head
						else:
							tax_ledger5['gl_name']=row.account_head
						tax_ledger5['amount']=(int(row.tax_amount*100)/100)
					tax_ledger5['has_debit']=True if row.add_deduct_tax=="Add" else False
		if tax_ledger1:
			gst_list.append(tax_ledger1)
		if tax_ledger2:
			gst_list.append(tax_ledger2)
		if tax_ledger3:
			gst_list.append(tax_ledger3)
		if tax_ledger4:
			gst_list.append(tax_ledger4)
		if tax_ledger5:
			gst_list.append(tax_ledger5)
		tax_ledger6['gl_name']="round_off"
		tax_ledger6['amount']=round(float(data.rounded_total)-float(data.total_taxes_and_charges)-float(data.net_total),2)
		gst_list.append(tax_ledger6)
		payload['other_charges']=gst_list
		payload['total_gst_amount']=data.total_taxes_and_charges
		payload['grand_total']=data.rounded_total
		data_list.append(payload)
	return data_list

def make_return_doc(doctype, source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	company = frappe.db.get_value("Delivery Note", source_name, "company")
	pr_company = frappe.db.get_value("Purchase Receipt", source_name, "company")
	default_warehouse_for_sales_return = frappe.db.get_value("Company", company, "default_warehouse_for_sales_return")
	set_warehouse = frappe.db.get_value("Company", pr_company, "default_warehouse_for_sales_return")
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		doc.is_return = 1
		doc.return_against = source.name
		doc.ignore_pricing_rule = 1
#		doc.set_warehouse = ""
		doc.narration = ""
		doc.set_warehouse = set_warehouse
		if doctype == "Sales Invoice":
			doc.is_pos = source.is_pos

			# look for Print Heading "Credit Note"
			if not doc.select_print_heading:
				doc.select_print_heading = frappe.db.get_value("Print Heading", _("Credit Note"))

		elif doctype == "Purchase Invoice":
			# look for Print Heading "Debit Note"
			doc.select_print_heading = frappe.db.get_value("Print Heading", _("Debit Note"))

		for tax in doc.get("taxes"):
			if tax.charge_type == "Actual":
				tax.tax_amount = -1 * tax.tax_amount

		if doc.get("is_return"):
			if doc.doctype == 'Sales Invoice':
				doc.set('payments', [])
				for data in source.payments:
					paid_amount = 0.00
					base_paid_amount = 0.00
					data.base_amount = flt(data.amount*source.conversion_rate, source.precision("base_paid_amount"))
					paid_amount += data.amount
					base_paid_amount += data.base_amount
					doc.append('payments', {
						'mode_of_payment': data.mode_of_payment,
						'type': data.type,
						'amount': -1 * paid_amount,
						'base_amount': -1 * base_paid_amount
					})
			elif doc.doctype == 'Purchase Invoice':
				doc.paid_amount = -1 * source.paid_amount
				doc.base_paid_amount = -1 * source.base_paid_amount
				doc.payment_terms_template = ''
				doc.payment_schedule = []

		if doc.get("is_return") and hasattr(doc, "packed_items"):
			for d in doc.get("packed_items"):
				d.qty = d.qty * -1

		doc.discount_amount = -1 * source.discount_amount
		doc.run_method("calculate_taxes_and_totals")

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = -1* source_doc.qty
		if doctype == "Purchase Receipt":
#			target_doc.received_qty = -1* source_doc.received_qty
#			target_doc.rejected_qty = -1* source_doc.rejected_qty
			target_doc.received_qty = -1* source_doc.rejected_qty
			target_doc.rejected_qty = 0
			target_doc.short_quantity = 0
			target_doc.po_qty = 0
			target_doc.invoice_quantity = 0
			target_doc.rate_s= 0
#			target_doc.qty = -1* source_doc.qty
			target_doc.qty = -1* source_doc.rejected_qty
			target_doc.stock_qty = -1 * source_doc.stock_qty
			target_doc.purchase_order = source_doc.purchase_order
			target_doc.purchase_order_item = source_doc.purchase_order_item
			target_doc.warehouse = set_warehouse
			target_doc.rejected_warehouse = source_doc.rejected_warehouse
			target_doc.purchase_receipt_item = source_doc.name

		elif doctype == "Purchase Invoice":
			target_doc.received_qty = -1* source_doc.received_qty
			target_doc.rejected_qty = -1* source_doc.rejected_qty
			target_doc.rate_s = source_doc.rate - source_doc.rate_s
			target_doc.amount_s = source_doc.invoice_quantity * target_doc.rate_s
			target_doc.short_quantity = 0
			target_doc.qty = -1* source_doc.qty
			target_doc.stock_qty = -1 * source_doc.stock_qty
			target_doc.purchase_order = source_doc.purchase_order
			target_doc.purchase_receipt = source_doc.purchase_receipt
			target_doc.rejected_warehouse = source_doc.rejected_warehouse
			target_doc.po_detail = source_doc.po_detail
			target_doc.pr_detail = source_doc.pr_detail
			target_doc.purchase_invoice_item = source_doc.name

		elif doctype == "Delivery Note":
			target_doc.against_sales_order = source_doc.against_sales_order
			target_doc.against_sales_invoice = source_doc.against_sales_invoice
			target_doc.so_detail = source_doc.so_detail
			target_doc.si_detail = source_doc.si_detail
			target_doc.expense_account = source_doc.expense_account
			target_doc.dn_detail = source_doc.name
			if default_warehouse_for_sales_return:
				target_doc.warehouse = default_warehouse_for_sales_return

		elif doctype == "Sales Invoice":
			target_doc.sales_order = source_doc.sales_order
			target_doc.delivery_note = source_doc.delivery_note
			target_doc.so_detail = source_doc.so_detail
			target_doc.dn_detail = source_doc.dn_detail
			target_doc.expense_account = source_doc.expense_account
			target_doc.sales_invoice_item = source_doc.name
			if default_warehouse_for_sales_return:
				target_doc.warehouse = default_warehouse_for_sales_return

	def update_terms(source_doc, target_doc, source_parent):
		target_doc.payment_amount = -source_doc.payment_amount

	if doctype == "Purchase Invoice":
		doclist = get_mapped_doc(doctype, source_name,	{
			doctype: {
			"doctype": doctype,

			"validation": {
				"docstatus": ["=", 0],
			}
		},
		doctype +" Item": {
			"doctype": doctype + " Item",
			"field_map": {
				"serial_no": "serial_no",
				"batch_no": "batch_no"
			},
			"postprocess": update_item
		}
#		"Payment Schedule": {
#			"doctype": "Payment Schedule",
#			"postprocess": update_terms
#		}
	}, target_doc, set_missing_values)
	else:
		doclist = get_mapped_doc(doctype, source_name,	{
		doctype: {
			"doctype": doctype,

			"validation": {
				"docstatus": ["=", 1],
			}
		},
		doctype +" Item": {
			"doctype": doctype + " Item",
			"field_map": {
				"serial_no": "serial_no",
				"batch_no": "batch_no"
			},
			"postprocess": update_item
		},
		"Payment Schedule": {
			"doctype": "Payment Schedule",
			"postprocess": update_terms
		}
	}, target_doc, set_missing_values)

	return doclist

def make_return_doc_for_reject(doctype, source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	company = frappe.db.get_value("Delivery Note", source_name, "company")
	default_warehouse_for_sales_return = frappe.db.get_value("Company", company, "default_warehouse_for_sales_return")
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		doc.is_return = 1
		doc.rejected_qty = 1
		doc.return_against = source.name
		doc.ignore_pricing_rule = 1
		doc.set_warehouse = ""
		doc.narration = ""
		doc.bill_date = source.bill_date
		if doctype == "Sales Invoice":
			doc.is_pos = source.is_pos

                        # look for Print Heading "Credit Note"
			if not doc.select_print_heading:
				doc.select_print_heading = frappe.db.get_value("Print Heading", _("Credit Note"))

		elif doctype == "Purchase Invoice":
                        # look for Print Heading "Debit Note"
			doc.select_print_heading = frappe.db.get_value("Print Heading", _("Debit Note"))

		for tax in doc.get("taxes"):
			if tax.charge_type == "Actual":
				tax.tax_amount = -1 * tax.tax_amount

		if doc.get("is_return"):
			if doc.doctype == 'Purchase Invoice':
				doc.paid_amount = -1 * source.paid_amount
				doc.base_paid_amount = -1 * source.base_paid_amount

		if doc.get("is_return") and hasattr(doc, "packed_items"):
			for d in doc.get("packed_items"):
				d.qty = d.qty * -1

		doc.discount_amount = -1 * source.discount_amount
		doc.run_method("calculate_taxes_and_totals")

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = -1* source_doc.qty
		if doctype == "Purchase Invoice":
			target_doc.invoice_quantity = -1 * source_doc.rejected_qty
			target_doc.received_qty = -1* source_doc.rejected_qty
			target_doc.rejected_qty = -1* source_doc.rejected_qty
			target_doc.short_quantity = 0
			target_doc.qty = -1* source_doc.rejected_qty
			target_doc.stock_qty = -1 * source_doc.stock_qty
			target_doc.purchase_order = source_doc.purchase_order
			target_doc.purchase_receipt = source_doc.purchase_receipt
			target_doc.rejected_warehouse = source_doc.rejected_warehouse
			target_doc.po_detail = source_doc.po_detail
			target_doc.pr_detail = source_doc.pr_detail

	def update_terms(source_doc, target_doc, source_parent):
		target_doc.payment_amount = -source_doc.payment_amount
		target_doc.outstanding_amount = -source_doc.payment_amount

	doclist = get_mapped_doc(doctype, source_name,  {
                doctype: {
                        "doctype": doctype,

                        "validation": {
                                "docstatus": ["=", 0],
                        }
                },
                doctype +" Item": {
                        "doctype": doctype + " Item",
                        "field_map": {
                                "serial_no": "serial_no",
                                "batch_no": "batch_no"
                        },
                        "postprocess": update_item
                }
        }, target_doc, set_missing_values)

	return doclist

def make_return_doc_for_shortqty(doctype, source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	company = frappe.db.get_value("Delivery Note", source_name, "company")
	default_warehouse_for_sales_return = frappe.db.get_value("Company", company, "default_warehouse_for_sales_return")
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		doc.is_return = 1
		doc.short_qty = 1
		doc.return_against = source.name
		doc.ignore_pricing_rule = 1
		doc.set_warehouse = ""
		doc.narration = ""
		doc.bill_date = source.bill_date
#               doc.outstanding_amount = source.rounded_total
		if doctype == "Sales Invoice":
			doc.is_pos = source.is_pos

                        # look for Print Heading "Credit Note"
			if not doc.select_print_heading:
				doc.select_print_heading = frappe.db.get_value("Print Heading", _("Credit Note"))

		elif doctype == "Purchase Invoice":
                        # look for Print Heading "Debit Note"
			doc.select_print_heading = frappe.db.get_value("Print Heading", _("Debit Note"))

		for tax in doc.get("taxes"):
			if tax.charge_type == "Actual":
				tax.tax_amount = -1 * tax.tax_amount

#               if doc.get("is_return"):
#                       if doc.doctype == 'Purchase Invoice':
#                               doc.paid_amount = -1 * source.paid_amount
#                               doc.base_paid_amount = -1 * source.base_paid_amount

		if doc.get("is_return") and hasattr(doc, "packed_items"):
			for d in doc.get("packed_items"):
				d.qty = d.qty * -1

		doc.discount_amount = -1 * source.discount_amount
		doc.run_method("calculate_taxes_and_totals")

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = -1* source_doc.qty
		if doctype == "Purchase Invoice":
			target_doc.invoice_quantity = -1 * source_doc.short_quantity
			target_doc.received_qty = -1* source_doc.short_quantity
			target_doc.rejected_qty = 0
			target_doc.qty = -1* source_doc.short_quantity
			target_doc.stock_qty = -1 * source_doc.stock_qty
			target_doc.purchase_order = source_doc.purchase_order
			target_doc.purchase_receipt = source_doc.purchase_receipt
			target_doc.rejected_warehouse = source_doc.rejected_warehouse
			target_doc.po_detail = source_doc.po_detail
			target_doc.pr_detail = source_doc.pr_detail

	def update_terms(source_doc, target_doc, source_parent):
		target_doc.payment_amount = -source_doc.payment_amount
		target_doc.outstanding_amount = -source_doc.payment_amount
	doclist = get_mapped_doc(doctype, source_name,  {
                doctype: {
                        "doctype": doctype,

                        "validation": {
                                "docstatus": ["=", 0],
                        }
                },
                doctype +" Item": {
                        "doctype": doctype + " Item",
                        "field_map": {
                                "serial_no": "serial_no",
                                "batch_no": "batch_no"
                        },
                        "postprocess": update_item
                }
        }, target_doc, set_missing_values)

	return doclist
