import frappe
from frappe import _

def on_submit_payment_transfer(self,method):
    if not self.from_customer == self.to_customer:
        frappe.throw(_("From Customer And To Customer Must be same"))