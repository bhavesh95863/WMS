// Copyright (c) 2016, Bhavesh and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Performance Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "User",
			"get_query": function() {
				var admin_role = false;
				if (frappe.user.has_role("WMS Admin") || frappe.user.has_role("System Manager")){
					admin_role = true
				}
				if(!admin_role) {
					return {
						query: "wms.wms.doctype.wms_task.wms_task.get_users",
						filters: {}
						}
				}
			},
		}
	]
};
