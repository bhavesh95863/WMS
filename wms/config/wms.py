from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("WMS"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "type": "doctype",
                    "name": "WMS Lead",
                    "label": _("WMS Lead")
                },
                {
                    "type": "doctype",
                    "name": "Send SMS",
                    "label": _("Send SMS")
                },
                {
                    "type": "doctype",
                    "name": "Message Template",
                    "label": _("Message Template")
                },
                {
                    "type": "doctype",
                    "name": "Group",
                    "label": _("Group")
                },
                {
                    "type": "doctype",
                    "name": "WhatsApp Setting",
                    "label": _("WhatsApp Setting")
                },
                {
                    "type": "doctype",
                    "name": "WMS Task",
                    "label": _("Task")
                },
                {
                    "type": "doctype",
                    "name": "WMS Task Rule",
                    "label": _("Task Rule")
                },
                {
                    "type": "doctype",
                    "name": "Message Rule",
                    "label": _("Message Rule")
                }  
            ]
        },
        {
            "label": _("Reports"),
            "icon": "octicon octicon-briefcase",
            "items": [
				{
					"type": "report",
					"name": "Performance Report",
					"doctype": "WMS Task",
					"is_query_report": True
				},
                {
                    "type": "doctype",
                    "name": "Whatsapp Message Log",
                    "label": _("Whatsapp Message Log")
                }  

            ]
        },
        {
            "label": _("ATW Integration"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "type": "doctype",
                    "name": "ATW Manf Traceability",
                    "label": _("ATW Manf Traceability")
                },
                {
                    "type": "doctype",
                    "name": "Sales Order Traceability",
                    "label": _("Sales Order Traceability")
                },
                {
                    "type": "doctype",
                    "name": "Material Transfer Traceability",
                    "label": _("Material Transfer Traceability")
                },
                {
                    "type": "doctype",
                    "name": "Debtors Entry",
                    "label": _("Debtors Entry")
                },
                {
                    "type": "doctype",
                    "name": "ATW Welding",
                    "label": _("ATW Welding")
                },
                {
                    "type": "doctype",
                    "name": "Portion Traceability",
                    "label": _("Portion Traceability")
                },
                {
                    "type": "doctype",
                    "name": "USFD Test Result",
                    "label": _("USFD Test Result")
                },
                {
                    "type": "doctype",
                    "name": "ATW Payment Status",
                    "label": _("ATW Payment Status")
                },
                {
                    "type": "doctype",
                    "name": "ATW App Settings",
                    "label": _("ATW App Settings")
                },
                {
                    "type": "doctype",
                    "name": "ATW Question",
                    "label": _("ATW Question")
                },
                {
                    "type": "doctype",
                    "name": "ATW Exam",
                    "label": _("ATW Exam")
                }  
            ]
        },
    ]
