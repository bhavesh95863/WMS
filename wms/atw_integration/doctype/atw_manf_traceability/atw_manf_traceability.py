# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt
from frappe import _


class ATWManfTraceability(Document):
    def autoname(self):
        self.name = self.batch_no

    def validate(self):
        self.validate_portion_no_rage()

    def on_cancel(self):
        self.delete_portion_trace_record()

    def on_submit(self):
        self.create_portion_trace_record()
        self.update_ignore_portions()

    def validate_portion_no_rage(self):
        if self.portion_no_from and self.portion_no_to:
            if len(str(self.portion_no_from)) > 17:
                frappe.throw(_("Portion No From length is more than 16"))
            if len(str(self.portion_no_to)) > 17:
                frappe.throw(_("Portion No to length is more than 16"))
            if cint(self.portion_no_from) >= cint(self.portion_no_to):
                frappe.throw(_("Portion From No Must Be Less Than Portion To No"))

    def populate_data(self):
        self.validate_portion_no_rage()
        if not self.portion_no_from or not self.portion_no_to:
            frappe.throw(_("Portion From And To Number Required For Populate Data"))
        portion_no_from = cint(self.portion_no_from)
        portion_no_to = cint(self.portion_no_to)
        while portion_no_from <= portion_no_to:
            self.append(
                "details",
                {
                    "batch_no": self.batch_no,
                    "portion_no": portion_no_from,
                    "item": self.item,
                },
            )
            portion_no_from = portion_no_from + 1

    def check_all(self):
        for row in self.details:
            row.select = 1

    def uncheck_all(self):
        for row in self.details:
            row.select = 0

    def create_portion_trace_record(self):
        for row in self.details:
            if row.select:
                create_portion_traceability(
                    row.batch_no, row.item, row.portion_no, self.warehouse
                )

    def popuplate_result_category(self):
        meta = frappe.get_meta("Trial Joints Internal Results")
        result_category = meta.fields[0].options.split("\n")
        self.trial_joints_internal_results_details = []
        self.trial_joints_external_results_details = []
        for row in result_category:
            self.append(
                "trial_joints_internal_results_details", dict(result_category=row)
            )
            self.append(
                "trial_joints_external_results_details", dict(result_category=row)
            )

    def update_ignore_portions(self):
        for row in self.trial_joints_internal_results_details:
            if row.result_category == "Portion No":
                portion_id = frappe.db.get_value(
                    "Portion Traceability", {"portion_no": cint(row.result)}, "name"
                )
                if portion_id:
                    frappe.db.set_value(
                        "Portion Traceability", portion_id, "ignore_portion", 1
                    )
                break
        for row in self.trial_joints_external_results_details:
            if row.result_category == "Portion No":
                portion_id1 = frappe.db.get_value(
                    "Portion Traceability", {"portion_no": cint(row.result1)}, "name"
                )
                if portion_id1:
                    frappe.db.set_value(
                        "Portion Traceability", portion_id1, "ignore_portion", 1
                    )
                portion_id2 = frappe.db.get_value(
                    "Portion Traceability", {"portion_no": cint(row.result2)}, "name"
                )
                if portion_id2:
                    frappe.db.set_value(
                        "Portion Traceability", portion_id2, "ignore_portion", 1
                    )
                break

    def delete_portion_trace_record(self):
        frappe.db.sql(
            """delete from `tabPortion Traceability` where batch_no=%s and inspection_sales_order is null""",
            self.batch_no,
        )


def create_portion_traceability(batch_no, item, portion_no, warehouse):
    doc = frappe.new_doc("Portion Traceability")
    doc.batch_no = batch_no
    doc.portion_no = portion_no
    doc.manufactured_item = item
    doc.current_warehouse = warehouse
    doc.insert(ignore_permissions=True)
