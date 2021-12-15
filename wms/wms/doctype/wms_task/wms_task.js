// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('WMS Task', {
	refresh: function(frm) {
		if(frm.doc.status == "Not Yet Due" || frm.doc.status == "Due Today" || frm.doc.status == "Without Due Date" || frm.doc.status == "Overdue") {
			frm.add_custom_button(__('Mark Complete'), function() {
				frm.call({
					doc:frm.doc,
					method:'mark_complete',
					freeze:true,
					callback:function(r){
						frm.refresh()
					}
				})
			});
		}
		if(frm.doc.status == "Ontime" || frm.doc.status == "Late") {
			frm.add_custom_button(__('Reopen'), function() {
				frm.call({
					doc:frm.doc,
					method:'mark_uncomplete',
					freeze:true,
					callback:function(r){
						frm.refresh()
					}
				})
			});
		}
	}
});
