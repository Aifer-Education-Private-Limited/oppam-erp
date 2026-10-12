frappe.ui.form.on('Course Topic', {
    custom_go_to_topics(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        if (!row.topic) {
            frappe.msgprint(__('Please select a Topic first.'));
            return;
        }

        frappe.set_route(
            'Form',
            'Topic',
            row.topic
        );
    }
});