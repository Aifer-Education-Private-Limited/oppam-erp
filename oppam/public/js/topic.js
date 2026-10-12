frappe.ui.form.on('Topic Content', {
    content_type(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Clear old content whenever Content Type changes
        frappe.model.set_value(
            cdt,
            cdn,
            'content',
            ''
        );
    },

    custom_go_to_content(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        if (!row.content_type) {
            frappe.msgprint(__('Please select Content Type first.'));
            return;
        }

        if (!row.content) {
            frappe.msgprint(__('Please select Content first.'));
            return;
        }

        frappe.set_route(
            'Form',
            row.content_type,
            row.content
        );
    }
});