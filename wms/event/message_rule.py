from re import template
import frappe
from frappe import _
import json
from frappe.utils import today, getdate, cint, now, add_days, parse_val, cstr,nowdate
import requests
from frappe.utils.safe_exec import get_safe_globals
from frappe import _

def send_message_for_event(doc, method):
    try:
        if (frappe.flags.in_import and frappe.flags.mute_emails) or frappe.flags.in_patch or frappe.flags.in_install:
            return
        get_message_rule(doc, doc.doctype, method)
    except Exception as e:
        frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())

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
                           "based_on": based_on, "ref_doctype": doctype, "enable":1}, fields=["*"])
    if rules:
        evalute_message_rule(self, based_on, rules)


def evalute_message_rule(self, based_on, rules):
    for rule in rules:
        context = get_context(self)
        if context and rule.conditions:
            if not frappe.safe_eval(rule.conditions, None, context):
                return
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

def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe": frappe._dict(utils=get_safe_globals().get("frappe").get("utils"))}


def send_message_using_template(self,rule):
    rule = frappe.get_doc("Message Rule",rule.name)
    template_doc = frappe.get_doc("Message Template",rule.message_template)
    so_fields = ["mobile1","mobile2","mobile3"]
    if rule.whatsapp:
        data = []
        for field in rule.template_variable:
            data.append({
                'name': field.get('template_variable'),
                'value': self.get(field.get('document_variable'))
            })
        if rule.rule_based_on == "Sales Order":
            if rule.ref_doctype == "Sales Order":
                so_doc = self
            else:
                so_doc = frappe.get_doc("Sales Order",self.get(rule.sales_order_field))
            for mobile in so_fields:
                if so_doc.get(mobile):
                    send_whatsapp_message(template_doc.template_name,so_doc.get(mobile),json.dumps(data),self.name)
        else:
            foreign = False
            if self.doctype == "WMS Lead" and self.type_of_contract == "Foreign":
                foreign = True
            send_whatsapp_message(template_doc.template_name,self.get(rule.mobile_no_field),json.dumps(data),self.name,foreign=foreign)

    if rule.sms:
        data = {}
        for field in rule.template_variables.split(","):
            data[field] = self.get(field)
        message = frappe.render_template(template_doc.template_message,data)
        receiver_list = []
        if rule.rule_based_on == "Sales Order":
        
            if rule.ref_doctype == "Sales Order":
                so_doc = self
            else:
                so_doc = frappe.get_doc("Sales Order",self.get(rule.sales_order_field))
            for mobile in so_fields:
                if so_doc.get(mobile):
                    receiver_list.append(so_doc.get(mobile))
        else:
            receiver_list.append(self.get(rule.mobile_no_field))
        send_sms_message(message,receiver_list)


def send_sms_message(message,receiver_list):
    from frappe.core.doctype.sms_settings.sms_settings import send_sms
    send_sms(receiver_list,message)

def send_whatsapp_message(template,mobile,data,document,foreign=False):
    if not foreign:
        mobile = '91' + cstr(mobile)
    whatsapp_setting = frappe.get_doc("WhatsApp Setting","WhatsApp Setting")
    base_url = whatsapp_setting.get('url') + "/api/v1/sendTemplateMessage/" + mobile + "?whatsappNumber=" + whatsapp_setting.get('whatsapp_number')
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
