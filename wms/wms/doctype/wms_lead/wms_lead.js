// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('WMS Lead', {
	refresh: function(frm) {
		if ((!frm.doc.__islocal) && (!frappe.user.has_role("System Manager"))){
			let meta = frappe.get_meta("WMS Lead");
			meta.fields.forEach(value => {
				if (!["Section Break", "Column Break"].includes(value.fieldtype)) {
					frm.set_df_property(value.fieldname,'read_only', 1);
				}
			});
		}
	}
});
