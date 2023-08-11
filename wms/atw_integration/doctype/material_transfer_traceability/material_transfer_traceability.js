// Copyright (c) 2022, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Transfer Traceability', {
	setup: function (frm) {
		frm.set_query("execution_item", function () {
			return {
				query: "wms.atw_integration.doctype.material_transfer_traceability.material_transfer_traceability.get_execution_item",
				filters: { "sales_order": frm.doc.dispatch_sales_order }
			}
		});
		frm.set_query("target_warehouse", function () {
			return {
				filters: {
					"sales_order": frm.doc.dispatch_sales_order
				}
			}

		})
	},
	batch_no: function (frm) {
		frm.call({
			method: "get_portion_no",
			doc: frm.doc,
			callback: function (r) {
				console.log(r)
				if (r.message) {
					set_field_options("portion_no_from", r.message.join("\n"));
					set_field_options("portion_no_to", r.message.join("\n"));
				} else {
					set_field_options("portion_no_from", "");
					set_field_options("portion_no_to", "");
				}

			}
		})
	},
	source_warehouse: function (frm) {
		frm.call({
			method: "get_portion_no",
			doc: frm.doc,
			callback: function (r) {
				console.log(r)
				if (r.message) {
					set_field_options("portion_no_from", r.message.join("\n"));
					set_field_options("portion_no_to", r.message.join("\n"));
				} else {
					set_field_options("portion_no_from", "");
					set_field_options("portion_no_to", "");
				}

			}
		})
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
