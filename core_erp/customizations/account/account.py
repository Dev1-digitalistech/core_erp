
import frappe


def validate_root_company_and_sync_account_to_children(self):
    # ignore validation while creating new compnay or while syncing to child companies
    if (
        frappe.local.flags.ignore_root_company_validation or self.flags.ignore_root_company_validation
    ):
        return
    ancestors = get_root_company(self.company)
    if ancestors:
        if frappe.get_value("Company", self.company, "allow_account_creation_against_child_company"):
            return
        # if not frappe.db.get_value(
        #     "Account", {"account_name": self.account_name, "company": ancestors[0]}, "name"
        # ):
        #     frappe.throw(_("Please add the account to root level Company - {}").format(ancestors[0]))
    elif self.parent_account:
        descendants = get_descendants_of("Company", self.company)
        if not descendants:
            return
        parent_acc_name_map = {}
        parent_acc_name, parent_acc_number = frappe.db.get_value(
            "Account", self.parent_account, ["account_name", "account_number"]
        )
        filters = {
            "company": ["in", descendants],
            "account_name": parent_acc_name,
        }
        if parent_acc_number:
            filters["account_number"] = parent_acc_number

        for d in frappe.db.get_values(
            "Account", filters=filters, fieldname=["company", "name"], as_dict=True
        ):
            parent_acc_name_map[d["company"]] = d["name"]

        if not parent_acc_name_map:
            return

        self.create_account_for_child_company(parent_acc_name_map, descendants, parent_acc_name)
