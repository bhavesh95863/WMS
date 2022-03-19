// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group', {
	group_type: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		frm.call({
			method:"get_group_type_details",
			doc: frm.doc,
			freeze:true,
			freeze_message:"Fetching Data ...",
			callback:function(r){
				frm.refresh_field("table_9");
			}
		})
	},
	enable_all: function(frm){
		frm.call({
			method:"enable_all",
			doc: frm.doc,
			freeze: true,
			freeze:"Enabling All..",
			callback:function(r){
				frm.refresh_field("table_9");
			}
		})
	},
	disable_all: function(frm){
		frm.call({
			method:"disable_all",
			doc: frm.doc,
			freeze: true,
			freeze:"Disabling All..",
			callback:function(r){
				frm.refresh_field("table_9");
			}
		})
	}
});
