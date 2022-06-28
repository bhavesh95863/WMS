# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WMSLead(Document):
	def after_insert(self):
		if self.group:
			group_details = frappe.get_all("Group",filters=[["Group","name","=",self.group],["Group","group_type","=","WMS Lead"],["Group Details","link","=",self.name]],fields=["name"])
			if not len(group_details) >= 1:
				group_doc = frappe.get_doc("Group",self.group)
				group_doc.append("table_9",dict(
					group_type = "WMS Lead",
					link = self.name,
					name_group = self.name,
					mobile = self.mobile_number,
					enable = 1
				))
				group_doc.save(ignore_permissions = True)
	
	def on_update(self):
		if self.group:
			group_details = frappe.get_all("Group",filters=[["Group","name","=",self.group],["Group","group_type","=","WMS Lead"],["Group Details","link","=",self.name]],fields=["name"])
			if not len(group_details) >= 1:
				group_doc = frappe.get_doc("Group",self.group)
				group_doc.append("table_9",dict(
					group_type = "WMS Lead",
					link = self.name,
					name_group = self.name,
					mobile = self.mobile_number,
					enable = 1
				))
				group_doc.save(ignore_permissions = True)
