# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate,today,now
from frappe.model.document import Document

class WMSTask(Document):
	def validate(self):
		if not self.due_date:
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
		self.save()


	def mark_uncomplete(self):
		self.date_of_completion = ''
		self.save()
	

