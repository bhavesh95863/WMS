# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate
from frappe.utils.safe_exec import get_safe_globals
from frappe.model.document import Document
from frappe import _

class WMSTaskRule(Document):
	def validate(self):
		self.validate_condition()

	def validate_condition(self):
		temp_doc = frappe.new_doc(self.ref_doctype)
		if self.condition:
			try:
				frappe.safe_eval(self.condition, None, get_context(temp_doc.as_dict()))
			except Exception:
				frappe.throw(_("The Condition '{0}' is invalid").format(self.condition))

def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe": frappe._dict(utils=get_safe_globals().get("frappe").get("utils"))}