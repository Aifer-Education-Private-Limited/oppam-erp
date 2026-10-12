import frappe


# Only these DocTypes should appear in the Education module sidebar.
ALLOWED_DOCTYPES = [
    "Student",
    "Academic Year",
    "Program",
    "Course",
    "Topic",
    "Video",
    "Article",
    "Assignment",
    "Program Enrollment",
    "Course Enrollment",
    "Course Activity",
]


def execute():
    """Replace the Education workspace sidebar with the allowed DocTypes only."""
    workspace = frappe.get_doc("Workspace", "Education")

    # Rebuild the sidebar links as a flat list of the allowed DocTypes.
    workspace.set(
        "links",
        [
            {
                "type": "Link",
                "label": doctype,
                "link_to": doctype,
                "link_type": "DocType",
                "hidden": 0,
            }
            for doctype in ALLOWED_DOCTYPES
        ],
    )

    # Keep only shortcuts that point to the allowed DocTypes.
    allowed = set(ALLOWED_DOCTYPES)
    workspace.set(
        "shortcuts",
        [s for s in workspace.shortcuts if s.link_to in allowed],
    )

    # Clear dashboard body cards so they don't reference removed card breaks.
    workspace.content = "[]"

    # `type` is a mandatory Select; ensure it stays "Workspace" (using set()
    # because `type` is a Python built-in and can be unreliable as an attribute).
    workspace.set("type", "Workspace")

    workspace.save(ignore_permissions=True)
    frappe.clear_cache()
