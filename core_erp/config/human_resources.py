from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Employee"),
			"items": [
                {
					"type": "doctype",
					"name": "Department",
					
				},
                {
					"type": "doctype",
					"name": "Employee Grade",
					
				},
                {
					"type": "doctype",
					"name": "Employee Group",
					
				}
               
			],
			
			"label": _("Attendance"),
			"items": [
                    {
					"type": "doctype",
					"name": "Attendance",
					
				},
                {
					"type": "doctype",
					"name": "Attendance Request",
					
				},
                {
					"type": "doctype",
					"name": "Employee Checkin",
					
				}
				
			],
			
			"label": _("Leaves"),
			"items": [
				{
					"type": "doctype",
					"name": "Leave Policy",
					
				},
                {
					"type": "doctype",
					"name": "Leave Period",
					
				},
                {
					"type": "doctype",
					"name": "Compensatory Leave Request",
					
				},
                {
					"type": "doctype",
					"name": "Leave Encashment",
					
				}
			],
            "label": _("Payroll"),
			"items": [
				{
					"type": "doctype",
					"name": "Payroll Period",
					
				},
                {
					"type": "doctype",
					"name": "Income Tax Slab",
					
				},
                {
					"type": "doctype",
					"name": "Additional Salary",
					
				},
                {
					"type": "doctype",
					"name": "Retention Bonus",
					
				}
			],
             "label": _("Employee Tax and Benefits"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee Tax Exemption Declaration",
					
				},
                {
					"type": "doctype",
					"name": "Employee Tax Exemption Proof Submission",
					
				},
                {
					"type": "doctype",
					"name": "Employee Benefit Application",
					
				},
                {
					"type": "doctype",
					"name": "Employee Benefit Claim",
					
				},
                {
					"type": "doctype",
					"name": "Employee Tax Exemption Category",
					
				},
                {
					"type": "doctype",
					"name": "Employee Tax Exemption Sub Category",
					
				}
			],
            "label": _("Employee Lifecycle"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee Skill Map",
					
				},
                {
					"type": "doctype",
					"name": "Employee Separation",
					
				},
                {
					"type": "doctype",
					"name": "Employee Onboarding Template",
					
				},
                {
					"type": "doctype",
					"name": "Employee Separation Template",
					
				}
			],
             "label": _("Recruitment"),
			"items": [
				{
					"type": "doctype",
					"name": "Job Opening",
					
				}
            ],
            "label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "HR Settings",
					
				},
                {
					"type": "doctype",
					"name": "Team Updates",
					
				}
			],
                "label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees working on a holiday",
					"doctype": "Attendence"
				}
            ]
		}
	]