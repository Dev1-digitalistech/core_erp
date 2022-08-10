
__version__ = '0.0.1'

app_name = "core_erp"

import frappe
import os

patches_loaded = False

def load_monkey_patches():
    global patches_loaded

    if (
        patches_loaded
        or not getattr(frappe, "conf", None)
        or not app_name in frappe.get_installed_apps()
    ):
        return

    folder = frappe.get_app_path(app_name, "monkey_patches")
    if not os.path.exists(folder): return

    import core_erp.monkey_patches

    patches_loaded = True


connect = frappe.connect


def custom_connect(*args, **kwargs):
    out = connect(*args, **kwargs)
    
    load_monkey_patches()
    return out

frappe.connect = custom_connect
