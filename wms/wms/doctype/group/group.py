# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Group(Document):
	def get_group_type_details(self):
		if self.group_type:
			self.table_9 = []
			doctype_fields_mape = {
				"Customer": ["name as 'link'","customer_name as 'name'","whatsapp_mobile_no"],
				"Employee": ["name as 'link'","employee_name as 'name'","cell_number as 'whatsapp_mobile_no'"],
				"Supplier": ["name as 'link'","supplier_name as 'name'","mobile_no as 'whatsapp_mobile_no'"],
				"Sales Order": ["name as 'link'","name","mobile1 as 'whatsapp_mobile_no'"],
				"Quotation": ["name as 'link'","name","mobile_no as 'whatsapp_mobile_no'"],
				"WMS Lead": ["name as 'link'","name","mobile_number as 'whatsapp_mobile_no'"],	
			}
			group_data = frappe.get_all(self.group_type,filters={},fields=doctype_fields_mape.get(self.group_type), order_by="modified desc")
			for row in group_data:
				self.append("table_9",dict(
					group_type = self.group_type,
					link = row.link,
					name_group = row.name,
					enable = 0,
					mobile = row.whatsapp_mobile_no
				))
		else:
			self.table_9 = []
	
	def enable_all(self):
		for row in self.table_9:
			row.enable = 1
		self.save()

	def disable_all(self):
		for row in self.table_9:
			row.enable = 0
		self.save()
	

