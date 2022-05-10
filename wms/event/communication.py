from shutil import ExecError
import frappe
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlencode



@frappe.whitelist()
def after_insert_communication(self,method):
    if len(self.subject) >= 5 and self.subject[:5] == "Group":
        try:
            subject_split = self.subject.split(' ')
            group = subject_split[1]
            message_template = subject_split[2][1:]
            variables = get_variable_value(self.text_content)
            for index,el in enumerate(variables):
                if el == '':
                    variables.pop(index)
            doc = frappe.new_doc("Send SMS")
            doc.message_send_to = "Group"
            doc.when_to_send = "Now"
            doc.group = group
            doc.message_format = message_template
            doc.message = frappe.db.get_value("Message Template",message_template,"template_message")
            doc.get_variables()
            if len(doc.message_variable) >= 1 and not len(variables) >= 1:
                return
            for index,variable in enumerate(doc.message_variable):
                # value = BeautifulSoup(variables[index])
                variable.value = str(variables[index]).replace('\r\n','; ')
            doc.submit()
        except Exception as e:
            frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())

def get_variable_value(s):
    substring = []
    # s = html2text.html2text(s)
    def get_substring(s):
        start_string = '#$#'
        end_string = '#$#'

        start_index = s.find(start_string) + len(start_string)
        end_index = s[start_index:].find(end_string) + start_index
        var_string = s[start_index:end_index]
        if not var_string == '':
            substring.append(var_string)
        if (len(s[end_index + len(start_string):])) >= 3:
            get_substring(s[end_index:])
    get_substring(s)
    return substring

@frappe.whitelist()
def communication_test(communication):
    comm_doc = frappe.get_doc("Communication",communication)
    frappe.msgprint(comm_doc.content)
    return comm_doc.content



        