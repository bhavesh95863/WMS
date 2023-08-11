// Copyright (c) 2022, Bhavesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Portion Traceability', {
	open_location: function (frm) {
		window.open("https://www.google.com/maps/search/?api=1&query=" + frm.doc.location_of_weld, '_blank');
	}
});
