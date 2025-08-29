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
				"Quotation": ["name as 'link'","name","mobile_number_of_contact_person as 'whatsapp_mobile_no'"],
				"WMS Lead": ["name as 'link'","name","mobile_number as 'whatsapp_mobile_no'"],	
			}
			if not self.group_type == "Sales Order":
				filters = []
				if self.group_type == "WMS Lead":
					filters = [["type_of_contract","=",self.type_of_contract]]
				group_data = frappe.get_all(self.group_type,filters=filters,fields=doctype_fields_mape.get(self.group_type), order_by="modified desc")
				for row in group_data:
					self.append("table_9",dict(
						group_type = self.group_type,
						link = row.link,
						name_group = row.name,
						enable = 0,
						mobile = row.whatsapp_mobile_no
					))
			else:
				group_data = frappe.get_all(self.group_type,filters={},fields=["name as 'link'","name","mobile1 as 'whatsapp_mobile_no'","mobile2","mobile3"], order_by="modified desc")
				for row in group_data:
					self.append("table_9",dict(
						group_type = self.group_type,
						link = row.link,
						name_group = row.name,
						enable = 0,
						mobile = row.whatsapp_mobile_no,
						mobile2 = row.mobile2,
						mobile3 = row.mobile3
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

@frappe.whitelist()
def update_new_mobile_no(document_type,document_id,group_detail_id):
	doctype_mobile_no_field_map = {
		"Supplier":"mobile_no",
		"Employee":"cell_number",
		"Quotation":"mobile_number_of_contact_person",
		"WMS Lead":"mobile_number"
	}
	if document_type == "Sales Order":
		so_doc = frappe.db.get_("Sales Order",document_id)
		frappe.db.set_value("Group Details",group_detail_id,"mobile",so_doc.mobile1)
		frappe.db.set_value("Group Details",group_detail_id,"mobile2",so_doc.mobile2)
		frappe.db.set_value("Group Details",group_detail_id,"mobile3",so_doc.mobile3)
		return {"mobile":so_doc.mobile1,"mobile1":so_doc.mobile2,"mobile2":so_doc.mobile3}
	else:
		if doctype_mobile_no_field_map[document_type]:
			mobile_no = frappe.db.get_value(document_type,document_id,doctype_mobile_no_field_map[document_type])
			if mobile_no:
				frappe.db.set_value("Group Details",group_detail_id,"mobile",mobile_no)
		return {"mobile":mobile_no,"mobile1":"","mobile2":""}

