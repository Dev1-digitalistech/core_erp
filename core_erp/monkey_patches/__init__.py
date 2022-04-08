from erpnext.stock.doctype.item.item import Item
from core_erp.dfm_foods_customization.overrides.item import custom_autoname

Item.autoname = custom_autoname