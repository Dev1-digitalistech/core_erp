import frappe
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions

from erpnext.accounts.doctype.budget.budget import get_item_details
def budget_autoname(self):
    pass

def validate_accounts(self):
		account_list = []
		for d in self.get('accounts'):
			if d.account:
				account_details = frappe.db.get_value("Account", d.account,
					["is_group", "company", "report_type"], as_dict=1)

				if account_details.is_group:
					frappe.throw(_("Budget cannot be assigned against Group Account {0}").format(d.account))
				elif account_details.company != self.company:
					frappe.throw(_("Account {0} does not belongs to company {1}")
						.format(d.account, self.company))
#				elif account_details.report_type != "Profit and Loss":
#					frappe.throw(_("Budget cannot be assigned against {0}, as it's not an Income or Expense account")
#						.format(d.account))

				if d.account in account_list:
					frappe.throw(_("Account {0} has been entered multiple times").format(d.account))
				else:
					account_list.append(d.account)

def validate_expense_against_budget(args):
	args = frappe._dict(args)

	if args.get('company') and not args.fiscal_year:
		args.fiscal_year = get_fiscal_year(args.get('posting_date'), company=args.get('company'))[0]
		frappe.flags.exception_approver_role = frappe.get_cached_value('Company',
			args.get('company'),  'exception_budget_approver_role')

	if not args.account:
		args.account = args.get("expense_account")

	if not (args.get('account') and args.get('cost_center')) and args.item_code:
		args.cost_center, args.account = get_item_details(args)

	if not args.account:
		return

	for budget_against in ['project', 'cost_center'] + get_accounting_dimensions():
		if (args.get(budget_against) and args.account):
#				and frappe.db.get_value("Account", {"name": args.account, "root_type": "Expense"})):

			doctype = frappe.unscrub(budget_against)

			if frappe.get_cached_value('DocType', doctype, 'is_tree'):
				lft, rgt = frappe.db.get_value(doctype, args.get(budget_against), ["lft", "rgt"])
				condition = """and exists(select name from `tab%s`
					where lft<=%s and rgt>=%s and name=b.%s)""" % (doctype, lft, rgt, budget_against) #nosec
				args.is_tree = True
			else:
				condition = "and b.%s=%s" % (budget_against, frappe.db.escape(args.get(budget_against)))
				args.is_tree = False

			args.budget_against_field = budget_against
			args.budget_against_doctype = doctype

			budget_records = frappe.db.sql("""
				select
					b.{budget_against_field} as budget_against, ba.budget_amount, b.monthly_distribution,
					ifnull(b.applicable_on_material_request, 0) as for_material_request,
					ifnull(applicable_on_purchase_order, 0) as for_purchase_order,
					ifnull(applicable_on_booking_actual_expenses,0) as for_actual_expenses,
					b.action_if_annual_budget_exceeded, b.action_if_accumulated_monthly_budget_exceeded,
					b.action_if_annual_budget_exceeded_on_mr, b.action_if_accumulated_monthly_budget_exceeded_on_mr,
					b.action_if_annual_budget_exceeded_on_po, b.action_if_accumulated_monthly_budget_exceeded_on_po
				from
					`tabBudget` b, `tabBudget Account` ba
				where
					b.name=ba.parent and b.fiscal_year=%s
					and ba.account=%s and b.docstatus=1
					{condition}
			""".format(condition=condition, budget_against_field=budget_against), (args.fiscal_year, args.account), as_dict=True) #nosec

			if budget_records:
				validate_budget_records(args, budget_records)
