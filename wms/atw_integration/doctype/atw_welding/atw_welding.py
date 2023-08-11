# -*- coding: utf-8 -*-
# Copyright (c) 2022, Bhavesh and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, cstr


class ATWWelding(Document):
    def autoname(self):
        if self.get("auto_gen_id"):
            self.name = self.get("auto_gen_id")
        else:
            self.name = (
                cstr(getdate(today()).month)
                + "-"
                + cstr(getdate(today()).year)
                + "-"
                + self.welder_code
                + "-"
                + self.weld_no
            )

    def after_insert(self):
        portion_doc = frappe.get_doc("Portion Traceability", self.portion)
        portion_doc.actual_welder = self.actual_welder
        portion_doc.weld_no = self.name
        portion_doc.date_of_welding = self.date_of_welding
        portion_doc.pwi = self.pwi
        portion_doc.aen_xen = self.aenxen
        portion_doc.km_tp = self.kmtp
        portion_doc.lh_rh = self.lhrh
        portion_doc.portion_slip_photo_link = self.portion_slip_photo
        portion_doc.welding = 1
        portion_doc.save(ignore_permissions=True)

    def on_update(self):
        if self.tolerance:
            portion_doc = frappe.get_doc("Portion Traceability", self.portion)
            portion_doc.tolerance_1_mtr_vertical = self.get("tolerance_1_mtr_vertical")
            portion_doc.tolerance_10cm_vertical = self.get("tolerance_10cm_vertical")
            portion_doc.tolerance_1_mtr_horizontal = self.get(
                "tolerance_1_mtr_horizontal"
            )
            portion_doc.tolerance_10cm_horizontal = self.get(
                "tolerance_10cm_horizontal"
            )
            portion_doc.location_of_weld = self.location_of_weld
            portion_doc.photo_of_weld = self.photo_of_weld
            portion_doc.welding_tolerance = 1
            portion_doc.location_link = "<a href='https://www.google.com/maps/search/?api=1&query={0}'.format(self.location_of_weld)>Weld Location</a>"
            portion_doc.date_of_entry_of_tolerances = self.date_of_entry_of_tolerances
            portion_doc.save(ignore_permissions=True)
