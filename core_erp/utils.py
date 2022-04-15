import frappe

# get fiscal year in 22-23 format for naming series
def get_fiscal_abbr(date):
	yr_start, yr_end = frappe.db.get_value('Fiscal Year',{'disabled':0, 'year_start_date':['<=',date], \
						'year_end_date':['>=',date]},['year_start_date','year_end_date'])
	if not yr_start or not yr_end:
		frappe.throw("Can't find any enabled Fiscal Year for the provided date")
	
	return yr_start.strftime('%y') + '-' + yr_end.strftime('%y')