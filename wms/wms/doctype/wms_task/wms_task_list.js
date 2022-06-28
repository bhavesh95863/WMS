frappe.listview_settings["WMS Task"] = {
	onload: function (listview) {
    listview.page.add_menu_item(__("Assigned To Me"), function() {
        listview.filter_area.clear();
		listview.filter_area.add([[listview.doctype, "assign_to", '=',  frappe.session.user]]);
    });
    listview.page.add_menu_item(__("Assigned By Me"), function() {
        listview.filter_area.clear();
		listview.filter_area.add([[listview.doctype, "assign_by", 'like',  '%' + frappe.session.user + '%']]);
     });

}
}