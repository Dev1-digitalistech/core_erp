import frappe
from erpnext.stock.doctype.item.item import make_variant_item_code
from frappe.utils import strip


def custom_autoname(self, method = None):
    if frappe.db.get_default("item_naming_by") == "Naming Series":
        if self.variant_of:
            if not self.item_code:
                template_item_name = frappe.db.get_value(
                    "Item", self.variant_of, "item_name")
                self.item_code = make_variant_item_code(
                    self.variant_of, template_item_name, self)
        else:
            from frappe.model.naming import set_name_by_naming_series
            set_name_by_naming_series(self)
            self.item_code = self.name

    if self.item_group == 'Finished Goods':
        if not self.ig_code:
            frappe.throw("Kindly update the Group Code in Item Group")
        if not self.sub_group_code:
            frappe.throw("Kindly update the Group Code in Item Sub Group")
        if self.product_category == "Rings" and not self.promo_abbr:
            frappe.throw("Kindly select Promo code")
        self.item_code = self.ig_code + self.sub_group_code + str(self.weight_per_unit)[0:5].replace('.', '_') \
            + str(self.promo_abbr)
    else:
        if not self.ig_code:
            frappe.throw("Kindly update the Group Code in Item Group")
        if not self.sub_group_code:
            frappe.throw("Kindly update the Group Code in Item Sub Group")
        item_code = self.ig_code + self.sub_group_code
        from frappe.model.naming import make_autoname
        self.item_code = make_autoname(item_code + '.#####')
    self.item_code = strip(self.item_code)
    self.name = self.item_code
