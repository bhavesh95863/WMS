# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _


class USFDTestResult(Document):
    def on_submit(self):
        self.validate_before_submit()
        self.update_portion_trace_record()

    def on_cancel(self):
        self.update_portion_trace_record_cancel()

    def validate_before_submit(self):
        for row in self.details:
            if not row.good and not row.defective:
                frappe.throw(
                    _("Row{0}: Select Good or Defective Before Submit".format(row.idx))
                )

    def populate_data(self):
        if not self.site_warehouse or not self.testing:
            frappe.throw("Site Warehouse And Testing Mandatory For Populate Data")
        filters = [["Portion Traceability", "welding_tolerance", "=", 1]]
        if self.testing == "Internal":
            filters.append(
                ["Portion Traceability", "internal_usfd_result", "is", "not set"]
            )
        if self.testing == "External":
            filters.append(
                ["Portion Traceability", "external_usfd_result", "is", "not set"]
            )
        portion_trace_details = frappe.get_all(
            "Portion Traceability",
            filters=filters,
            fields=["weld_no", "date_of_welding", "km_tp", "lh_rh", "name"],
        )
        for row in portion_trace_details:
            self.append(
                "details",
                {
                    "portion": row.name,
                    "weld_no": row.weld_no,
                    "date_of_welding": row.date_of_welding,
                    "km_tp": row.km_tp,
                    "lh_rh": row.lh_rh,
                },
            )

    def check_all(self):
        for row in self.details:
            row.select = 1

    def check_all_good(self):
        for row in self.details:
            row.good = 1

    def check_all_defective(self):
        for row in self.details:
            row.defective = 1

    def uncheck_all(self):
        for row in self.details:
            row.select = 0

    def update_portion_trace_record(self):
        for row in self.details:
            if row.select:
                trace_doc = frappe.get_doc("Portion Traceability", row.portion)
                if self.testing == "Internal":
                    if row.good:
                        trace_doc.internal_usfd_result = "Good"
                    if row.defective:
                        trace_doc.internal_usfd_result = "Defective"
                if self.testing == "External":
                    if row.good:
                        trace_doc.external_usfd_result = "Good"
                    if row.defective:
                        trace_doc.external_usfd_result = "Defective"
                trace_doc.save()

    def update_portion_trace_record_cancel(self):
        for row in self.details:
            if row.select:
                trace_doc = frappe.get_doc("Portion Traceability", row.portion)
                if self.testing == "Internal":
                    trace_doc.internal_usfd_result = None
                if self.testing == "External":
                    trace_doc.external_usfd_result = None
                trace_doc.save()


@frappe.whitelist()
def get_site_warehouse(doctype, txt, searchfield, start, page_len, filters):
    cond = ""
    if txt:
        cond = " and target_warehouse like '%{0}%'".format(txt)
    return frappe.db.sql(
        """select target_warehouse as 'name' from `tabPortion Traceability` where target_warehouse is not null""",
        as_list=1,
    )
