# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today


class DebtorsEntry(Document):
    def autoname(self):
        self.name = self.billing_sales_order + "-" + self.date

    def on_submit(self):
        self.update_portion_trace_record()
        self.create_transfer_entry()

    def on_cancel(self):
        self.update_portion_trace_record_cancel()
        stock_entry = frappe.db.get_value(
            "Stock Entry", {"debtor_entry": self.name}, "name"
        )
        if stock_entry:
            status = frappe.db.get_value("Stock Entry", stock_entry, "docstatus")
            stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry)
            if int(status) == 1:
                stock_entry_doc.cancel()
            if int(status) == 0:
                frappe.delete_doc("Stock Entry", stock_entry)

    def populate_data(self):
        if not self.site_warehouse or not self.billing_warehouse:
            frappe.throw(
                "Site Warehouse And Billing Warehouse Mandatory For Populate Data"
            )
        filters = [
            ["Portion Traceability", "debtors_entry", "is", "not set"],
            ["Portion Traceability", "welding_tolerance", "=", 1],
        ]
        portion_trace_details = frappe.get_all(
            "Portion Traceability",
            filters=filters,
            fields=[
                "weld_no",
                "date_of_welding",
                "batch_no",
                "manufactured_item",
                "execution_item",
                "location_of_weld",
            ],
        )
        for row in portion_trace_details:
            self.append(
                "details",
                {
                    "weld_no": row.weld_no,
                    "date_of_welding": row.date_of_welding,
                    "batch_no": row.batch_no,
                    "manufactured_item": row.manufactured_item,
                    "execution_item": row.execution_item,
                    "location": row.location_of_weld,
                },
            )

    def check_all(self):
        for row in self.details:
            row.select = 1

    def uncheck_all(self):
        for row in self.details:
            row.select = 0

    def update_portion_trace_record(self):
        filters = [
            ["Portion Traceability", "debtors_entry", "is", "not set"],
            ["Portion Traceability", "welding_tolerance", "=", 1],
        ]
        portion_trace_details = frappe.get_all(
            "Portion Traceability", filters=filters, fields=["name"]
        )
        for row in portion_trace_details:
            trace_doc = frappe.get_doc("Portion Traceability", row.name)
            trace_doc.debtors_entry = self.name
            trace_doc.billing_warehouse = self.billing_warehouse
            trace_doc.save()

    def update_portion_trace_record_cancel(self):
        filters = [
            ["Portion Traceability", "welding_tolerance", "=", 1],
            ["Portion Traceability", "debtors_entry", "=", self.name],
            ["Portion Traceability", "billing_warehouse", "=", self.billing_warehouse],
        ]
        portion_trace_details = frappe.get_all(
            "Portion Traceability", filters=filters, fields=["name"]
        )
        for row in portion_trace_details:
            trace_doc = frappe.get_doc("Portion Traceability", row.name)
            trace_doc.debtors_entry = None
            trace_doc.billing_warehouse = None
            trace_doc.save()

    def load_billing_warehouse(self):
        sales_order = frappe.db.get_value(
            "Warehouse", self.site_warehouse, "sales_order"
        )
        if sales_order:
            self.billing_sales_order = sales_order
            billing_warehouse = frappe.get_all(
                "Warehouse",
                filters={"sales_order": sales_order, "warehouse_type": "Billing"},
                fields=["name"],
            )
            if len(billing_warehouse) >= 1:
                self.billing_warehouse = billing_warehouse[0].name

    def create_transfer_entry(self):
        items = []
        qty = 0
        for row in self.details:
            if row.select:
                # qty += 1

                items.append(
                    dict(
                        item_code=row.manufactured_item,
                        batch_no=row.batch_no,
                        s_warehouse=self.site_warehouse,
                        qty=1,
                    )
                )

                items.append(
                    dict(
                        item_code=row.execution_item,
                        t_warehouse=self.billing_warehouse,
                        qty=1,
                    )
                )
        doc = frappe.get_doc(
            dict(
                doctype="Stock Entry",
                stock_entry_type="Manufacture",
                posting_date=self.date,
                items=items,
                debtor_entry=self.name,
            )
        )
        doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_site_warehouse(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """select target_warehouse as 'name' from `tabPortion Traceability` where debtors_entry is null and target_warehouse is not null""",
        as_list=1,
    )


@frappe.whitelist()
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
    if not filters.get("target_warehouse"):
        frappe.throw("Select Site Warehouse First")
    return frappe.db.sql(
        """select distinct batch_no as 'name' from `tabPortion Traceability` where debtors_entry is null and current_warehouse=%s""",
        filters.get("target_warehouse"),
        as_list=1,
    )
