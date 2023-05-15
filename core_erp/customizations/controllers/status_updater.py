from __future__ import unicode_literals
import frappe
from frappe.utils import flt, comma_or, nowdate, getdate, now, get_link_to_form
from frappe import _
from frappe.model.document import Document


def update_billing_status_dup(self, zero_amount_refdoc, ref_dt, ref_fieldname):
    frappe.msgprint(str(ref_dt))
    if ref_dt=='Purchase Receipt':
        for ref_dn in zero_amount_refdoc:
            ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tab%s Item`
                where parent=%s""" % (ref_dt, '%s'), (ref_dn))[0][0])
            ref_doc_received_qty = flt(frappe.db.sql("""select ifnull(sum(received_qty), 0) from `tab%s Item`
                where parent=%s""" % (ref_dt, '%s'), (ref_dn))[0][0])

            billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0)
                from `tab%s Item` where %s=%s and docstatus=1""" %
                (self.doctype, ref_fieldname, '%s'), (ref_dn))[0][0])

            per_billed = (min(ref_doc_qty, billed_qty) / ref_doc_received_qty) * 100

            ref_doc = frappe.get_doc(ref_dt, ref_dn)

            ref_doc.db_set("per_billed", per_billed)
            ref_doc.set_status(update=True)
    else:
        for ref_dn in zero_amount_refdoc:
            ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tab%s Item`
                where parent=%s""" % (ref_dt, '%s'), (ref_dn))[0][0])

            billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0)
                from `tab%s Item` where %s=%s and docstatus=1""" %
                (self.doctype, ref_fieldname, '%s'), (ref_dn))[0][0])

            per_billed = (min(ref_doc_qty, billed_qty) / ref_doc_qty) * 100

            ref_doc = frappe.get_doc(ref_dt, ref_dn)

            ref_doc.db_set("per_billed", per_billed)
            ref_doc.set_status(update=True)


def update_prevdoc_status(self):
	if self.doctype == "Purchase Receipt":
		return
	self.update_qty()
	self.validate_qty()


def validate_serialized_batch_dup(self):
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

            if self.get("doctype")=="Stock Entry" and self.get("stock_entry_type")=="Material Transfer" and expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                pass
            else:
                #  expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                frappe.msgprint(str(self.stock_entry_type))
                frappe.throw(
                    _("Row #{0}: The batch {1} has already expired.").format(
                        d.idx, get_link_to_form("Batch", d.get("batch_no"))
                    ),
                    # BatchExpiredError,
                )