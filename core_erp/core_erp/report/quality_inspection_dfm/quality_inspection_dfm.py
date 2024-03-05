# Copyright (c) 2023, Extension and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    conditions = get_conditions(filters)
    return columns, data
