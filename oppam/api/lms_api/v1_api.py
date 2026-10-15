import frappe


@frappe.whitelist(methods=["POST"])
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

@frappe.whitelist(methods=["GET"])
def get_student_by_token(token=None):
    try:
        if not token:
            frappe.local.response.update({
                "success": False,
                "message": "Token is required"
            })
            return
        
        student_id = frappe.db.get_value(
            "Student",
            {"custom_token": token, "enabled": 1},
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


import frappe


@frappe.whitelist(methods=["GET"])
def get_topic_list(course_id=None, student_id=None):
    try:
        if not course_id or not student_id:
            frappe.local.response.update({
                "success": False,
                "message": "Course ID and Student ID are required",
                "topics": []
            })
            return

        if not frappe.db.exists("Course", course_id):
            frappe.local.response.update({
                "success": False,
                "message": "Course not found",
                "topics": []
            })
            return

        if not frappe.db.exists("Student", student_id):
            frappe.local.response.update({
                "success": False,
                "message": "Student not found",
                "topics": []
            })
            return

        # Validate course enrollment
        enrollment = frappe.db.exists(
            "Course Enrollment",
            {
                "student": student_id,
                "course": course_id
            }
        )

        if not enrollment:
            frappe.local.response.update({
                "success": False,
                "message": "Student is not enrolled in this course",
                "topics": []
            })
            return

        activities = frappe.get_all(
            "Course Activity",
            filters={
                "course": course_id,
                "student": student_id,
                "enrollment": enrollment
            },
            fields=[
                "content_type",
                "content",
                "custom_submitted_date",
                "custom_status"
            ]
        )

        watched_keys = set()
        submitted_keys = set()

        for activity in activities:
            if not activity.content:
                continue

            key = (
                activity.content_type,
                activity.content
            )

            if activity.content_type in ("Article", "Video"):
                watched_keys.add(key)

            elif activity.content_type == "Assignment":
                if (
                    activity.custom_submitted_date
                    and activity.custom_status == "Confirmed"
                ):
                    submitted_keys.add(key)

        course = frappe.get_doc("Course", course_id)

        topic_list = []

        # Course Topic child table
        for row in course.get("topics") or []:

            if not row.topic:
                continue

            topic = frappe.get_doc("Topic", row.topic)

            total_articles = 0
            watched_articles = 0

            total_videos = 0
            watched_videos = 0

            total_assignments = 0
            submitted_assignments = 0

            # Topic Content child table
            for content in topic.get("topic_content") or []:

                if not content.content:
                    continue

                key = (
                    content.content_type,
                    content.content
                )

                if content.content_type == "Article":
                    total_articles += 1

                    if key in watched_keys:
                        watched_articles += 1

                elif content.content_type == "Video":
                    total_videos += 1

                    if key in watched_keys:
                        watched_videos += 1

                elif content.content_type == "Assignment":
                    total_assignments += 1

                    if key in submitted_keys:
                        submitted_assignments += 1

            total_contents = (
                total_articles
                + total_videos
                + total_assignments
            )

            watched_contents = (
                watched_articles
                + watched_videos
                + submitted_assignments
            )

            topic_list.append({
                "topic_name": row.topic_name or topic.topic_name,
                "total_contents": total_contents,
                "watched_contents": watched_contents,
                "total_articles": total_articles,
                "watched_articles": watched_articles,
                "total_videos": total_videos,
                "watched_videos": watched_videos,
                "total_assignments": total_assignments,
                "submitted_assignments": submitted_assignments
            })

        frappe.local.response.update({
            "success": True,
            "message": "Topics retrieved successfully",
            "topics": topic_list
        })
        return

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Topic List API Error"
        )

        frappe.local.response.update({
            "success": False,
            "message": "An error occurred",
            "topics": []
        })
        return

import frappe
import urllib.parse
from frappe.utils import strip_html_tags


def build_file_url(path):
    if not path:
        return None
    raw_url = frappe.utils.get_url(path)
    return urllib.parse.quote(raw_url, safe=":/?=&%#")


@frappe.whitelist(methods=["GET"])
def get_topic_contents(course_id=None, topic_name=None, student_id=None):
    try:
        if not course_id or not topic_name or not student_id:
            frappe.local.response.update({
                "success": False,
                "message": "Course ID, Topic Name and Student ID are required",
                "contents": []
            })
            return

        if not frappe.db.exists("Course", course_id):
            frappe.local.response.update({
                "success": False,
                "message": "Course not found",
                "contents": []
            })
            return

        if not frappe.db.exists("Student", student_id):
            frappe.local.response.update({
                "success": False,
                "message": "Student not found",
                "contents": []
            })
            return

        # Validate course enrollment
        enrollment = frappe.db.exists(
            "Course Enrollment",
            {
                "student": student_id,
                "course": course_id
            }
        )

        if not enrollment:
            frappe.local.response.update({
                "success": False,
                "message": "Student is not enrolled in this course",
                "contents": []
            })
            return

        course = frappe.get_doc("Course", course_id)

        topic_id = None

        for row in course.get("topics") or []:
            if row.topic_name == topic_name or row.topic == topic_name:
                topic_id = row.topic
                break

        if not topic_id:
            frappe.local.response.update({
                "success": False,
                "message": "Topic not found in this course",
                "contents": []
            })
            return

        if not frappe.db.exists("Topic", topic_id):
            frappe.local.response.update({
                "success": False,
                "message": "Topic not found",
                "contents": []
            })
            return

        # Get Topic document
        topic = frappe.get_doc("Topic", topic_id)

        activities = frappe.get_all(
            "Course Activity",
            filters={
                "course": course_id,
                "student": student_id,
                "enrollment": enrollment
            },
            fields=[
                "content_type",
                "content",
                "custom_submitted_content",
                "custom_submitted_date",
                "custom_submitted_note",
                "custom_status",
                "custom_rework_note"
            ],
            order_by="modified desc"
        )

       
        activity_map = {}

        for activity in activities:
            if not activity.content:
                continue

            key = (
                activity.content_type,
                activity.content
            )

            if key not in activity_map:
                activity_map[key] = activity

        content_list = []

       
        for row in topic.get("topic_content") or []:

            if not row.content:
                continue

            content_type = row.content_type
            content_id = row.content

            if content_type not in ("Article", "Video", "Assignment"):
                continue

            if not frappe.db.exists(content_type, content_id):
                continue

           
            content_doc = frappe.get_doc(content_type, content_id)

            title = None
            description = None
            content_value = None

            if content_type == "Article":
                title = content_doc.get("title")
                description = content_doc.get("custom_description")

                content_value = build_file_url(
                    content_doc.get("custom_contents")
                )

            elif content_type == "Video":
                title = content_doc.get("title")

                # Convert HTML description to plain text
                video_description = content_doc.get("description")

                description = (
                    strip_html_tags(video_description).strip()
                    if video_description else None
                )

                
                content_value = content_doc.get("url")

            elif content_type == "Assignment":
                title = content_doc.get("title")
                description = content_doc.get("description")

                content_value = build_file_url(
                    content_doc.get("content")
                )
            if content_type in ("Article", "Video"):
                response_content_id = content_doc.get("custom_id") or content_doc.name
            else:
                response_content_id = content_doc.name


            content_data = {
                "content_id": response_content_id,
                "content_title": title,
                "description": description,
                "content": content_value,
                "content_type": content_type
            }

            # Assignment-specific details
            if content_type == "Assignment":

                key = (content_type, content_id)
                activity = activity_map.get(key)

                status = (
                    activity.custom_status
                    if activity and activity.custom_status
                    else "Pending"
                )

                content_data.update({
                    "submitted_content": (
                        build_file_url(
                            activity.custom_submitted_content
                        )
                        if activity else None
                    ),
                    "submitted_date": (
                        str(activity.custom_submitted_date)
                        if activity and activity.custom_submitted_date
                        else None
                    ),
                    "submitted_note": (
                        activity.custom_submitted_note
                        if activity else None
                    ),
                    "status": status,
                    "rework_note": (
                        activity.custom_rework_note
                        if activity and status == "Rework"
                        else None
                    )
                })

            content_list.append(content_data)

        frappe.local.response.update({
            "success": True,
            "message": "Topic contents retrieved successfully",
            "contents": content_list
        })
        return

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Topic Contents API Error"
        )

        frappe.local.response.update({
            "success": False,
            "message": "An error occurred",
            "contents": []
        })
        return