// Copyright (c) 2022, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order Traceability', {
	batch_no: function (frm) {
		frm.call({
			method: "get_portion_no",
			doc: frm.doc,
			callback: function (r) {
				console.log(r)
				if (r.message) {
					set_field_options("portion_no_from", r.message.join("\n"));
					set_field_options("portion_no_to", r.message.join("\n"));
				}

			}
		})
	},
	setup: function (frm) {
		// frm.set_query("batch_no", function () {
		// 	return {
		// 		query: "wms.atw_integration.doctype.sales_order_traceability.sales_order_traceability.get_batch_no",
		// 	}
		// });
		// frm.set_query("inspection_sales_order", function() {
		// 	return {
		// 		query: "wms.atw_integration.doctype.sales_order_traceability.sales_order_traceability.get_sales_order",
		// 	}
		// });
	},
	populate_data: function (frm) {
		frm.call({
			method: "populate_data",
			doc: frm.doc,
			callback: function (r) {
				frm.reload_doc()
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
				frm.reload_doc()
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
				frm.reload_doc()
			}
		})
	},
});
