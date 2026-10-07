import frappe


def create_course_from_program(doc, method=None):
    if frappe.db.exists("Course", {"course_name": doc.program_name}):
        return

    course = frappe.new_doc("Course")
    course.course_name = doc.program_name
    course.insert(ignore_permissions=True)
