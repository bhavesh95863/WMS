# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class SalesOrderTraceability(Document):
    def autoname(self):
        self.name = self.batch_no

    def on_submit(self):
        self.update_portion_trace_record()

    def on_cancel(self):
        for row in self.details:
            if row.select:
                update_portion_traceability_record(
                    row.batch_no,
                    row.item,
                    row.portion_no,
                    self.inspection_sales_order,
                    cancel=True,
                )

    def validate_portion_no_rage(self):
        if self.portion_no_from and self.portion_no_to:
            if cint(self.portion_no_from) >= cint(self.portion_no_to):
                frappe.throw(_("Portion From No Must Be Less Than Portion To No"))

    def populate_data(self):
        self.validate_portion_no_rage()
        if not self.portion_no_from or not self.portion_no_to:
            frappe.throw(_("Portion From And To Number Required For Populate Data"))
        if not self.batch_no or not self.item:
            frappe.throw("Batch No And Item Mandatory For Populate Data")
        filters = [
            ["Portion Traceability", "portion_no", ">=", cint(self.portion_no_from)],
            ["Portion Traceability", "portion_no", "<=", cint(self.portion_no_to)],
            ["Portion Traceability", "batch_no", "=", self.batch_no],
            ["Portion Traceability", "manufactured_item", "=", self.item],
            ["Portion Traceability", "inspection_sales_order", "is", "not set"],
            ["Portion Traceability", "ignore_portion", "!=", 1],
        ]
        portion_trace_details = frappe.get_all(
            "Portion Traceability", filters=filters, fields=["portion_no"]
        )
        for row in portion_trace_details:
            self.append(
                "details",
                {
                    "batch_no": self.batch_no,
                    "portion_no": row.portion_no,
                    "item": self.item,
                },
            )

    def check_all(self):
        for row in self.details:
            row.select = 1

    def uncheck_all(self):
        for row in self.details:
            row.select = 0

    def update_portion_trace_record(self):
        for row in self.details:
            if row.select:
                update_portion_traceability_record(
                    row.batch_no, row.item, row.portion_no, self.inspection_sales_order
                )

    def get_portion_no(self):
        filters = [
            ["Portion Traceability", "inspection_sales_order", "is", "not set"],
            ["Portion Traceability", "batch_no", "=", self.batch_no],
            ["Portion Traceability", "ignore_portion", "=", 0],
        ]

        portion_trace_details = frappe.get_all(
            "Portion Traceability",
            filters=filters,
            fields=["portion_no"],
            order_by="portion_no asc",
        )
        portions = []
        for row in portion_trace_details:
            portions.append(row.get("portion_no"))
        return portions


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """select distinct batch_no as 'name' from `tabPortion Traceability` where inspection_sales_order is null""",
        as_list=1,
    )


@frappe.whitelist()
def get_sales_order(doctype, txt, searchfield, start, page_len, filters):
    cond = ""
    if txt:
        cond = " and name like '%{0}%'".format(txt)
    return frappe.db.sql(
        """SELECT DISTINCT name AS 'name'
FROM `tabSales Order`
WHERE name like 'OATW-%'
  OR name like 'OATWS-%'
  OR name like 'OATWR%'
  OR name like 'OATWSR%' %s""",
        cond,
        as_list=1,
    )


def update_portion_traceability_record(
    batch_no, item, portion_no, sales_order, cancel=False
):
    inspection_sales_order = "not set"
    if cancel:
        inspection_sales_order = "set"
    filters = [
        ["Portion Traceability", "batch_no", "=", batch_no],
        ["Portion Traceability", "manufactured_item", "=", item],
        ["Portion Traceability", "portion_no", "=", portion_no],
        [
            "Portion Traceability",
            "inspection_sales_order",
            "is",
            inspection_sales_order,
        ],
    ]
    portion_trace_details = frappe.get_all(
        "Portion Traceability", filters=filters, fields=["name"]
    )
    for row in portion_trace_details:
        if not cancel:
            frappe.db.set_value(
                "Portion Traceability", row.name, "inspection_sales_order", sales_order
            )
        else:
            frappe.db.set_value(
                "Portion Traceability", row.name, "inspection_sales_order", None
            )
