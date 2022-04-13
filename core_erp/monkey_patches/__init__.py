from erpnext.stock.doctype.item.item import Item
from core_erp.overrides.item import custom_autoname

Item.autoname = custom_autoname