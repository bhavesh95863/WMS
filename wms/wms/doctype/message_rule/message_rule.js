// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Message Rule', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Message Rule', {
	setup_fieldname_select: function (frm) {
		console.log('call')
		// get the doctype to update fields
		if (!frm.doc.ref_doctype) {
			return;
		}

		frappe.model.with_doctype(frm.doc.ref_doctype, function () {
			let get_select_options = function (df, parent_field) {
				// Append parent_field name along with fieldname for child table fields
				let select_value = parent_field ? df.fieldname + ',' + parent_field : df.fieldname;

				return {
					value: select_value,
					label: df.fieldname + ' (' + __(df.label) + ')'
				};
			};


			let fields = frappe.get_doc('DocType', frm.doc.ref_doctype).fields;
			let options = $.map(fields, function (d) {
				return in_list(frappe.model.no_value_type, d.fieldtype)
					? null : get_select_options(d);
			});

			// set value changed options
			frm.set_df_property('fields', 'options', [''].concat(options));
			frm.set_df_property('mobile_no_field', 'options', [''].concat(options));



		});
	},
	onload: function (frm) {
		frm.set_query('ref_doctype', function () {
			return {
				filters: {
					istable: 0
				}
			};
		});
	},
	refresh: function (frm) {
		frm.trigger('setup_fieldname_select')
	},
	ref_doctype: function (frm) {
		frm.trigger('setup_fieldname_select')
	}
});