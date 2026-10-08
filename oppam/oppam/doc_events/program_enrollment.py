import frappe


def create_course_enrollments(doc, method=None):
    if doc.custom_active:
        create_enrollments(doc)


def sync_course_enrollments(doc, method=None):
    if doc.custom_active:
        create_enrollments(doc)
    else:
        delete_enrollments(doc)


def create_enrollments(doc):
    if not doc.student:
        return

    if not doc.courses:
        return

    for row in doc.courses:
        if not row.course:
            continue

        existing_enrollment = frappe.db.exists(
            "Course Enrollment",
            {
                "program_enrollment": doc.name,
                "course": row.course
            }
        )

        if existing_enrollment:
            continue

        course_enrollment = frappe.new_doc("Course Enrollment")

        course_enrollment.program_enrollment = doc.name
        course_enrollment.course = row.course
        course_enrollment.student = doc.student
        course_enrollment.enrollment_date = doc.enrollment_date

        course_enrollment.insert(ignore_permissions=True)


def delete_enrollments(doc):
    enrollments = frappe.get_all(
        "Course Enrollment",
        filters={
            "program_enrollment": doc.name
        },
        pluck="name"
    )

    for enrollment_name in enrollments:
        course_enrollment = frappe.get_doc(
            "Course Enrollment",
            enrollment_name
        )

        if course_enrollment.docstatus == 1:
            course_enrollment.cancel()

        frappe.delete_doc(
            "Course Enrollment",
            enrollment_name,
            ignore_permissions=True
        )