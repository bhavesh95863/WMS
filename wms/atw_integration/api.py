import frappe
from frappe.utils import cstr
from bs4 import BeautifulSoup


def gen_response(status, message, data=[]):
	frappe.response['http_status_code'] = status
	if status == 500:
		frappe.response['message'] = BeautifulSoup(str(message)).get_text()
	else:
		frappe.response['message'] = message
	frappe.response['data'] = data


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
	try:
		employee = frappe.db.get_value("Employee",{"welder_no":usr},"name")
		if not employee:
			return gen_response(500, "Invalid Username")
		employee_doc = frappe.get_doc("Employee",employee)
		if not employee_doc.get_password("password") == pwd:
			return gen_response(500, "Invalid Password")
		settings = frappe.get_doc("ATW App Settings","ATW App Settings")
		data = dict(
			api_key = settings.api_key,
			secret_key = settings.get_password("secret_key"),
			employee_id = employee_doc.name
		)
		gen_response(200,"logged in successfully",data)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def get_batch_list(employee):
	try:
		warehouse = frappe.db.get_value("Warehouse",{"employee":employee},"name")
		if not warehouse:
			return gen_response(200, "No any linked warehouse with loggedin user",[])
		batches = frappe.db.sql("""select distinct batch_no as 'batch_no' from `tabPortion Traceability` where target_warehouse=%s""",warehouse,as_dict=1)
		return gen_response(200,"Batch List Get Successfully",batches)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def get_portion_list(employee,batch_no):
	try:
		warehouse = frappe.db.get_value("Warehouse",{"employee":employee},"name")
		if not warehouse:
			return gen_response(200, "No any linked warehouse with loggedin user",[])
		portions = frappe.db.sql("""select distinct portion_no as 'portion_no',welding as 'welding',welding_tolerance 'tolerance' from `tabPortion Traceability` where target_warehouse=%s and batch_no=%s""",(warehouse,batch_no),as_dict=1)
		return gen_response(200,"Portions List Get Successfully",portions)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def crate_welding(**kwargs):
	try:
		data = frappe._dict(kwargs)
		doc = frappe.new_doc("ATW Welding")
		doc.actual_welder = data.get("employee")
		doc.date_of_welding = data.get("date_of_welding")
		doc.pwi = data.get("pwi")
		doc.aenxen = data.get("aenxen")
		doc.kmtp = data.get("kmtp")
		doc.lhrh = data.get("lhrh")
		doc.batch_no = data.get("batch_no")
		doc.portion = data.get("portion")
		doc.insert(ignore_permissions = True)
		return gen_response(200,"Welding created Successfully")
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))