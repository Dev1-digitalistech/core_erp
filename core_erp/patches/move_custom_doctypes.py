import frappe


def execute():
    for dt in [
        "account_subtype",
        "delivery_days",
        "po_type",
        "product_category",
        "product_line",
        "product_variants_for_ticket",
        "ticket_type",
        "category",
        "gate_entry",
        "item_sub_group",
        "price_category",
        "product_for_ticket",
        "product_variant",
        "promo_code",
        "sub_category",
    ]:
        frappe.delete_doc('Doctype', dt, ignore_missing=True, force=True)
