from re import template
import frappe
from frappe import _
import json
from frappe.utils import today, getdate, cint, now, add_days, parse_val
import requests

def send_message_for_event(doc, method):
    if (frappe.flags.in_import and frappe.flags.mute_emails) or frappe.flags.in_patch or frappe.flags.in_install:
        return
    get_message_rule(doc, doc.doctype, method)

def get_message_rule(self, doctype, method):
    event_map = {
        "on_submit": "Submit",
        "after_insert": "New",
        "on_cancel": "Cancel",
        "after_save": "Save"
    }
    if not self.flags.in_insert:
        # value change is not applicable in insert
        event_map['on_change'] = 'Value Change'
    based_on = event_map.get(method)
    if not based_on:
        return
    rules = frappe.get_all("Message Rule", filters={
                           "based_on": based_on, "ref_doctype": doctype}, fields=["*"])
    if rules:
        evalute_message_rule(self, based_on, rules)


def evalute_message_rule(self, based_on, rules):
    for rule in rules:
        if based_on == "Value Change" and not self.is_new():
            if not frappe.db.has_column(self.doctype, rule.fields):
                continue
            else:
                doc_before_save = self.get_doc_before_save()
                field_value_before_save = doc_before_save.get(
                    rule.fields) if doc_before_save else None
                field_value_before_save = parse_val(field_value_before_save)
                if (self.get(rule.fields) == field_value_before_save):
                    # value not changed
                    continue
                else:
                    send_message_using_template(self,rule)
        else:
            send_message_using_template(self,rule)


def send_message_using_template(self,rule):
    template_doc = frappe.get_doc("Message Template",rule.message_template)
    if rule.whatsapp:
        data = []
        for field in template_doc.template_variables.split(","):
            data.append({
                'name': field,
                'value': self.get(field)
            })
        send_whatsapp_message(template_doc.template_name,self.get(rule.mobile_no_field),json.dumps(data),self.name)
    if rule.sms:
        data = {}
        for field in template_doc.template_variables.split(","):
            data[field] = self.get(field)
        message = frappe.render_template(template_doc.template_message,data)
        receiver_list = []
        receiver_list.append(self.get(rule.mobile_no_field))
        send_sms_message(message,receiver_list)

def send_sms_message(message,receiver_list):
    from frappe.core.doctype.sms_settings.sms_settings import send_sms
    send_sms(receiver_list,message)

def send_whatsapp_message(template,mobile,data,document):
    # template = "new_referral_introduction"
    # mobile = "916359985959"
    # data = json.dumps([{'name':'company','value':'Oberoi Thermit Pvt. Ltd.'}])
    whatsapp_setting = frappe.get_doc("WhatsApp Setting","WhatsApp Setting")
    base_url = whatsapp_setting.get('url') + "/api/v1/sendTemplateMessage/" + whatsapp_setting.get('whatsapp_number') + "?whatsappNumber=" + mobile
    payload = json.dumps({
    "template_name": template,
    "broadcast_name": template,
    "parameters": data
    })
    headers = {
    'Authorization': 'Bearer ' + whatsapp_setting.token,
    'Content-Type': 'application/json',
    'Cookie': 'affinity=1640466569.646.162034.484452'
    }

    response = requests.request("POST", base_url, data=payload, headers=headers)
    # frappe.log_error(response)
    frappe.get_doc(dict(
        doctype = "Whatsapp Message Log",
        mobile_no = mobile,
        url = base_url,
        payload = payload,
        headers = json.dumps(headers),
        status_code = response.status_code,
        response = response.text,
        document = document

    )).insert(ignore_permissions = True)
    frappe.msgprint(_('Whatsapp Message sent on {0}').format(mobile), alert=True, indicator='green')
    # print(response.text)

