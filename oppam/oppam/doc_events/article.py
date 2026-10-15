from frappe.model.naming import make_autoname


def generate_article_id(doc, method=None):
    if not doc.get("custom_id"):
        doc.custom_id = make_autoname("ART-.####")