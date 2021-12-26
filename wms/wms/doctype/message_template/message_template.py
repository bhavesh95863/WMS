# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe.model.document import Document

class MessageTemplate(Document):
	def validate(self):
		template_message = self.template_message.format()
		res = re.findall(r'\{.*?\}', template_message)
		template_variables = ""
		for variable in res:
			if not template_variables == "":
				template_variables += ","
			variable = variable.replace('{','')
			variable = variable.replace('}','')
			template_variables += f"{variable}"
		self.template_variables = template_variables