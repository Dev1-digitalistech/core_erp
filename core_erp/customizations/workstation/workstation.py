import frappe

def autoname(doc, method = None):
	if doc.workstation_name and doc.abbr:
		doc.name = str(doc.workstation_name) + '-' + str(doc.abbr)
	else:
		frappe.throw("Workstation Name or Company Abbreviation is missing.")