frappe.query_reports['Completed Work Orders'] = {

    filters: [

        {

            fieldname: 'company',

            label: __('Company'),

            fieldtype: 'Link',

            options: 'Company',

            default: frappe.defaults.get_user_default('company')

        },

        {

            fieldname: 'from_date',

            label: __('From Date'),

            fieldtype: 'Date',

            default: frappe.datetime.add_days(frappe.datetime.now_date(),-1),


        },
        {

            fieldname: 'to_date',

            label: __('TO Date'),

            fieldtype: 'Date',

            default: frappe.datetime.now_date(),


        }

    ]

}
