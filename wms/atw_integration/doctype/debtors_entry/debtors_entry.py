# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DebtorsEntry(Document):
	pass



@frappe.whitelist()
def get_site_warehouse(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select target_warehouse as 'name' from `tabPortion Traceability` where debtors_entry is null and target_warehouse is not null""",as_list=1)


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("target_warehouse"):
		frappe.throw("Select Site Warehouse First")
	return frappe.db.sql("""select batch_no as 'name' from `tabPortion Traceability` where debtors_entry is null and target_warehouse=%s""",filters.get("target_warehouse"),as_list=1)
