// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('WMS Task', {
	refresh(frm,cdt,cdn) {
		// your code here
		frm.trigger("make_fields_readonly")
	},
	after_save:function(frm,cdt,cdn) {
		frm.trigger("make_fields_readonly")
	},
	onload:function(frm,cdt,cdn) {
		if(frm.doc.__islocal){
			frappe.model.set_value(cdt,cdn,"assign_by",frappe.session.user)
		}
		frm.trigger("make_fields_readonly")
	},
	make_fields_readonly:function(frm,cdt,cdn) {
		if ((!frm.doc.__islocal) && (!frappe.user.has_role("WMS Admin") || !frappe.user.has_role("System Manager"))){
			let meta = frappe.get_meta("WMS Task");
			meta.fields.forEach(value => {
				if (!["Section Break", "Column Break"].includes(value.fieldtype)) {
					if(frm.doc.status == "Extend Required" && frappe.user.has_role("WMS Admin") && value.fieldname != "date_extend_request")
					frm.set_df_property(value.fieldname,'read_only', 1);
				}
			});
		}
	},
	approve:function(frm){
		frm.call({
			doc:frm.doc,
			method:'approve_extend_request',
			freeze:true,
			callback:function(r){
				frm.refresh()
			}
		})
	},
	reject:function(frm){
		frm.call({
			doc:frm.doc,
			method:'reject_extend_request',
			freeze:true,
			callback:function(r){
				frm.refresh()
			}
		})
	},
	refresh: function(frm) {
		if((frm.doc.status == "Not Yet Due" || frm.doc.status == "Due Today" || frm.doc.status == "Without Due Date" || frm.doc.status == "Overdue") && frm.doc.assign_to == frappe.session.user) {
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
			if(frm.doc.status != "Overdue" && frm.doc.assign_to == frappe.session.user) {
				frm.add_custom_button(__('Date Extend'), function() {
					const dialog = new frappe.ui.Dialog({
						title: __("Select Difference Account"),
						fields: [
							{
								fieldtype:'Date',
								fieldname:"extend_date",
								label: __("Extend Date")
							},
							{
								fieldtype:'Small Text',
								fieldname:"reason",
								label: __("Reason")
							}
						],
						primary_action: (data) => {
							dialog.hide();
							frm.call({
								method:'wms.wms.doctype.wms_task.wms_task.extend_date_request',
								args:{"task_id":frm.doc.name,"date":data.extend_date,"reason":data.reason},
								freeze:true,
								callback:function(r){
									frm.refresh()
								}
							})
						},
						primary_action_label: __('Extend')
					});
		
		
					dialog.show();
	
				});
			}
		}
		if(frm.doc.status == "Ontime" || frm.doc.status == "Late") {
			if(frappe.user.has_role('WMS Admin') || frappe.user.has_role('WMS Manager')){
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
	}
});
