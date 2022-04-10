import frappe


@frappe.whitelist()
def get_order_items(sales_order):
    try:
        order_doc = frappe.get_doc("Sales Order",sales_order)
        items = []
        item_arr = []
        for item in order_doc.items:
            # if item.item_code in item_arr:
            #     for i in items:
            #         if item.item_code == i.get('item'):
            #             i['qty'] = i.get('qty') + item.qty
            # else:
            items.append(dict(
                item = item.item_code,
                qty = item.qty,
                uom = item.uom,
                rate = item.rate,
                sales_order = item.parent
            ))
                # item_arr.append(item.item_code)
        return items
    except Exception as e:
        frappe.log_error(frappe.get_traceback())

@frappe.whitelist()
def get_items_for_order_execution(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("order_no"):
		return []

	so_filter = [
		['parent', '=', filters.get("order_no")]
	]

	items = frappe.get_all(
		"Sales Order Item",
		fields=["item_code as 'name'"],
		filters=so_filter,
		limit_start=start,
		limit_page_length=page_len,
		as_list=1
	)
	return items



def on_update_order_execution(self,method):
    if len(self.totals) < 1:
        items = []
        item_arr = []
        for item in self.items_on_order:
            if item.item in item_arr:
                for i in items:
                    if item.item == i.get('item'):
                        i['qty'] = i.get('qty') + item.get('order_qty')
            else:
                items.append(dict(
                    item = item.item,
                    qty = item.order_qty
                ))
                item_arr.append(item.item)
        for row in items:
            self.append("totals",dict(
                item = row.get('item'),
                balance_to_weld = item.get('qty')
            ))
    for total_row in self.totals:
        total_weld = 0
        total_welds = frappe.get_all("Order Execution ATW Ledger ITEM Child",filters = {"parent":self.name,"item":total_row.item},fields=["order_qty"])
        for t_w in total_welds:
            total_weld += t_w.get("order_qty")
        total_weld_executed = total_usfd_executed = total_defective = total_paid = tested_balance_to_pay =  0
        weld_executed = frappe.get_all("Order Execution Ledger ATW Child",filters = {"parent":self.name,"item":total_row.item},fields=["qty_executed","usfd_tested","defective_jts","paid_qty"])
        for weld in weld_executed:
            total_weld_executed += weld.qty_executed
            total_usfd_executed += weld.usfd_tested
            total_defective += weld.defective_jts
            total_paid += weld.paid_qty
        total_row.balance_to_weld = total_weld - total_weld_executed
        tested_balance_to_pay = total_usfd_executed - total_defective - total_paid
        frappe.db.set_value(total_row.doctype,total_row.name,"total_welded",total_weld_executed)
        frappe.db.set_value(total_row.doctype,total_row.name,"balance_to_weld",total_row.balance_to_weld)
        frappe.db.set_value(total_row.doctype,total_row.name,"total_usfd_tested",total_usfd_executed)
        frappe.db.set_value(total_row.doctype,total_row.name,"total_defective",total_defective)
        frappe.db.set_value(total_row.doctype,total_row.name,"total_paid",total_paid)
        frappe.db.set_value(total_row.doctype,total_row.name,"tested_balance_to_pay",tested_balance_to_pay)
        balance_pay = total_weld_executed - total_paid - total_defective
        frappe.db.set_value(total_row.doctype,total_row.name,"balance_to_pay",balance_pay)
    if method == "on_change":
        self.reload()

            
