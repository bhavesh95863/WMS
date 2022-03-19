# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re

class MessageRule(Document):
	def validate(self):
		if self.rule_based_on == "Sales Order":
			self.set_sales_order_field_name()
		if self.rule_based_on == "Other":
			self.validate_mobile_no_field()
		self.set_variable()

	def validate_mobile_no_field(self):
		if not self.mobile_no_field:
			frappe.throw("Select Mobile No Field Name.")

	def set_sales_order_field_name(self):
		meta = frappe.get_meta(self.ref_doctype)
		so_field_exists = False
		so_field_name = ''
		if not self.ref_doctype == "Sales Order":
			for field in meta.fields:
				if field.options == "Sales Order":
					so_field_name = field.fieldname
					so_field_exists = True
					break
			self.sales_order_field = so_field_name
			if not so_field_exists:
				frappe.throw("Selected Doctype {0} Does Not Have Sales Order Field. Select Only Doctype Which Have Sales Order Field".format(self.ref_doctype))
		else:
			self.sales_order_field = "name"

	def set_variable(self):
		template_doc = frappe.get_doc("Message Template",self.message_template)
		template_message = template_doc.template_message.format()
		res = re.findall(r'\{.*?\}', template_message)
		# self.template_variable = []
		if not self.template_variables:
			self.template_variables = ""
		for variable in res:
			if not self.template_variables == "":
				self.template_variables += ","
			variable = variable.replace('{','')
			variable = variable.replace('}','')
			if not frappe.db.exists("Template Variable",{"template_variable": variable,"parenttype":"Message Rule","ref_doctype":self.ref_doctype}):
				self.template_variables += f"{variable}"
				self.append("template_variable",dict(
					template_variable = variable,
					ref_doctype = self.ref_doctype
				))