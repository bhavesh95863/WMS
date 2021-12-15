import frappe
from frappe.utils import today, getdate, cint, now, add_days, parse_val


def create_task_for_event(doc, method):
    if (frappe.flags.in_import and frappe.flags.mute_emails) or frappe.flags.in_patch or frappe.flags.in_install:
        return
    get_task_template(doc,doc.doctype, method)


def create_task_for_recurring():
    templates = []
    tasks = frappe.get_all("WMS Task Rule", filters={
                           "recurring": 1}, fields=["*"])
    for row in tasks:
        if row.frequency == "Daily":
            templates.append(row)
        if row.frequency == "Monthly":
            today_day = getdate(today()).day
            if cint(today_day) == cint(row.date_of_month):
                templates.append(row)
        if row.frequency == "Weekly":
            today_day_name = getdate(today()).strftime('%A')
            if today_day_name == row.day_of_week:
                templates.append(row)
        if row.frequency == "Yearly":
            today_day = getdate(today()).day
            today_month = getdate(today()).month
            if cint(today_day) == cint(row.date_of_month) and cint(today_month) == cint(row.month_of_year):
                templates.append(row)
    evalute_recuring_task(templates)


def get_task_template(self,doctype, method):
    event_map = {
        "on_submit": "Submit",
        "after_insert": "New",
        "on_cancel": "Cancel",
        "after_save": "Save"
    }
    if not self.flags.in_insert:
        # value change is not applicable in insert
        event_map['on_change'] = 'Value Change'
    based_on = event_map.get(method)
    if not based_on:
        return
    tasks = frappe.get_all("WMS Task Rule", filters={
                           "based_on": based_on, "ref_doctype": doctype}, fields=["*"])
    if tasks:
        evalute_event_task(self,based_on,tasks)


def evalute_event_task(self,based_on,tasks):
    for task in tasks:
        if based_on=="Value Change" and not self.is_new():
            if not frappe.db.has_column(self.doctype, task.fields):
                continue
            else:
                doc_before_save = self.get_doc_before_save()
                field_value_before_save = doc_before_save.get(task.fields) if doc_before_save else None
                field_value_before_save = parse_val(field_value_before_save)
                if (self.get(task.fields) == field_value_before_save):
                    # value not changed
                    continue
                else:
                    create_task(task,"ERP")
        else:
            create_task(task,"ERP")

def evalute_recuring_task(tasks):
    for task in tasks:
        create_task(task,"Recurring")

def create_task(task,task_type):
    doc = frappe.get_doc(dict(
        doctype="WMS Task",
        date_of_issue=now(),
        due_date=add_days(today(), task.get('due_days')),
        source=task_type,
        details=task.get('task_details'),
        task_title=task.get('task_title'),
        assign_to=task.get('assign_to'),
        assign_by=frappe.session.user
    )).insert(ignore_permissions=True)
