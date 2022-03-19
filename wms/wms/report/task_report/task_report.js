// Copyright (c) 2016, Bhavesh and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Task Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Not Yet Due\nDue Today\nWithout Due Date\nOntime\nLate\nOverdue"
		},
		{
			"fieldname":"user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User"
		}
	]
};
