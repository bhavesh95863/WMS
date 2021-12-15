# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "wms"
app_title = "WMS"
app_publisher = "Bhavesh"
app_description = "WMS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "maheshwaribhavesh95863@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/wms/css/wms.css"
# app_include_js = "/assets/wms/js/wms.js"

# include js, css files in header of web template
# web_include_css = "/assets/wms/css/wms.css"
# web_include_js = "/assets/wms/js/wms.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "wms.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "wms.install.before_install"
# after_install = "wms.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "wms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_submit": "wms.event.task.create_task_for_event",
		"after_insert": "wms.event.task.create_task_for_event",
		"on_cancel": "wms.event.task.create_task_for_event",
        "after_save":"wms.event.task.create_task_for_event",
		"on_change":"wms.event.task.create_task_for_event"
	}
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"daily": [
		"wms.event.task.create_task_for_recurring"
	]
}
# scheduler_events = {
# 	"all": [
# 		"wms.tasks.all"
# 	],
# 	"daily": [
# 		"wms.tasks.daily"
# 	],
# 	"hourly": [
# 		"wms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"wms.tasks.weekly"
# 	]
# 	"monthly": [
# 		"wms.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "wms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "wms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "wms.task.get_dashboard_data"
# }

