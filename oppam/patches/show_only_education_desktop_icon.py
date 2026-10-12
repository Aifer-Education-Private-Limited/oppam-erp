import frappe


def execute():
	"""Show only the Education module icon on the desk home page.

	Hides every other Desktop Icon so the /desk home grid renders
	Education alone. Reversible: set `hidden` back to 0 on any icon
	to bring it back.
	"""
	frappe.db.set_value(
		"Desktop Icon",
		{"label": ["!=", "Education"]},
		"hidden",
		1,
		update_modified=False,
	)
	frappe.db.set_value("Desktop Icon", {"label": "Education"}, "hidden", 0, update_modified=False)

	# `desktop_icons` and `bootinfo` are cached per-user in Redis hashes;
	# dropping the keys clears them for all users
	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")
