	
from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import cint, flt, cstr,get_link_to_form,getdate
from frappe import _
import frappe.defaults
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.stock.stock_ledger import get_valuation_rate
from erpnext.stock import get_warehouse_account_map

class BatchExpiredError(frappe.ValidationError):
	pass
    
def validate_inspection_dup(self):
    '''Checks if quality inspection is set for Items that require inspection.
    On submit, throw an exception'''
    inspection_required_fieldname = None
    if self.doctype in ["Purchase Receipt", "Purchase Invoice"]:
        inspection_required_fieldname = "inspection_required_before_purchase"
    elif self.doctype in ["Delivery Note", "Sales Invoice"]:
        inspection_required_fieldname = "inspection_required_before_delivery"

    if ((not inspection_required_fieldname and self.doctype != "Stock Entry") or
        (self.doctype == "Stock Entry" and not self.inspection_required) or
        (self.doctype in ["Sales Invoice", "Purchase Invoice"] and not self.update_stock)):
            return

    for d in self.get('items'):
        qa_required = False
        if (inspection_required_fieldname and not d.quality_inspection and
            frappe.db.get_value("Item", d.item_code, inspection_required_fieldname)):
            qa_required = True
        elif self.doctype == "Stock Entry" and not d.quality_inspection and d.t_warehouse:
            qa_required = True
        if self.docstatus == 1 and d.quality_inspection:
            qa_doc = frappe.get_doc("Quality Inspection", d.quality_inspection)
            if qa_doc.docstatus != 1:
                link = frappe.utils.get_link_to_form('Quality Inspection', d.quality_inspection)
                frappe.throw(_("Quality Inspection: {0} is not submitted for the item: {1} in row {2}").format(link, d.item_code, d.idx), QualityInspectionNotSubmittedError)

            # qa_failed = any([r.status=="Rejected" for r in qa_doc.readings])
            # if qa_failed:
            #     frappe.throw(_("Row {0}: Quality Inspection rejected for item {1}")
            #         .format(d.idx, d.item_code), QualityInspectionRejectedError)
        elif qa_required :
            action = frappe.get_doc('Stock Settings').action_if_quality_inspection_is_not_submitted
            if self.doctype == "Purchase Receipt" and self.docstatus == 1:
                link = frappe.utils.get_link_to_form('Quality Inspection', d.quality_inspection)
                frappe.throw(_("Quality Inspection not submitted for the item: {0} in row {1}").format(d.item_code, d.idx))
            if self.docstatus==1 and action == 'Stop':
                frappe.throw(_("Quality Inspection required for Item {0} to submit").format(frappe.bold(d.item_code)),
                    exc=QualityInspectionRequiredError)
            else:
                frappe.msgprint(_("Create Quality Inspection for Item {0}").format(frappe.bold(d.item_code)))


def validate_serialized_batch_dup(self):
    if self.doctype == "Stock Entry":
        from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

        # is_material_issue = False
        # if self.doctype == "Stock Entry" and self.purpose == "Material Issue":
        #     is_material_issue = True

        for d in self.get("items"):
            if hasattr(d, "serial_no") and hasattr(d, "batch_no") and d.serial_no and d.batch_no:
                serial_nos = frappe.get_all(
                    "Serial No",
                    fields=["batch_no", "name", "warehouse"],
                    filters={"name": ("in", get_serial_nos(d.serial_no))},
                )

                for row in serial_nos:
                    if row.warehouse and row.batch_no != d.batch_no:
                        frappe.throw(
                            _("Row #{0}: Serial No {1} does not belong to Batch {2}").format(
                                d.idx, row.name, d.batch_no
                            )
                        )

            # if is_material_issue:
            #     continue

            if flt(d.qty) > 0.0 and d.get("batch_no") and self.get("posting_date") and self.docstatus < 2:
                expiry_date = frappe.get_cached_value("Batch", d.get("batch_no"), "expiry_date")

                if self.get("stock_entry_type")=="Material Transfer" and expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                    pass
                # elif self.get("stock_entry_type")=="Repack" and expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                #     pass
                # else:
                #     #  expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                #     # frappe.msgprint(str(self.stock_entry_type))
                #     frappe.throw(
                #         _("Row #{0}: The batch {1} has already expired.").format(
                #             d.idx, get_link_to_form("Batch", d.get("batch_no"))
                #         ),
                #         BatchExpiredError,
                #     )
    else:
        from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

        is_material_issue = False
        if self.doctype == "Stock Entry" and self.purpose == "Material Issue":
            is_material_issue = True

        for d in self.get("items"):
            if hasattr(d, "serial_no") and hasattr(d, "batch_no") and d.serial_no and d.batch_no:
                serial_nos = frappe.get_all(
                    "Serial No",
                    fields=["batch_no", "name", "warehouse"],
                    filters={"name": ("in", get_serial_nos(d.serial_no))},
                )

                for row in serial_nos:
                    if row.warehouse and row.batch_no != d.batch_no:
                        frappe.throw(
                            _("Row #{0}: Serial No {1} does not belong to Batch {2}").format(
                                d.idx, row.name, d.batch_no
                            )
                        )

            if is_material_issue:
                continue

            if flt(d.qty) > 0.0 and d.get("batch_no") and self.get("posting_date") and self.docstatus < 2:
                expiry_date = frappe.get_cached_value("Batch", d.get("batch_no"), "expiry_date")

                if expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                    frappe.throw(
                        _("Row #{0}: The batch {1} has already expired.").format(
                            d.idx, get_link_to_form("Batch", d.get("batch_no"))
                        ),
                        BatchExpiredError,
                    )


