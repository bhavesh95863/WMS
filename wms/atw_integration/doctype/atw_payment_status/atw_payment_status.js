// Copyright (c) 2022, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('ATW Payment Status', {
	setup: function (frm) {
		frm.set_query("billing_warehouse", function () {
			return {
				query: "wms.atw_integration.doctype.atw_payment_status.atw_payment_status.get_site_warehouse",
			}
		});
		frm.set_query("execution_item", function () {
			return {
				query: "wms.atw_integration.doctype.atw_payment_status.atw_payment_status.get_execution_items"
			}
		});
	},
	populate_data: function (frm) {
		frm.call({
			method: "populate_data",
			doc: frm.doc,
			callback: function (r) {
				// frm.reload_doc()
			}
		})
	},
	check_all: function (frm) {
		frm.call({
			method: "check_all",
			doc: frm.doc,
			freeze: true,
			freeze: "Updating..",
			callback: function (r) {
				frm.refresh_field("details");
				// frm.reload_doc()
			}
		})
	},
	uncheck_all: function (frm) {
		frm.call({
			method: "uncheck_all",
			doc: frm.doc,
			freeze: true,
			freeze: "Updating..",
			callback: function (r) {
				frm.refresh_field("details");
				// frm.reload_doc()
			}
		})
	},
});
