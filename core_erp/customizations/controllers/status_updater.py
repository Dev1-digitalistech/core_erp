from __future__ import unicode_literals
import frappe
from frappe.utils import flt, comma_or, nowdate, getdate, now
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
            ref_doc_received_qty = flt(frappe.db.sql("""select ifnull(sum(received_qty), 0) from `tab%s Item`
                where parent=%s""" % (ref_dt, '%s'), (ref_dn))[0][0])

            billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0)
                from `tab%s Item` where %s=%s and docstatus=1""" %
                (self.doctype, ref_fieldname, '%s'), (ref_dn))[0][0])

            per_billed = (min(ref_doc_qty, billed_qty) / ref_doc_received_qty) * 100

            ref_doc = frappe.get_doc(ref_dt, ref_dn)

            ref_doc.db_set("per_billed", per_billed)
            ref_doc.set_status(update=True)