# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ATWPaymentStatus(Document):
	def on_submit(self):
		self.update_portion_trace_record()

	def populate_data(self):
		if not self.billing_warehouse and not self.execution_item and not self.date_of_payment_receipt:
			frappe.throw("Billing Warehouse, Execution Item And Payment Receipt Date Mandatory For Populate Data")
		filters = [
			["Portion Traceability","billing_warehouse","=",self.billing_warehouse],
			["Portion Traceability","welding_tolerance","=",1]
			]
		portion_trace_details = frappe.get_all("Portion Traceability",filters=filters,fields=["weld_no","name"])
		for row in portion_trace_details:
			self.append("details",{
				"weld_no": row.weld_no,
				"portion": row.name
			})

	def check_all(self):
		for row in self.details:
			row.select = 1

	def uncheck_all(self):
		for row in self.details:
			row.select = 0

	def update_portion_trace_record(self):
		for row in self.details:
			trace_doc = frappe.get_doc("Portion Traceability",row.portion)
			trace_doc.joint_paid_cc_no = self.cc_no
			trace_doc.billing_agent = self.billing_agent
			trace_doc.date_of_payment_receipt = self.date_of_payment_receipt
			trace_doc.save()



@frappe.whitelist()
def get_site_warehouse(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select billing_warehouse as 'name' from `tabPortion Traceability` where billing_warehouse is not null""",as_list=1)



@frappe.whitelist()
def get_execution_items(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select execution_item as 'name' from `tabPortion Traceability` where date_of_payment_receipt is null and execution_item is not null""",as_list=1)
