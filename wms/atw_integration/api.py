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
		portions = frappe.db.sql("""select distinct portion_no as 'portion_no',welding as 'welding',welding_tolerance 'tolerance',welding as 'welding_sync',welding_tolerance 'tolerance_tolerance' from `tabPortion Traceability` where target_warehouse=%s and batch_no=%s""",(warehouse,batch_no),as_dict=1)
		return gen_response(200,"Portions List Get Successfully",portions)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def crate_welding(**kwargs):
	try:
		data = frappe._dict(kwargs)
		if frappe.db.exists("ATW Welding",{"batch_no":data.get("batch_no"),"portion": data.get("portion")}):
			return gen_response(500,"Welding already created")
		doc = frappe.new_doc("ATW Welding")
		doc.actual_welder = data.get("employee")
		doc.date_of_welding = data.get("date_of_welding")
		doc.pwi = data.get("pwi")
		doc.aenxen = data.get("aenxen")
		doc.kmtp = data.get("kmtp")
		doc.lhrh = data.get("lhrh")
		doc.batch_no = data.get("batch_no")
		doc.portion = data.get("portion")
		doc.weld_no = data.get("weld_no")
		doc.auto_gen_id = data.get("auto_gen_id")
		doc.welder_code = frappe.db.get_value("Employee",data.get("employee"),"welder_no")
		res = doc.insert(ignore_permissions = True)
		file_url = upload_photo(data.get("photo_content"),data.get("file_name"),"portion_slip_photo",res.doctype,res.name)
		frappe.db.set_value("Portion Traceability",data.get("portion"),"portion_slip_photo_link",file_url)
		return gen_response(200,"Welding created Successfully")
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))


@frappe.whitelist()
def create_tolerance(**kwargs):
	try:
		data = frappe._dict(kwargs)
		if not data.get("weld_no"):
			return gen_response(500, "Weld No Must Required")
		if not frappe.db.exists("ATW Welding",data.get("weld_no")):
			return gen_response(500, "Welding No Incorrect")
		doc = frappe.get_doc("ATW Welding",data.get("weld_no"))
		doc.tolerance_1_mtr_vertical = data.get("tolerance_1_mtr_vertical")
		doc.tolerance_10cm_vertical = data.get("tolerance_10cm_vertical")
		doc.tolerance_1_mtr_horizontal = data.get("tolerance_1_mtr_horizontal")
		doc.tolerance_10cm_horizontal = data.get("tolerance_10cm_horizontal")
		doc.location_of_weld = cstr(data.get('latitude')) + ',' + cstr(data.get('longitude'))
		doc.tolerance = 1
		res = doc.save(ignore_permissions = True)
		file_url = upload_photo(data.get("photo_content"),data.get("file_name"),"photo_of_weld",res.doctype,res.name)
		frappe.db.set_value("Portion Traceability",doc.get("portion"),"photo_of_weld",file_url)
		return gen_response(200,"Tolerance updated successfully")
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))


@frappe.whitelist()
def upload_photo(content,filename,fieldname,attached_to_doctype,attached_to_name):
	import base64

	ret = frappe.get_doc({
		"doctype": "File",
		"attached_to_name": attached_to_name,
		"attached_to_doctype": attached_to_doctype,
		"attached_to_field": fieldname,
		"file_name": filename,
		"is_private": 0,
		"content": content,
		"decode": True
	})
	ret.save()
	frappe.db.commit()
	frappe.db.set_value(attached_to_doctype,attached_to_name,fieldname,ret.file_url)
	return ret.file_url
	# return ret

@frappe.whitelist()
def get_pwi_list():
	try:
		pwi_list = (frappe.get_meta("ATW Welding").get_field("pwi").options or "").split("\n")
		return gen_response(200,"PWI Get successfully",pwi_list)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def get_aenxen_list():
	try:
		pwi_list = (frappe.get_meta("ATW Welding").get_field("aenxen").options or "").split("\n")
		return gen_response(200,"PWI Get successfully",pwi_list)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))	

@frappe.whitelist()
def get_welding_no(employee_id):
	try:
		welding_list = frappe.get_all("ATW Welding",filters={"actual_welder":employee_id},fields=["name","tolerance"])
		return gen_response(200,"Welding Details Get Successfully",welding_list)
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))

@frappe.whitelist()
def get_settings(employee):
	try:
		settings = frappe.get_doc("ATW App Settings","ATW App Settings")
		return gen_response(200,"Settings Get Successfully",dict(
			sync_data = settings.get("sync_data")
		))
	except Exception as e:
		frappe.log_error(frappe.get_traceback())
		gen_response(500, cstr(e))
