// Copyright (c) 2022, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Transfer Traceability', {
	setup: function(frm) {
		frm.set_query("batch_no", function() {
			return {
				query: "wms.atw_integration.doctype.material_transfer_traceability.material_transfer_traceability.get_batch_no"
			}
		});
	},
	populate_data: function(frm) {
		frm.call({
			method:"populate_data",
			doc: frm.doc,
			callback:function(r){
				frm.reload_doc()
			}
		})
	},
	check_all: function(frm){
		frm.call({
			method:"check_all",
			doc: frm.doc,
			freeze: true,
			freeze:"Updating..",
			callback:function(r){
				frm.refresh_field("details");
				frm.reload_doc()
			}
		})
	},
	uncheck_all: function(frm){
		frm.call({
			method:"uncheck_all",
			doc: frm.doc,
			freeze: true,
			freeze:"Updating..",
			callback:function(r){
				frm.refresh_field("details");
				frm.reload_doc()
			}
		})
	},
});
