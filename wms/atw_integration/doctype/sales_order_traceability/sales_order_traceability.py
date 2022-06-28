# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesOrderTraceability(Document):
	def on_submit(self):
		self.update_portion_trace_record()

	def populate_data(self):
		if not self.batch_no or not self.item:
			frappe.throw("Batch No And Item Mandatory For Populate Data")
		filters = [
			["Portion Traceability","batch_no","=",self.batch_no],
			["Portion Traceability","manufactured_item","=",self.item],
			["Portion Traceability","inspection_sales_order","is","not set"]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["portion_no"])
		for row in portion_trace_details:
			self.append("details",{
				"batch_no": self.batch_no,
				"portion_no": row.portion_no,
				"item": self.item
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
				update_portion_traceability_record(row.batch_no,row.item,row.portion_no,self.inspection_sales_order)


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select distinct batch_no as 'name' from `tabPortion Traceability` where inspection_sales_order is null""",as_list=1)


def update_portion_traceability_record(batch_no,item,portion_no,sales_order):
		filters = [
			["Portion Traceability","batch_no","=",batch_no],
			["Portion Traceability","manufactured_item","=",item],
			["Portion Traceability","portion_no","=",portion_no],
			["Portion Traceability","inspection_sales_order","is","not set"]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["name"])
		for row in portion_trace_details:
			frappe.db.set_value("Portion Traceability",row.name,"inspection_sales_order",sales_order)
