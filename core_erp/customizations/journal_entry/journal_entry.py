from frappe.utils import money_in_words

def validate(doc, method=None):
    debit = money_in_words(doc.total_debit)
    doc.custom_total_debit_in_words = debit