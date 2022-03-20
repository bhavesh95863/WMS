# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_time,nowtime,cstr,now_datetime
from wms.event.message_rule import send_whatsapp_message,send_sms_message
import json


class SendSMS(Document):
	def get_variables(self):
		if self.message_format:
			self.message_variable = []
			message_template_doc = frappe.get_doc(
				"Message Template", self.message_format)
			for row in message_template_doc.template_variables.split(','):
				self.append("message_variable", dict(
					template_variable=row
				))
		else:
			self.message_variable = []

	def on_submit(self):
		if self.when_to_send == "Now":
			send_message(self)
		else:
			self.status = "Scheduled"

@frappe.whitelist()
def cron_job_for_schedule_message():
	from datetime import datetime
	from datetime import timedelta
	from_time = now_datetime()
	to_time = now_datetime() + timedelta(minutes = 1)
	filters = [
		["docstatus","=",1],
		["sent","=",0],
		["schedule_date_and_time","between",[cstr(from_time),cstr(to_time)]]
	]
	send_sms_data = frappe.get_all("Send SMS",filters=filters,fields=["name"])
	print(send_sms_data)
	for row in send_sms_data:
		send_sms_doc = frappe.get_doc("Send SMS",row.name)
		send_message(send_sms_doc)
		frappe.db.set_value("Send SMS",row.name,"sent",1)

def send_message(doc):
	if doc.message_send_to == "All Suppliers":
		send_message_supplier(doc)
	if doc.message_send_to == "All Employees":
		send_message_employee(doc)
	if doc.message_send_to == "All Sales Order":
		send_message_sales_order(doc)
	if doc.message_send_to == "All Leads":
		send_message_lead(doc)
	if doc.message_send_to == "Group":
		send_message_group(doc)
	
def send_message_supplier(doc):
	suppliers_detail = frappe.db.sql(
		"""select name,mobile_no from `tabSupplier` where disabled=0 and mobile_no is not null""",as_dict=1)
	for row in suppliers_detail:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_format, row.get('mobile_no'), message_template_data, doc.name)

def send_message_employee(doc):
	employees_detail = frappe.db.sql(
		"""select name,cell_number as 'mobile_no' from `tabEmployee` where status='Active' and cell_number is not null""",as_dict=1)
	for row in employees_detail:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_format, row.get('mobile_no'), message_template_data, doc.name)

def send_message_sales_order(doc):
	so_details = frappe.db.sql(
		"""select name,mobile1,mobile2,mobile3 from `tabSales Order` where docstatus<>2""",as_dict=1)
	for row in so_details:
		message_template_data = get_template_data(doc)
		if row.get('mobile1'):
			send_whatsapp_message(doc.message_format, row.get('mobile1'), message_template_data, doc.name)
		if row.get('mobile2'):
			send_whatsapp_message(doc.message_format, row.get('mobile2'), message_template_data, doc.name)
		if row.get('mobile3'):
			send_whatsapp_message(doc.message_format, row.get('mobile3'), message_template_data, doc.name)

def send_message_lead(doc):
	lead_details = frappe.db.sql(
		"""select name,mobile_no as 'mobile_no' from `tabLead` where mobile_no is not null""",as_dict=1)
	for row in lead_details:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_format, row.get('mobile_no'), message_template_data, doc.name)

def send_message_group(doc):
	group_doc = frappe.get_doc("Group",doc.group)
	message_template_data = get_template_data(doc)
	for row in group_doc.table_9:
		if row.enable:
			# if row.group_type == "Customer":
			# 	mobile_no = frappe.db.get_value("Customer",row.link,"whatsapp_mobile_no")
			# 	if mobile_no:
			# 		if group_doc.get('whatsapp'):
			# 			send_whatsapp_message(doc.message_format,mobile_no, message_template_data, doc.name)
			# 		if group_doc.get('sms'):
			# 			send_text_message(doc,mobile_no)
			if row.group_type == "Supplier" and row.mobile:
				if group_doc.get('whatsapp'):
					send_whatsapp_message(doc.message_format,row.mobile, message_template_data, doc.name)
				if group_doc.get('sms'):
					send_text_message(doc,row.mobile)
			if row.group_type == "Employee" and row.mobile:
				if group_doc.get('whatsapp'):
					send_whatsapp_message(doc.message_format,row.mobile, message_template_data, doc.name)
				if group_doc.get('sms'):
					send_text_message(doc,row.mobile)
			if row.group_type == "Sales Order":
				order_doc = frappe.get_doc("Sales Order",row.link)
				if order_doc.mobile1:
					if group_doc.get('whatsapp'):
						send_whatsapp_message(doc.message_format,order_doc.mobile1, message_template_data, doc.name)
					if group_doc.get('sms'):
						send_text_message(doc,order_doc.mobile1)
				if order_doc.mobile2:
					if group_doc.get('whatsapp'):
						send_whatsapp_message(doc.message_format,order_doc.mobile2, message_template_data, doc.name)
					if group_doc.get('sms'):
						send_text_message(doc,order_doc.mobile2)
				if order_doc.mobile3:
					if group_doc.get('whatsapp'):
						send_whatsapp_message(doc.message_format,order_doc.mobile3, message_template_data, doc.name)
					if group_doc.get('sms'):
						send_text_message(doc,order_doc.mobile3)
			if row.group_type == "WMS Lead":
				if group_doc.get('whatsapp'):
					send_whatsapp_message(doc.message_format,row.mobile, message_template_data, doc.name)
				if group_doc.get('sms'):
					send_text_message(doc,row.mobile)

def send_text_message(doc,mobile_no):
	data = {}
	for field in doc.message_variable:
		data[field.get('template_variable')] = field.get('value')
	message = frappe.render_template(doc.message,data)
	receiver_list = []
	receiver_list.append(mobile_no)
	send_sms_message(message,receiver_list)

def get_template_data(doc):
	data = []
	for field in doc.message_variable:
		data.append({
			'name': field.get('template_variable'),
			'value': field.get('value')
		})
	return json.dumps(data)