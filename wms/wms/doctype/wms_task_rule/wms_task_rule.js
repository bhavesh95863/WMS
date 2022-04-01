// Copyright (c) 2021, Bhavesh and contributors
// For license information, please see license.txt


frappe.ui.form.on('WMS Task Rule', {
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
			let get_date_change_options = function() {
				let date_options = $.map(fields, function(d) {
					return d.fieldtype == 'Date' || d.fieldtype == 'Datetime'
						? get_select_options(d)
						: null;
				});
				// append creation and modified date to Date Change field
				return date_options.concat([
					{ value: 'creation', label: `creation (${__('Created On')})` },
					{ value: 'modified', label: `modified (${__('Last Modified Date')})` }
				]);
			};

			let fields = frappe.get_doc('DocType', frm.doc.ref_doctype).fields;
			let options = $.map(fields, function (d) {
				return in_list(frappe.model.no_value_type, d.fieldtype)
					? null : get_select_options(d);
			});

			// set value changed options
			frm.set_df_property('fields', 'options', [''].concat(options));
			frm.set_df_property('date_changed', 'options', get_date_change_options());


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
		if ((!frm.doc.__islocal) && (!frappe.user.has_role("System Manager"))){
			console.log('asd')
			let meta = frappe.get_meta("WMS Task Rule");
			meta.fields.forEach(value => {
				if (!["Section Break", "Column Break"].includes(value.fieldtype)) {
					frm.set_df_property(value.fieldname,'read_only', 1);
				}
			});
		}
	},
	ref_doctype: function (frm) {
		frm.trigger('setup_fieldname_select')
	}
});