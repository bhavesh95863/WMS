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
	},
});

frappe.ui.form.on('Group Details', {
	fetch_updated_mobile_no: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn]
		frappe.call({
			method:"wms.wms.doctype.group.group.update_new_mobile_no",
			args:{'document_type':doc.group_type,'document_id':doc.link,'group_detail_id':doc.name},
			freeze:true,
			freeze_message:'Getting Updated Details',
			callback:function(r){
				if(r.message){
					// frm.refresh_field('mobile')
					// frappe.model.set_value(cdt,cdn,"mobile",r.message.mobile)
					// frappe.model.set_value(cdt,cdn,"mobile2",r.message.mobile2)
					// frappe.model.set_value(cdt,cdn,"mobile3",r.message.mobile3)

					cur_frm.refresh_field('table_9')
					cur_frm.reload_doc()
				}
			}

		})
	}
})
