# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MaterialTransferTraceability(Document):
	def on_submit(self):
		self.update_portion_trace_record()

	def populate_data(self):
		if not self.batch_no or not self.item:
			frappe.throw("Batch No And Item Mandatory For Populate Data")
		filters = [
			["Portion Traceability","batch_no","=",self.batch_no],
			["Portion Traceability","manufactured_item","=",self.item],
			["Portion Traceability","date_of_transfer","is","not set"]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["portion_no"])
		for row in portion_trace_details:
			self.append("details",{
				"batch_no": self.batch_no,
				"portion_no": row.portion_no
			})

	def check_all(self):
		for row in self.details:
			row.select = 1

	def uncheck_all(self):
		for row in self.details:
			row.select = 0

	def update_portion_trace_record(self):
		for row in self.details:
			if row.select:
				update_portion_traceability_record(row.batch_no,row.portion_no,self.date_of_transfer,self.execution_item,self.source_warehouse,self.target_warehouse,self.dispatch_sales_order)


def update_portion_traceability_record(batch_no,portion_no,transfer_date,execution_item,source_warehouse,target_warehouse,sales_order):
		filters = [
			["Portion Traceability","batch_no","=",batch_no],
			["Portion Traceability","portion_no","=",portion_no],
			["Portion Traceability","date_of_transfer","is","not set"]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["name"])
		for row in portion_trace_details:
			trace_doc = frappe.get_doc("Portion Traceability",row.name)
			trace_doc.date_of_transfer = transfer_date
			trace_doc.source_warehouse = source_warehouse
			trace_doc.dispatch_sales_order = sales_order
			trace_doc.target_warehouse = target_warehouse
			trace_doc.execution_item = execution_item
			trace_doc.save()

@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select batch_no as 'name' from `tabPortion Traceability` where date_of_transfer is null""",as_list=1)
