frappe.ui.form.on('Program', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Go to Course'), function() {
                frappe.db.get_value(
                    'Course',
                    { course_name: frm.doc.program_name },
                    'name'
                ).then(r => {
                    if (r.message && r.message.name) {
                        frappe.set_route(
                            'Form',
                            'Course',
                            r.message.name
                        );
                    } else {
                        frappe.msgprint(__('Course not found'));
                    }
                });
            });
        }
    }
});