// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Send SMS', {
	message_format: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		frm.call({
			method:"get_variables",
			doc: frm.doc,
			callback:function(r){
				frm.refresh_field("message_variable");
			}
		})
	}
});
