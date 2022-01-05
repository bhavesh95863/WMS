# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today, now
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

 

	def mark_complete(self):
		if not self.date_of_completion:
			self.date_of_completion = now()
		self.completed = 1
		self.flags.ignore_permissions = True
		self.save()

	def mark_uncomplete(self):
		self.date_of_completion = ''
		self.completed = 0
		self.flags.ignore_permissions = True
		self.save()

	def approve_extend_request(self):
		self.append("task_extend_details",dict(
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
	if user == "Administrator":
		return
	return """(`tabWMS Task`.`assign_by`=%(user)s or `tabWMS Task`.`assign_to`=%(user)s)""" % {
			"user": frappe.db.escape(user),
		}