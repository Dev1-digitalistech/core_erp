import frappe
from frappe.utils import now
from datetime import date,timedelta,datetime

#  project name ="Project for testing"  , parent_task_name = "Vertical Meal Mixer+Auto Vib. Screen (Already have)"
# print(item['exp_end_date'] +  yesterday)
@frappe.whitelist()
def validate(doc, method=None):
    parent_task_test = doc.name
    def testing(parent_task_test):
        get = frappe.db.get_value("Task",parent_task_test,'parent_task')
        if get:
            parent_task_test = get
            testing(parent_task_test)
        else:
            variable = parent_task_test
            task = frappe.db.sql(f"""select task from `tabTask Depends On` where parent = '{variable}' """,as_dict=1)
            # frappe.msgprint(str(task))
            list = []
            for items in task:
                main_group_date = frappe.db.get_value("Task",items['task'],['name','exp_end_date'],as_dict=1)
                list.append(main_group_date)
            latest_task = max(list, key=lambda x: x['exp_end_date'])
            latest_updated_date = latest_task['exp_end_date']
            frappe.msgprint(str(latest_updated_date))
            frappe.db.sql(f"""update `tabTask` set exp_end_date = '{latest_updated_date}' where name= '{variable}' """)
    

    if doc.exp_end_date:
        old_doc = doc.get_doc_before_save()
        if old_doc:
            if old_doc.exp_end_date != doc.exp_end_date:
                previous_date = old_doc.exp_end_date
                current_date = doc.exp_end_date
                d1 = datetime.strptime(str(previous_date), "%Y-%m-%d")
                d2 = datetime.strptime(str(current_date), "%Y-%m-%d")
                delta = d2 - d1

                diff_in_days = timedelta(days=delta.days)
                current_task = doc.name
                depended_task_list = []
                all_child_task_list = []
                # if doc.project:
                #     project_date = data2 = frappe.db.get_all("Project",{'name':doc.project},['name','expected_end_date'])
                #     change_start_date_format_of_project = datetime.strptime(str(project_date[0]['expected_end_date']), "%Y-%m-%d")
                #     frappe.db.sql(f"""update `tabProject` set expected_end_date = '{change_start_date_format_of_project + diff_in_days}' where name='{data2[0]['name']}' """)
                ##get all the depended task above this task
                def depended_task(current_task):
                    data = frappe.db.get_all("Task Depends On",{'parent':current_task},'task')
                    for task in data:
                        depended_task_list.append(task['task'])
                        if task['task']:
                            current_task = task['task']
                            depended_task(current_task)

                depended_task(current_task)


                all_child_task = frappe.db.get_all("Task",{"project":doc.project,"is_group":0,'parent_task_name':doc.parent_task_name},['name'])
                for task in all_child_task:
                    if task['name']!=doc.name:
                        all_child_task_list.append(task['name'])


                def remove_common(a, b):
                    a, b = [i for i in a if i not in b], [j for j in b if j not in a]
                
                    for items in a:
                        subject = frappe.db.get_all('Task', {'name':items}, ['name','exp_start_date','exp_end_date'])
                        # frappe.msgprint(str(subject))
                        for values in subject:
                            change_date_format_of_start_date = datetime.strptime(str(values['exp_start_date']), "%Y-%m-%d")
                            change_date_format_of_end_date = datetime.strptime(str(values['exp_end_date']), "%Y-%m-%d")
                            frappe.db.sql(f"""update `tabTask` set exp_end_date = '{change_date_format_of_end_date + diff_in_days}' where name='{values['name']}' """)
                            frappe.db.sql(f"""update `tabTask` set exp_start_date = '{change_date_format_of_start_date + diff_in_days}' where name='{values['name']}' """)
                        # frappe.db.sql(f"""update `tabTask` set exp_start_date = exp_start_date + '{diff_in_days}' where name='{items}' """)

                
                remove_common(all_child_task_list,depended_task_list)
                parent = doc.parent_task_name

                def recursion(parent):
                    data2 = frappe.db.get_all("Task",{'subject':parent,'project':doc.project},['name','exp_end_date','exp_start_date','parent_task_name'])
                    change_start_date_format_of_parent_task = datetime.strptime(str(data2[0]['exp_start_date']), "%Y-%m-%d")
                    change_end_date_format_of_parent_task = datetime.strptime(str(data2[0]['exp_end_date']), "%Y-%m-%d")
                    frappe.db.sql(f"""update `tabTask` set exp_end_date = '{change_end_date_format_of_parent_task + diff_in_days}' where name='{data2[0]['name']}' """)
                    # frappe.db.sql(f"""update `tabTask` set exp_start_date = '{change_start_date_format_of_parent_task + diff_in_days}' where name='{data2[0]['name']}' """)

                    if data2[0]['parent_task_name']:
                        parent = data2[0]['parent_task_name']
                        recursion(parent)
                    else:
                        pass

                if doc.parent_task_name:
                    recursion(parent)
                else:
                    pass
        else:
            pass
    testing(parent_task_test)

 
def validate_parent_expected_end_date_dup(self):
    pass

def validate_parent_project_dates_dup(self):
    pass

