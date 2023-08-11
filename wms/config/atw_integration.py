from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("ATW Integration"),
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
        }
    ]
