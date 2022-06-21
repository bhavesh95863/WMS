# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today, now, add_days
from frappe.model.document import Document


class WMSTask(Document):
	def validate(self):
		if self.date_extend_request:
			self.status = "Extend Required"
		elif not self.due_date:
			self.status = "Without Due Date"
		elif self.date_of_completion and getdate(self.date_of_completion) <= getdate(self.due_date):
			self.status = "Ontime"
		elif self.date_of_completion and getdate(self.date_of_completion) > getdate(self.due_date):
			self.status = "Late"
		elif self.due_date and getdate(self.due_date) == getdate(today()):
			self.status = "Due Today"
		elif self.due_date and getdate(self.due_date) > getdate(today()):
			self.status = "Not Yet Due"
		elif self.due_date and getdate(self.due_date) < getdate(today()):
			self.status = "Overdue"
		if not self.assign_by:
			self.assign_by = frappe.session.user
		self.validate_date()
		self.validate_assign()


 
	def validate_date(self):
		if self.get('__islocal'):
			if getdate(self.date_of_issue) < getdate(today()):
				frappe.throw("Date Of Issue Must Be Today or Greater Than Today")

			def validate_holiday_leave(self):
				# frappe.errprint('call')
				if get_leave(self.assign_to,self.due_date):
					frappe.msgprint(f"{self.assign_to} Applied For Leave On {self.due_date}.So Due Date Adjust As per next working days ")
					self.due_date = add_days(self.due_date,1)
					return validate_holiday_leave(self)
				if get_holidays(self.assign_to,self.due_date):
					frappe.msgprint(f"Public Holiday On {self.due_date}. So Due Date Adjust As per next working days ")
					self.due_date = add_days(self.due_date,1)
					return validate_holiday_leave(self)
			validate_holiday_leave(self)

	def validate_assign(self):
		if self.assign_by == self.assign_to:
			frappe.throw("Assign From and Assign To Must Be Different")

	def mark_complete(self):
		if not self.date_of_completion:
			self.date_of_completion = now()
		self.completed = 1
		self.flags.ignore_permissions = True
		self.save()

	def mark_uncomplete(self):
		self.date_of_completion = ''
		self.mark_incomplete = 1
		self.completed = 0
		self.flags.ignore_permissions = True
		self.save()

	def approve_extend_request(self):
		self.append("task_extend_details",dict(
			due_date_before_extend = self.due_date,
			extend_date = self.date_extend_request,
			reason = self.reason,
			action = "Approve"
		))
		self.due_date = self.date_extend_request
		self.date_extend_request = ""
		self.reason = ""
		self.flags.ignore_permissions = True
		self.save()
	
	def reject_extend_request(self):
		self.append("task_extend_details",dict(
			due_date_before_extend = self.due_date,
			extend_date = self.date_extend_request,
			reason = self.reason,
			action = "Reject"
		))
		# self.due_date = self.date_extend_request
		self.date_extend_request = ""
		self.reason = ""
		self.save()

@frappe.whitelist()
def extend_date_request(task_id,date,reason=None):
	task_doc = frappe.get_doc("WMS Task",task_id)
	task_doc.date_extend_request = date
	task_doc.reason = reason
	task_doc.flags.ignore_permissions = True
	task_doc.save()

def get_permission_query_conditions(user):

	if not user: user = frappe.session.user
	if user == "Administrator" or "WMS Admin" in frappe.get_roles(user):
		return
	return """(`tabWMS Task`.`assign_by`=%(user)s or `tabWMS Task`.`assign_to`=%(user)s)""" % {
			"user": frappe.db.escape(user),
		}

@frappe.whitelist()
def get_users(doctype, txt, searchfield, start, page_len, filters):
	employees = []
	emp_id = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"name")
	if emp_id:
		employees.append(emp_id)
	reporting_employees = frappe.get_all("Employee",filters={"reports_to":emp_id},fields=["name"])
	for row in reporting_employees:
		employees.append(row.name)
	if len(employees) >= 1:
		return frappe.db.sql("""select user_id as 'name' from `tabEmployee` where name in ({0}) """.format(', '.join(frappe.db.escape(i) for i in employees)),as_list=1)


def get_leave(user,due_date):
	# frappe.errprint('leave')
	employee = frappe.db.get_value("Employee",{"user_id":user},"name")
	filters = [
		["employee","=",employee],
		["to_date","=",due_date],
		["docstatus","=",1]
	]
	leave_application = frappe.db.sql("""select name from `tabLeave Application` where %s between from_date and to_date and employee=%s and docstatus=1""",(due_date,employee),as_dict=1)
	# leave_application = frappe.db.get_all("Leave Application",filters=filters,fields=["*"])
	if len(leave_application) >= 1:
		return True
	else:
		return False

def get_holidays(user,due_date):
	# frappe.errprint('holiday')
	employee = frappe.db.get_value("Employee",{"user_id":user},"name")
	filters = [
		["Holiday","holiday_date","=",due_date],
	]
	holidays = frappe.db.get_all("Holiday List",filters=filters,fields=["name"])
	if len(holidays) >= 1:
		return True
	else:
		return False

