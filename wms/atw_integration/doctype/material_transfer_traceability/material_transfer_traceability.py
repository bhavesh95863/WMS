# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, cstr, cint
from frappe import _


class MaterialTransferTraceability(Document):
    def autoname(self):
        self.name = (
            self.dispatch_sales_order
            + "-"
            + cstr(self.date_of_transfer)
            + "-"
            + self.batch_no
        )

    def on_submit(self):
        self.qty = 0
        self.update_portion_trace_record()
        self.create_transfer_entry()

    def on_cancel(self):
        self.update_portion_trace_record_cancel()
        stock_entry = frappe.db.get_value("Stock Entry", {"mtt": self.name}, "name")
        if stock_entry:
            status = frappe.db.get_value("Stock Entry", stock_entry, "docstatus")
            stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry)
            if int(status) == 1:
                stock_entry_doc.cancel()
            if int(status) == 0:
                frappe.delete_doc("Stock Entry", stock_entry)

    def validate_portion_no_rage(self):
        if self.portion_no_from and self.portion_no_to:
            if cint(self.portion_no_from) >= cint(self.portion_no_to):
                frappe.throw(_("Portion From No Must Be Less Than Portion To No"))

    def populate_data(self):
        self.validate_portion_no_rage()
        if not self.batch_no or not self.item:
            frappe.throw("Batch No And Item Mandatory For Populate Data")
        filters = [
            ["Portion Traceability", "portion_no", ">=", cint(self.portion_no_from)],
            ["Portion Traceability", "portion_no", "<=", cint(self.portion_no_to)],
            ["Portion Traceability", "batch_no", "=", self.batch_no],
            ["Portion Traceability", "manufactured_item", "=", self.item],
            ["Portion Traceability", "inspection_sales_order", "is", "set"],
            ["Portion Traceability", "current_warehouse", "=", self.source_warehouse],
        ]
        portion_trace_details = frappe.get_all(
            "Portion Traceability", filters=filters, fields=["portion_no"]
        )
        for row in portion_trace_details:
            self.append(
                "details", {"batch_no": self.batch_no, "portion_no": row.portion_no}
            )

    def get_portion_no(self):
        filters = [["Portion Traceability", "inspection_sales_order", "is", "set"]]
        if self.batch_no:
            filters.append(["Portion Traceability", "batch_no", "=", self.batch_no])
        if self.item:
            filters.append(
                ["Portion Traceability", "manufactured_item", "=", self.item]
            )
        if self.source_warehouse:
            filters.append(
                [
                    "Portion Traceability",
                    "current_warehouse",
                    "=",
                    self.source_warehouse,
                ]
            )

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
                    row.batch_no,
                    row.portion_no,
                    self.date_of_transfer,
                    self.execution_item,
                    self.source_warehouse,
                    self.target_warehouse,
                    self.dispatch_sales_order,
                )
                self.qty += 1

    def update_portion_trace_record_cancel(self):
        for row in self.details:
            if row.select:
                update_portion_traceability_record_cancel(
                    row.batch_no,
                    row.portion_no,
                    self.date_of_transfer,
                    self.execution_item,
                    self.source_warehouse,
                    self.target_warehouse,
                    self.dispatch_sales_order,
                )

    def create_transfer_entry(self):
        items = []
        items.append(
            dict(
                item_code=self.item,
                batch_no=self.batch_no,
                s_warehouse=self.source_warehouse,
                t_warehouse=self.target_warehouse,
                qty=self.qty,
            )
        )
        doc = frappe.get_doc(
            dict(
                doctype="Stock Entry",
                stock_entry_type="Material Transfer",
                posting_date=self.date_of_transfer,
                from_warehouse=self.source_warehouse,
                to_warehouse=self.target_warehouse,
                items=items,
                mtt=self.name,
                sales_order=self.dispatch_sales_order,
            )
        )
        doc.insert(ignore_permissions=True)


def update_portion_traceability_record(
    batch_no,
    portion_no,
    transfer_date,
    execution_item,
    source_warehouse,
    target_warehouse,
    sales_order,
):
    filters = [
        ["Portion Traceability", "batch_no", "=", batch_no],
        ["Portion Traceability", "portion_no", "=", portion_no],
    ]

    portion_trace_details = frappe.get_all(
        "Portion Traceability", filters=filters, fields=["name"]
    )
    for row in portion_trace_details:
        trace_doc = frappe.get_doc("Portion Traceability", row.name)
        trace_doc.date_of_transfer = transfer_date
        trace_doc.source_warehouse = source_warehouse
        trace_doc.dispatch_sales_order = sales_order
        trace_doc.target_warehouse = target_warehouse
        trace_doc.current_warehouse = target_warehouse
        trace_doc.execution_item = execution_item
        trace_doc.save()


def update_portion_traceability_record_cancel(
    batch_no,
    portion_no,
    transfer_date,
    execution_item,
    source_warehouse,
    target_warehouse,
    sales_order,
):
    filters = [
        ["Portion Traceability", "batch_no", "=", batch_no],
        ["Portion Traceability", "portion_no", "=", portion_no],
        ["Portion Traceability", "date_of_transfer", "=", transfer_date],
        ["Portion Traceability", "source_warehouse", "=", source_warehouse],
        ["Portion Traceability", "dispatch_sales_order", "=", sales_order],
        ["Portion Traceability", "execution_item", "=", execution_item],
        ["Portion Traceability", "current_warehouse", "=", target_warehouse],
    ]
    portion_trace_details = frappe.get_all(
        "Portion Traceability", filters=filters, fields=["name"]
    )
    for row in portion_trace_details:
        trace_doc = frappe.get_doc("Portion Traceability", row.name)
        trace_doc.date_of_transfer = None
        trace_doc.source_warehouse = None
        trace_doc.dispatch_sales_order = None
        trace_doc.target_warehouse = None
        trace_doc.current_warehouse = None
        trace_doc.execution_item = None
        trace_doc.save()


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """select distinct batch_no as 'name' from `tabPortion Traceability` where date_of_transfer is null""",
        as_list=1,
    )


@frappe.whitelist()
def get_execution_item(doctype, txt, searchfield, start, page_len, filters):
    if not filters.get("sales_order"):
        frappe.throw("Select Sales Order First")
    cond = "parent='{0}'".format(filters.get("sales_order"))
    if txt:
        cond += " and item_code like '%{0}%'".format(txt)
    return frappe.db.sql(
        """SELECT item_code,item_name 
FROM `tabSales Order Item`
WHERE {0}""".format(
            cond
        )
    )
