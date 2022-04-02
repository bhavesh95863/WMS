# Copyright (c) 2013, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,getdate

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"label": _("Date From"),
			"fieldtype": "Date",
			"fieldname": "date_from"
		},
		{
			"label": _("Date To"),
			"fieldtype": "Date",
			"fieldname": "date_to",
		},
		{
			"label": _("Name"),
			"fieldtype": "Data",
			"fieldname": "employee_name",
			"width": 100
		},
		{
			"label": _("Total Tasks issued till today"),
			"fieldtype": "Int",
			"fieldname": "total_task_till_today",
			"width": 200
		},
		{
			"label": _("Tasks completed on time"),
			"fieldtype": "Int",
			"fieldname": "total_completed_on_time",
			"width": 200
		},
		{
			"label": _("Tasks completed late"),
			"fieldtype": "Int",
			"fieldname": "total_completed_late",
			"width": 200
		},
		{
			"label": _("Due Today"),
			"fieldtype": "Int",
			"fieldname": "due_today",
			"width": 200
		},
		{
			"label": _("Tasks overdue"),
			"fieldtype": "Int",
			"fieldname": "tasks_overdue",
			"width": 200
		},
		{
			"label": _("Tasks without due date"),
			"fieldtype": "Int",
			"fieldname": "tasks_without_due_date",
			"width": 200
		},
		{
			"label": _("Tasks Marked Complete Incorrectly"),
			"fieldtype": "Int",
			"fieldname": "tasks_marked_complete_incorrectly",
			"width": 200
		},
		{
			"label": _("% age Work Not done on time"),
			"fieldtype": "Float",
			"fieldname": "age_work_not_done_on_time",
			"width": 200,
			"precision": 2
		},
		{
			"label": _("salary increment %age"),
			"fieldtype": "Float",
			"fieldname": "salary_increment_age",
			"width": 200,
			"precision": 2
		}
	]

	return columns


def get_data(filters):
	data = []
	if not filters.get("employee"):
		users = []
		if "WMS Admin" in frappe.get_roles():
			users = frappe.get_all("User",filters={"enabled":1},fields=["name"])
		else:
			users = get_users()
		if users:
			for user in users:
				if not user.name in ["Administrator"]:
					frappe.errprint(user.get('name'))
					issues = frappe.get_all("WMS Task", filters=[["date_of_issue", "between", [
											filters.get("from_date"), filters.get("to_date")]],["assign_to","=",user.get('name')]], fields=["*"])
					row = dict(
						date_from = filters.get("from_date"),
						date_to = filters.get("to_date"),
						employee_name = frappe.db.get_value("User",user.name,"full_name")
					)
					get_filters_data(row,issues,filters)
					data.append(row)
	else:
		issues = frappe.get_all("WMS Task", filters=[["date_of_issue", "between", [
								filters.get("from_date"), filters.get("to_date")]],["assign_to","=",filters.get("employee")]], fields=["*"])
		row = dict(
			date_from = filters.get("from_date"),
			date_to = filters.get("to_date"),
			employee_name = frappe.db.get_value("User",filters.get("employee"),"full_name")
		)
		get_filters_data(row,issues,filters)
		data.append(row)
	return data

def get_users():
	employees = []
	emp_id = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"name")
	if emp_id:
		employees.append(emp_id)
	reporting_employees = frappe.get_all("Employee",filters={"reports_to":emp_id},fields=["name"])
	for row in reporting_employees:
		employees.append(row.name)
	if len(employees) >= 1:
		return frappe.db.sql("""select user_id as 'name' from `tabEmployee` where name in ({0}) """.format(', '.join(frappe.db.escape(i) for i in employees)),as_dict=1)


def get_filters_data(row,issues,filters):
	row["total_task_till_today"] = len(issues)
	row["total_completed_on_time"] = len(list(filter(lambda x: x['status'] == "Ontime", issues)))
	row["total_completed_late"] = len(list(filter(lambda x: x['status'] == "Late", issues)))
	row["tasks_overdue"] = len(list(filter(lambda x: x['status'] == "Overdue", issues)))
	row["tasks_without_due_date"] = len(list(filter(lambda x: x['status'] == "Without Due Date", issues)))
	row["tasks_marked_complete_incorrectly"] = len(list(filter(lambda x: int(x['mark_incomplete']) == 1, issues)))
	row["due_today"] = len(list(filter(lambda x: x['status'] == "Due Today", issues)))

	if (row["total_task_till_today"] > 0):
		task_not_complete = row["total_completed_late"] + row["tasks_overdue"] + row["tasks_without_due_date"]
		tasks_marked_complete_incorrectly = row["tasks_marked_complete_incorrectly"] * 5
		row["age_work_not_done_on_time"] = update_percentage(-1 * ((task_not_complete + tasks_marked_complete_incorrectly) / row["total_task_till_today"]) * 100)
	else:
		row["age_work_not_done_on_time"] = 0

	row["salary_increment_age"] = get_salary_increment(row["age_work_not_done_on_time"],filters)

def get_salary_increment(age_work_not_done_on_time,filters):
	year = getdate(filters.get("from_date")).year
	salary_increment_cap = frappe.db.get_value("Increment Capping",{"year":year,"docstatus":1},"increment_capping")
	if not salary_increment_cap:
		return 0
	else:
		return salary_increment_cap * (1 + (age_work_not_done_on_time / 100))

def update_percentage(value):
	if flt(value) < flt(-100):
		return -100
	else:
		return value
