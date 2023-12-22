import frappe
from core_erp.customizations.purchase_receipt.purchase_receipt import create_custom_gl_entries

def on_submit(self, method=False):
	job_name = "repost_accounting_ledger_CUSTOM_" + self.name
	frappe.enqueue(
		method="core_erp.customizations.report_accounting_ledger.report_accounting_ledger.start_custom_repost",
		account_repost_doc=self.name,
		is_async=True,
		job_name=job_name,
	)
	frappe.msgprint("Custom Patches Repost has started in the background")

@frappe.whitelist()
def start_custom_repost(account_repost_doc=str):
	if account_repost_doc:
		repost_doc = frappe.get_doc("Repost Accounting Ledger", account_repost_doc)
		if repost_doc.docstatus == 1:
			for x in repost_doc.vouchers:
				if x.voucher_type == "Purchase Receipt":
					doc = frappe.get_doc(x.voucher_type, x.voucher_no)
					create_custom_gl_entries(doc)
				frappe.db.commit()
