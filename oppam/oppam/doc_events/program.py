import frappe


def create_course_from_program(doc, method=None):
    existing_course = frappe.db.get_value(
        "Course",
        {"course_name": doc.program_name},
        "name"
    )

    if existing_course:
        course_name = existing_course
    else:
        course = frappe.new_doc("Course")
        course.course_name = doc.program_name
        course.insert(ignore_permissions=True)

        course_name = course.name

    # Add the created Course to Program Courses child table
    if not any(row.course == course_name for row in doc.courses):
        doc.append(
            "courses",
            {
                "course": course_name,
                "course_name": doc.program_name,
                "mandatory": 1
            }
        )

        doc.save(ignore_permissions=True)