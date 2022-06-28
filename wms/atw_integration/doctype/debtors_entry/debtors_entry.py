# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DebtorsEntry(Document):
	def on_submit(self):
		self.update_portion_trace_record()

	def populate_data(self):
		if not self.batch_no or not self.site_warehouse or not self.billing_warehouse:
			frappe.throw("Batch No,Site Warehouse And Billing Warehouse Mandatory For Populate Data")
		filters = [
			["Portion Traceability","batch_no","=",self.batch_no],
			["Portion Traceability","debtors_entry","is","not set"],
			["Portion Traceability","welding_tolerance","=",1]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["weld_no","date_of_welding"])
		for row in portion_trace_details:
			self.append("details",{
				"weld_no": row.weld_no,
				"date_of_welding": row.date_of_welding
			})

	def check_all(self):
		for row in self.details:
			row.select = 1

	def uncheck_all(self):
		for row in self.details:
			row.select = 0

	def update_portion_trace_record(self):
			filters = [
				["Portion Traceability","batch_no","=",self.batch_no],
				["Portion Traceability","debtors_entry","is","not set"],
				["Portion Traceability","welding_tolerance","=",1]
				]
			portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["name"])
			for row in portion_trace_details:
				trace_doc = frappe.get_doc("Portion Traceability",row.name)
				trace_doc.debtors_entry = self.name
				trace_doc.billing_warehouse = self.billing_warehouse
				trace_doc.save()


@frappe.whitelist()
def get_site_warehouse(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select target_warehouse as 'name' from `tabPortion Traceability` where debtors_entry is null and target_warehouse is not null""",as_list=1)


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("target_warehouse"):
		frappe.throw("Select Site Warehouse First")
	return frappe.db.sql("""select batch_no as 'name' from `tabPortion Traceability` where debtors_entry is null and target_warehouse=%s""",filters.get("target_warehouse"),as_list=1)


