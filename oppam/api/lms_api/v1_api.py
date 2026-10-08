import frappe


@frappe.whitelist(allow_guest=True)
def student_login(email="", password=""):
    try:
        if not email or not password:
            frappe.local.response.update({
                "success": False,
                "message": "Email and Password are required"
            })
            return
        
        student = frappe.db.get_value(
            "Student",
            {"student_email_id": email, "enabled": 1},
            ["name", "custom_password"],
            as_dict=True
        )
        
        if not student:
            frappe.local.response.update({
                "success": False,
                "message": "Student not found"
            })
            return
        
        if student.get("custom_password") != password:
            frappe.local.response.update({
                "success": False,
                "message": "Invalid credentials"
            })
            return
        
        frappe.local.response.update({
            "success": True,
            "message": "Login successful",
            "student_id": student.name
        })
        return
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Student Login API Error")
        frappe.local.response.update({
            "success": False,
            "message": "An error occurred"
        })
        return

@frappe.whitelist(allow_guest=True)
def get_student_by_token(token):
    try:
        if not token:
            frappe.local.response.update({
                "success": False,
                "message": "Token is required"
            })
            return
        
        student_id = frappe.db.get_value(
            "Student",
            {"custom_token": token},
            "name"
        )
        
        if not student_id:
            frappe.local.response.update({
                "success": False,
                "message": "Invalid token"
            })
            return
        
        frappe.local.response.update({
            "success": True,
            "message": "Student retrieved successfully",
            "student_id": student_id
        })
        return
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Student By Token API Error")
        frappe.local.response.update({
            "success": False,
            "message": "An error occurred"
        })
        return