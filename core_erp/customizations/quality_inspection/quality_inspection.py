import frappe

def on_submit(self,method):
	if not self.inspection_for_wip:
		doc = frappe.get_doc(self.reference_type,self.reference_name)
		qc = 1
		for i in doc.items:
			if i.item_code == self.item_code and i.qty == self.acc_qty:
				if self.rejected_qty:
					i.rejected_qty = i.rejected_qty + self.rejected_qty
					i.qty = i.received_qty - i.rejected_qty
					doc.total_rejected_qty = doc.total_rejected_qty + self.rejected_qty
			if not i.quality_inspection and qc == 1:
				qc = 0
		if qc ==0:
			doc.save()
		else:
			doc.submit()

def get_quality_inspection_template(self):
	template = ''
	if self.bom_no:
		template = frappe.db.get_value('BOM', self.bom_no, 'quality_inspection_template')

	if not template:
		template = frappe.db.get_value('BOM', self.item_code, 'quality_inspection_template')

	self.quality_inspection_template = template
	if not self.inspection_for_wip:
		self.get_item_specification_details()
	else:
		get_wip_reading_template(self)

def get_wip_reading_template(self):
	if not self.quality_inspection_template:
		self.quality_inspection_template=frappe.db.get_value("Item",self.item_code,"quality_inspection_template")
	if not self.quality_inspection_template: return
	self.set("readings_2",[])
	parameters=get_template_details(self.quality_inspection_template)
	for d in parameters:
		child=self.append("readings_2",{})
		child.specification=d.specification
		child.acceptance_criteria=d.value
		child.reading_type=d.reading_type
		child.exp_range=d.qty_range
		child.exp_low=d.low
		child.exp_high=d.high
		child.status="Accepted"

def get_item_specification_details(self):
	if not self.quality_inspection_template:
		self.quality_inspection_template = frappe.db.get_value('Item',
			self.item_code, 'quality_inspection_template')

	if not self.quality_inspection_template: return

	self.set('readings', [])
	parameters = get_template_details(self.quality_inspection_template)
	for d in parameters:
		child = self.append('readings', {})
		child.specification = d.specification
		child.acceptance_criteria = d.value
		child.reading_type = d.reading_type
		child.exp_range = d.qty_range
		child.exp_low = d.low
		child.exp_high = d.high
		child.status = "Accepted"

def update_qc_reference(self):
	quality_inspection = self.name if self.docstatus == 1 else ""
	doctype = self.reference_type + ' Item'
	if self.reference_type == 'Stock Entry':
		doctype = 'Stock Entry Detail'

	if self.reference_type and self.reference_name:
		frappe.db.sql("""update `tab{child_doc}` t1, `tab{parent_doc}` t2
			set t1.quality_inspection = %s, t2.modified = %s
			where t1.parent = %s and t1.item_code = %s and t1.parent = t2.name and t1.name = %s"""
			.format(parent_doc=self.reference_type, child_doc=doctype),
			(quality_inspection, self.modified, self.reference_name, self.item_code,self.row_name))

def get_template_details(template):
	if not template: return []

	return frappe.get_all('Item Quality Inspection Parameter', fields=["specification", "value","reading_type","qty_range","low","high"],
		filters={'parenttype': 'Quality Inspection Template', 'parent': template}, order_by="idx")
