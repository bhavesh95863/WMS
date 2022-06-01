# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe import _

class ATWManfTraceability(Document):
	def validate(self):
		self.validate_portion_no_rage()

	def on_submit(self):
		self.create_portion_trace_record()

	def validate_portion_no_rage(self):
		if self.portion_no_from and self.portion_no_to:
			if cint(self.portion_no_from) >= cint(self.portion_no_to):
				frappe.throw(_("Portion From No Must Be Less Than Portion To No"))
	
	def populate_data(self):
		self.validate_portion_no_rage()
		if not self.portion_no_from or not self.portion_no_to:
			frappe.throw(_("Portion From And To Number Required For Populate Data"))
		portion_no_from = cint(self.portion_no_from)
		portion_no_to = cint(self.portion_no_to)
		while portion_no_from <= portion_no_to:
			self.append("details",{
				"batch_no": self.batch_no,
				"portion_no": portion_no_from,
				"item": self.item
			})
			portion_no_from = portion_no_from + 1

	def check_all(self):
		for row in self.details:
			row.select = 1

	def uncheck_all(self):
		for row in self.details:
			row.select = 0

	def create_portion_trace_record(self):
		for row in self.details:
			if row.select:
				create_portion_traceability(row.batch_no,row.item,row.portion_no)
	
def create_portion_traceability(batch_no,item,portion_no):
	doc = frappe.new_doc("Portion Traceability")
	doc.batch_no = batch_no
	doc.portion_no = portion_no
	doc.manufactured_item = item
	doc.insert(ignore_permissions = True)

