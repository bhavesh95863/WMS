import frappe
from frappe.utils import today, getdate, cint, now, add_days, parse_val,add_to_date,nowdate
from frappe.utils.safe_exec import get_safe_globals


def create_task_for_event(doc, method):
	try:
		if (frappe.flags.in_import and frappe.flags.mute_emails) or frappe.flags.in_patch or frappe.flags.in_install:
			return
		get_task_template(doc, doc.doctype, method)
	except Exception as e:
		frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())


def trigger_daily_alerts():
	try:
		trigger_notifications(None, "daily")
	except Exception as e:
		frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())

def trigger_notifications(doc, method=None):
	if frappe.flags.in_import or frappe.flags.in_patch:
		# don't send notifications while syncing or patching
		return

	if method == "daily":
		doc_list = frappe.get_all('WMS Task Rule',
			filters={
				'based_on': ('in', ('Days Before', 'Days After')),
				'enabled': 1
			})
		for d in doc_list:
			print(d.name)
			task_rule = frappe.get_doc("WMS Task Rule", d.name)

			for task in get_documents_for_today(task_rule):
				evalute_daily_task(task,d.based_on,task_rule)
				frappe.db.commit()

def get_documents_for_today(self):
	print('call')
	'''get list of documents that will be triggered today'''
	docs = []

	diff_days = self.days_in_advance
	if self.based_on=="Days After":
		diff_days = -diff_days

	reference_date = add_to_date(nowdate(), days=diff_days)
	print(reference_date)
	reference_date_start = reference_date + ' 00:00:00.000000'
	reference_date_end = reference_date + ' 23:59:59.000000'

	doc_list = frappe.get_all(self.ref_doctype,
		fields='name',
		filters=[
			{ self.date_changed: ('>=', reference_date_start) },
			{ self.date_changed: ('<=', reference_date_end) }
		])
	print(doc_list)
	for d in doc_list:
		doc = frappe.get_doc(self.ref_doctype, d.name)

		if self.condition and not frappe.safe_eval(self.condition, None, get_context(doc)):
			continue

		docs.append(doc)

	return docs


def create_task_for_recurring():
	try:
		templates = []
		tasks = frappe.get_all("WMS Task Rule", filters={
							"recurring": 1}, fields=["*"])
		for row in tasks:
			if row.frequency == "Daily":
				templates.append(row)
			if row.frequency == "Monthly":
				today_day = getdate(today()).day
				if cint(today_day) == cint(row.date_of_month):
					templates.append(row)
			if row.frequency == "Weekly":
				today_day_name = getdate(today()).strftime('%A')
				if today_day_name == row.day_of_week:
					templates.append(row)
			if row.frequency == "Yearly":
				today_day = getdate(today()).day
				today_month = getdate(today()).month
				if cint(today_day) == cint(row.date_of_month) and cint(today_month) == cint(row.month_of_year):
					templates.append(row)
		evalute_recuring_task(templates)
	except Exception as e:
		frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())

def get_task_template(self, doctype, method):
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
	tasks = frappe.get_all("WMS Task Rule", filters={
						   "based_on": based_on, "ref_doctype": doctype, "enabled":1}, fields=["*"])
	if tasks:
		evalute_event_task(self, based_on, tasks)


def evalute_event_task(self, based_on, tasks):
	context = get_context(self)
	for task in tasks:
		if based_on == "Value Change" and not self.is_new():
			if not frappe.db.has_column(self.doctype, task.fields):
				continue
			else:
				doc_before_save = self.get_doc_before_save()
				field_value_before_save = doc_before_save.get(
					task.fields) if doc_before_save else None
				field_value_before_save = parse_val(field_value_before_save)
				if (self.get(task.fields) == field_value_before_save):
					# value not changed
					continue
				else:
					create_task(task, "ERP", context)
		else:
			create_task(task, "ERP", context)

def evalute_daily_task(self, based_on, task):
	# for task in tasks:
	context = get_context(self)
	if based_on == "Value Change" and not self.is_new():
		if not frappe.db.has_column(self.doctype, task.fields):
			return
		else:
			doc_before_save = self.get_doc_before_save()
			field_value_before_save = doc_before_save.get(
				task.fields) if doc_before_save else None
			field_value_before_save = parse_val(field_value_before_save)
			if (self.get(task.fields) == field_value_before_save):
				# value not changed
				return
			else:
				create_task(task, "ERP", context)
	else:
		create_task(task, "ERP", context)



def evalute_recuring_task(tasks):
	for task in tasks:
		create_task(task, "Recurring")


def create_task(task, task_type, context=None):
	# context = get_context(task)
	if context and task.condition:
		if not frappe.safe_eval(task.condition, None, context):
			return
	doc = frappe.get_doc(dict(
		doctype="WMS Task",
		date_of_issue=now(),
		due_date=add_days(today(), task.get('due_days')),
		source=task_type,
		details= frappe.render_template(task.get('task_details'),context) if context else task.get('task_details'),
		task_title=task.get('task_title'),
		assign_to=task.get('assign_to'),
		assign_by=task.get('assign_from')
	)).insert(ignore_permissions=True)

def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe": frappe._dict(utils=get_safe_globals().get("frappe").get("utils"))}

@frappe.whitelist()
def update_task_status():
	filters = [
		["status","not in",["Completed"]]
	]
	tasks = frappe.get_all("WMS Task",filters=filters,fields=["name"])
	for task in tasks:
		task_doc = frappe.get_doc("WMS Task",task.name)
		old_status = task_doc.status
		task_doc.validate()
		if not task_doc.status == old_status:
			try:
				task_doc.save()
			except Exception as e:
				frappe.log_error(title='WMS Error Log', message=frappe.get_traceback())