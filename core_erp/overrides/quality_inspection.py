import frappe

def custom_on_submit(self,method):
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

