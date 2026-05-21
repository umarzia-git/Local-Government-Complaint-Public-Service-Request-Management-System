from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional in production
    load_dotenv = None

try:
    import mysql.connector
except ImportError:  # pragma: no cover - demo mode works without MySQL driver
    mysql = None
else:
    mysql = mysql.connector

if load_dotenv:
    load_dotenv()

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


STATUSES = ("Received", "In Progress", "Resolved", "Closed")
CLOSED_STATUSES = {"Resolved", "Closed"}


def mysql_enabled() -> bool:
    return os.getenv("LGC_DB_BACKEND", "demo").lower() == "mysql"


def db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("LGC_DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("LGC_DB_PORT", "3306")),
        "user": os.getenv("LGC_DB_USER", "root"),
        "password": os.getenv("LGC_DB_PASSWORD", ""),
        "database": os.getenv("LGC_DB_NAME", "lgc_system"),
    }


def get_connection():
    if mysql is None:
        raise RuntimeError(
            "mysql-connector-python is not installed. Run `pip install -r requirements.txt`."
        )
    return mysql.connect(**db_config())


def normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: normalize(value) for key, value in row.items()} for row in rows]


def mysql_select(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return normalize_rows(rows)
    finally:
        connection.close()


def now() -> datetime:
    return datetime.now().replace(microsecond=0)


seed_now = now()

DEPARTMENTS = [
    {
        "dept_id": 1,
        "dept_name": "Water & Sanitation",
        "head_name": "Asif Mehmood",
        "contact_email": "water@lgc.gov.pk",
        "contact_phone": "0912-345001",
    },
    {
        "dept_id": 2,
        "dept_name": "Roads & Infrastructure",
        "head_name": "Tariq Hussain",
        "contact_email": "roads@lgc.gov.pk",
        "contact_phone": "0912-345002",
    },
    {
        "dept_id": 3,
        "dept_name": "Electricity",
        "head_name": "Nadia Bibi",
        "contact_email": "electric@lgc.gov.pk",
        "contact_phone": "0912-345003",
    },
    {
        "dept_id": 4,
        "dept_name": "Solid Waste Management",
        "head_name": "Usman Shah",
        "contact_email": "waste@lgc.gov.pk",
        "contact_phone": "0912-345004",
    },
]

CATEGORIES = [
    {
        "category_id": 1,
        "category_name": "Water Supply Issue",
        "dept_id": 1,
        "sla_hours": 48,
        "description": "Low pressure, outage, or water quality complaint",
    },
    {
        "category_id": 2,
        "category_name": "Sewage / Drainage",
        "dept_id": 1,
        "sla_hours": 72,
        "description": "Blocked drain, sewage overflow, or standing water",
    },
    {
        "category_id": 3,
        "category_name": "Road Damage",
        "dept_id": 2,
        "sla_hours": 96,
        "description": "Potholes, damaged road surface, or broken footpaths",
    },
    {
        "category_id": 4,
        "category_name": "Illegal Encroachment",
        "dept_id": 2,
        "sla_hours": 120,
        "description": "Shops, stalls, or structures blocking public space",
    },
    {
        "category_id": 5,
        "category_name": "Street Light Fault",
        "dept_id": 3,
        "sla_hours": 24,
        "description": "Broken, flickering, or missing street lights",
    },
    {
        "category_id": 6,
        "category_name": "Transformer Issue",
        "dept_id": 3,
        "sla_hours": 48,
        "description": "Transformer noise, sparks, overload, or outage",
    },
    {
        "category_id": 7,
        "category_name": "Garbage Collection",
        "dept_id": 4,
        "sla_hours": 48,
        "description": "Missed pickup, overflow, or dumping point issue",
    },
    {
        "category_id": 8,
        "category_name": "Open Drain / Nullah",
        "dept_id": 4,
        "sla_hours": 72,
        "description": "Unsafe open drain or uncovered nullah",
    },
]

CITIZENS = [
    {
        "citizen_id": 1,
        "full_name": "Ali Hassan",
        "email": "ali.hassan12@gmail.com",
        "phone": "03001234567",
        "ward_no": "Ward-5",
    },
    {
        "citizen_id": 2,
        "full_name": "Sana Tariq",
        "email": "sana.tariq99@yahoo.com",
        "phone": "03111234567",
        "ward_no": "Ward-3",
    },
    {
        "citizen_id": 3,
        "full_name": "Bilal Ahmed",
        "email": "bilal.ahmed55@gmail.com",
        "phone": "03211234567",
        "ward_no": "Ward-7",
    },
    {
        "citizen_id": 4,
        "full_name": "Fatima Noor",
        "email": "fatima.noor22@hotmail.com",
        "phone": "03451234567",
        "ward_no": "Ward-2",
    },
    {
        "citizen_id": 5,
        "full_name": "Umar Farooq",
        "email": "umar.farooq88@gmail.com",
        "phone": "03321234567",
        "ward_no": "Ward-9",
    },
    {
        "citizen_id": 6,
        "full_name": "Hina Shah",
        "email": "hina.shah33@outlook.com",
        "phone": "03011234567",
        "ward_no": "Ward-11",
    },
]

STAFF = [
    {"staff_id": 5, "dept_id": 1, "full_name": "Raheel Khan", "role": "staff"},
    {"staff_id": 7, "dept_id": 2, "full_name": "Maryam Bibi", "role": "staff"},
    {"staff_id": 9, "dept_id": 3, "full_name": "Asim Raza", "role": "staff"},
    {"staff_id": 10, "dept_id": 4, "full_name": "Rukhsana Bibi", "role": "staff"},
]

COMPLAINTS = [
    {
        "complaint_id": 1,
        "token": "LGC-2026-00001",
        "citizen_id": 1,
        "category_id": 1,
        "dept_id": 1,
        "ward_no": "Ward-5",
        "description": "No water supply since three days in our street.",
        "photo_path": None,
        "status": "Resolved",
        "priority": "Normal",
        "sla_deadline": seed_now - timedelta(days=6),
        "feedback_pending": 1,
        "filed_at": seed_now - timedelta(days=8),
        "resolved_at": seed_now - timedelta(days=7),
    },
    {
        "complaint_id": 2,
        "token": "LGC-2026-00002",
        "citizen_id": 2,
        "category_id": 3,
        "dept_id": 2,
        "ward_no": "Ward-3",
        "description": "Large pothole on main road near the bazaar.",
        "photo_path": None,
        "status": "In Progress",
        "priority": "High",
        "sla_deadline": seed_now + timedelta(hours=11),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(days=3, hours=8),
        "resolved_at": None,
    },
    {
        "complaint_id": 3,
        "token": "LGC-2026-00003",
        "citizen_id": 3,
        "category_id": 5,
        "dept_id": 3,
        "ward_no": "Ward-7",
        "description": "Street light broken for two weeks near school.",
        "photo_path": None,
        "status": "Resolved",
        "priority": "Normal",
        "sla_deadline": seed_now - timedelta(days=2),
        "feedback_pending": 1,
        "filed_at": seed_now - timedelta(days=3),
        "resolved_at": seed_now - timedelta(days=2, hours=6),
    },
    {
        "complaint_id": 4,
        "token": "LGC-2026-00004",
        "citizen_id": 4,
        "category_id": 2,
        "dept_id": 1,
        "ward_no": "Ward-2",
        "description": "Sewage overflow is blocking access to nearby homes.",
        "photo_path": None,
        "status": "Received",
        "priority": "Normal",
        "sla_deadline": seed_now - timedelta(hours=9),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(days=4),
        "resolved_at": None,
    },
    {
        "complaint_id": 5,
        "token": "LGC-2026-00005",
        "citizen_id": 5,
        "category_id": 7,
        "dept_id": 4,
        "ward_no": "Ward-9",
        "description": "Garbage has not been collected for five days.",
        "photo_path": None,
        "status": "Closed",
        "priority": "Normal",
        "sla_deadline": seed_now - timedelta(days=10),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(days=12),
        "resolved_at": seed_now - timedelta(days=10, hours=5),
    },
    {
        "complaint_id": 6,
        "token": "LGC-2026-00006",
        "citizen_id": 6,
        "category_id": 6,
        "dept_id": 3,
        "ward_no": "Ward-11",
        "description": "Transformer is making a loud noise near the mosque.",
        "photo_path": None,
        "status": "In Progress",
        "priority": "High",
        "sla_deadline": seed_now - timedelta(hours=4),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(days=2, hours=3),
        "resolved_at": None,
    },
    {
        "complaint_id": 7,
        "token": "LGC-2026-00007",
        "citizen_id": 1,
        "category_id": 1,
        "dept_id": 1,
        "ward_no": "Ward-5",
        "description": "Low water pressure across the lane.",
        "photo_path": None,
        "status": "Received",
        "priority": "Normal",
        "sla_deadline": seed_now + timedelta(hours=18),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(hours=30),
        "resolved_at": None,
    },
    {
        "complaint_id": 8,
        "token": "LGC-2026-00008",
        "citizen_id": 2,
        "category_id": 4,
        "dept_id": 2,
        "ward_no": "Ward-4",
        "description": "A stall is blocking the public footpath.",
        "photo_path": None,
        "status": "Resolved",
        "priority": "Normal",
        "sla_deadline": seed_now - timedelta(days=1),
        "feedback_pending": 1,
        "filed_at": seed_now - timedelta(days=6),
        "resolved_at": seed_now - timedelta(days=2),
    },
    {
        "complaint_id": 9,
        "token": "LGC-2026-00009",
        "citizen_id": 3,
        "category_id": 8,
        "dept_id": 4,
        "ward_no": "Ward-8",
        "description": "Open nullah is unsafe for children in the area.",
        "photo_path": None,
        "status": "Received",
        "priority": "CRITICAL",
        "sla_deadline": seed_now + timedelta(hours=8),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(days=2),
        "resolved_at": None,
    },
    {
        "complaint_id": 10,
        "token": "LGC-2026-00010",
        "citizen_id": 5,
        "category_id": 3,
        "dept_id": 2,
        "ward_no": "Ward-3",
        "description": "Road edge has collapsed near the hospital turn.",
        "photo_path": None,
        "status": "Received",
        "priority": "High",
        "sla_deadline": seed_now + timedelta(days=2),
        "feedback_pending": 0,
        "filed_at": seed_now - timedelta(hours=9),
        "resolved_at": None,
    },
]

FEEDBACK = [
    {
        "feedback_id": 1,
        "complaint_id": 1,
        "citizen_id": 1,
        "dept_id": 1,
        "rating": 5,
        "comments": "Very quick response.",
        "submitted_at": seed_now - timedelta(days=6),
    },
    {
        "feedback_id": 2,
        "complaint_id": 3,
        "citizen_id": 3,
        "dept_id": 3,
        "rating": 4,
        "comments": "Good service.",
        "submitted_at": seed_now - timedelta(days=2),
    },
    {
        "feedback_id": 3,
        "complaint_id": 5,
        "citizen_id": 5,
        "dept_id": 4,
        "rating": 3,
        "comments": "Workers were late.",
        "submitted_at": seed_now - timedelta(days=9),
    },
    {
        "feedback_id": 4,
        "complaint_id": 8,
        "citizen_id": 2,
        "dept_id": 2,
        "rating": 4,
        "comments": "Encroachment removed.",
        "submitted_at": seed_now - timedelta(days=1),
    },
]

CHRONIC_ISSUES = [
    {
        "chronic_id": 1,
        "category_id": 1,
        "ward_no": "Ward-5",
        "complaint_count": 5,
        "detected_at": seed_now - timedelta(days=5),
        "is_resolved": 1,
        "resolution_note": "Main water supply pipe replaced.",
    },
    {
        "chronic_id": 2,
        "category_id": 3,
        "ward_no": "Ward-3",
        "complaint_count": 4,
        "detected_at": seed_now - timedelta(days=2),
        "is_resolved": 0,
        "resolution_note": None,
    },
    {
        "chronic_id": 3,
        "category_id": 8,
        "ward_no": "Ward-8",
        "complaint_count": 3,
        "detected_at": seed_now - timedelta(days=1),
        "is_resolved": 0,
        "resolution_note": None,
    },
]

STATUS_LOG = [
    {
        "log_id": 1,
        "complaint_id": 1,
        "staff_id": 5,
        "old_status": "Received",
        "new_status": "In Progress",
        "note": "Field team dispatched",
        "changed_at": seed_now - timedelta(days=8, hours=-2),
    },
    {
        "log_id": 2,
        "complaint_id": 1,
        "staff_id": 5,
        "old_status": "In Progress",
        "new_status": "Resolved",
        "note": "Pipe repaired",
        "changed_at": seed_now - timedelta(days=7),
    },
]


def by_id(items: list[dict[str, Any]], key: str, value: Any) -> Optional[dict[str, Any]]:
    return next((item for item in items if item[key] == value), None)


def serializable_complaint(complaint: dict[str, Any]) -> dict[str, Any]:
    citizen = by_id(CITIZENS, "citizen_id", complaint["citizen_id"]) or {}
    category = by_id(CATEGORIES, "category_id", complaint["category_id"]) or {}
    department = by_id(DEPARTMENTS, "dept_id", complaint["dept_id"]) or {}
    row = {
        **complaint,
        "citizen_name": citizen.get("full_name", "Unknown citizen"),
        "citizen_phone": citizen.get("phone", ""),
        "category_name": category.get("category_name", "Uncategorized"),
        "dept_name": department.get("dept_name", "Unassigned"),
    }
    return {key: normalize(value) for key, value in row.items()}


def demo_complaints(status: Optional[str] = None, query: Optional[str] = None) -> list[dict[str, Any]]:
    rows = [serializable_complaint(complaint) for complaint in COMPLAINTS]
    if status and status != "All":
        rows = [row for row in rows if row["status"] == status]
    if query:
        needle = query.lower()
        rows = [
            row
            for row in rows
            if needle in row["token"].lower()
            or needle in row["citizen_name"].lower()
            or needle in row["category_name"].lower()
            or needle in row["ward_no"].lower()
        ]
    return sorted(rows, key=lambda row: row["filed_at"], reverse=True)


def complaint_is_breached(complaint: dict[str, Any]) -> bool:
    deadline = complaint["sla_deadline"]
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    return complaint["status"] not in CLOSED_STATUSES and deadline < now()


def demo_department_kpi() -> list[dict[str, Any]]:
    rows = []
    for department in DEPARTMENTS:
        dept_complaints = [c for c in COMPLAINTS if c["dept_id"] == department["dept_id"]]
        resolved = [c for c in dept_complaints if c["status"] in CLOSED_STATUSES]
        ratings = [f["rating"] for f in FEEDBACK if f["dept_id"] == department["dept_id"]]
        on_time = [
            c
            for c in resolved
            if c["resolved_at"] is not None and c["resolved_at"] <= c["sla_deadline"]
        ]
        rows.append(
            {
                "dept_id": department["dept_id"],
                "dept_name": department["dept_name"],
                "total_resolved": len(resolved),
                "total_feedback": len(ratings),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "resolved_on_time": len(on_time),
                "on_time_pct": round((len(on_time) / len(resolved)) * 100, 1)
                if resolved
                else 0,
            }
        )
    return rows


def demo_heatmap() -> list[dict[str, Any]]:
    rows = []
    wards = sorted({complaint["ward_no"] for complaint in COMPLAINTS})
    for ward in wards:
        ward_complaints = [c for c in COMPLAINTS if c["ward_no"] == ward]
        open_complaints = [c for c in ward_complaints if c["status"] not in CLOSED_STATUSES]
        breaches = [c for c in ward_complaints if complaint_is_breached(c)]
        complaint_ids = {c["complaint_id"] for c in ward_complaints}
        ratings = [f["rating"] for f in FEEDBACK if f["complaint_id"] in complaint_ids]
        avg_satisfaction = round(sum(ratings) / len(ratings), 2) if ratings else 3
        risk_score = round(
            (len(open_complaints) * 0.40)
            + (len(breaches) * 0.35)
            + ((5 - avg_satisfaction) * 0.25 * 10),
            2,
        )
        rows.append(
            {
                "ward_no": ward,
                "open_complaints": len(open_complaints),
                "sla_breaches": len(breaches),
                "avg_satisfaction": avg_satisfaction,
                "risk_score": risk_score,
            }
        )
    return sorted(rows, key=lambda row: row["risk_score"], reverse=True)


def demo_chronic_issues() -> list[dict[str, Any]]:
    rows = []
    for issue in CHRONIC_ISSUES:
        category = by_id(CATEGORIES, "category_id", issue["category_id"]) or {}
        rows.append(
            {
                **issue,
                "category_name": category.get("category_name", "Uncategorized"),
                "detected_at": normalize(issue["detected_at"]),
            }
        )
    return rows


def demo_dashboard() -> dict[str, Any]:
    ratings = [feedback["rating"] for feedback in FEEDBACK]
    status_counts = {status: 0 for status in STATUSES}
    for complaint in COMPLAINTS:
        status_counts[complaint["status"]] += 1
    return {
        "source": "demo",
        "stats": {
            "total_complaints": len(COMPLAINTS),
            "open_complaints": len(
                [complaint for complaint in COMPLAINTS if complaint["status"] not in CLOSED_STATUSES]
            ),
            "resolved_complaints": len(
                [complaint for complaint in COMPLAINTS if complaint["status"] in CLOSED_STATUSES]
            ),
            "sla_breaches": len([c for c in COMPLAINTS if complaint_is_breached(c)]),
            "feedback_pending": len(
                [complaint for complaint in COMPLAINTS if complaint["feedback_pending"]]
            ),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
        },
        "status_counts": status_counts,
        "department_kpi": demo_department_kpi(),
        "ward_heatmap": demo_heatmap(),
        "chronic_issues": demo_chronic_issues(),
        "recent_complaints": demo_complaints()[:8],
    }


def mysql_dashboard() -> dict[str, Any]:
    stats = mysql_select(
        """
        SELECT
            COUNT(*) AS total_complaints,
            SUM(CASE WHEN status NOT IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS open_complaints,
            SUM(CASE WHEN status IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS resolved_complaints,
            SUM(CASE WHEN sla_deadline < NOW() AND status NOT IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS sla_breaches,
            SUM(CASE WHEN feedback_pending = 1 THEN 1 ELSE 0 END) AS feedback_pending,
            (SELECT ROUND(AVG(rating), 2) FROM complaint_feedback) AS avg_rating
        FROM complaint
        """
    )[0]
    status_counts = mysql_select(
        "SELECT status, COUNT(*) AS total FROM complaint GROUP BY status ORDER BY status"
    )
    department_kpi = mysql_select(
        """
        SELECT dept_id, dept_name, total_resolved, total_feedback, avg_rating,
               resolved_on_time, on_time_pct
        FROM v_department_kpi
        ORDER BY dept_name
        """
    )
    ward_heatmap = mysql_select(
        """
        SELECT ward_no, open_complaints, sla_breaches, avg_satisfaction, risk_score
        FROM v_ward_heatmap
        LIMIT 12
        """
    )
    chronic_issues = mysql_select(
        """
        SELECT ci.chronic_id, ci.category_id, cat.category_name, ci.ward_no,
               ci.complaint_count, ci.detected_at, ci.is_resolved, ci.resolution_note
        FROM chronic_issue ci
        JOIN category cat ON cat.category_id = ci.category_id
        ORDER BY ci.is_resolved ASC, ci.detected_at DESC
        LIMIT 10
        """
    )
    recent_complaints = mysql_select(
        """
        SELECT c.complaint_id, c.token, c.citizen_id, ci.full_name AS citizen_name,
               ci.phone AS citizen_phone, c.category_id, cat.category_name, c.dept_id,
               d.dept_name, c.ward_no, c.description, c.photo_path, c.status,
               c.priority, c.sla_deadline, c.feedback_pending, c.filed_at, c.resolved_at
        FROM complaint c
        JOIN citizen ci ON ci.citizen_id = c.citizen_id
        JOIN category cat ON cat.category_id = c.category_id
        JOIN department d ON d.dept_id = c.dept_id
        ORDER BY c.filed_at DESC
        LIMIT 8
        """
    )
    return {
        "source": "mysql",
        "stats": stats,
        "status_counts": {row["status"]: row["total"] for row in status_counts},
        "department_kpi": department_kpi,
        "ward_heatmap": ward_heatmap,
        "chronic_issues": chronic_issues,
        "recent_complaints": recent_complaints,
    }


def mysql_complaints(status: Optional[str] = None, query: Optional[str] = None) -> list[dict[str, Any]]:
    conditions = []
    params: list[Any] = []
    if status and status != "All":
        conditions.append("c.status = %s")
        params.append(status)
    if query:
        conditions.append(
            """
            (
                c.token LIKE %s OR ci.full_name LIKE %s OR cat.category_name LIKE %s
                OR c.ward_no LIKE %s OR d.dept_name LIKE %s
            )
            """
        )
        like = f"%{query}%"
        params.extend([like, like, like, like, like])
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return mysql_select(
        f"""
        SELECT c.complaint_id, c.token, c.citizen_id, ci.full_name AS citizen_name,
               ci.phone AS citizen_phone, c.category_id, cat.category_name, c.dept_id,
               d.dept_name, c.ward_no, c.description, c.photo_path, c.status,
               c.priority, c.sla_deadline, c.feedback_pending, c.filed_at, c.resolved_at
        FROM complaint c
        JOIN citizen ci ON ci.citizen_id = c.citizen_id
        JOIN category cat ON cat.category_id = c.category_id
        JOIN department d ON d.dept_id = c.dept_id
        {where_clause}
        ORDER BY c.filed_at DESC
        LIMIT 200
        """,
        tuple(params),
    )


def generate_token(next_id: int) -> str:
    return f"LGC-{now().year}-{next_id:05d}"


def create_demo_complaint(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    try:
        citizen_id = int(payload.get("citizen_id"))
        category_id = int(payload.get("category_id"))
    except (TypeError, ValueError):
        return {"error": "Select a valid citizen and category."}, 400

    citizen = by_id(CITIZENS, "citizen_id", citizen_id)
    category = by_id(CATEGORIES, "category_id", category_id)
    if not citizen or not category:
        return {"error": "Citizen or category was not found."}, 404

    description = (payload.get("description") or "").strip()
    if len(description) < 10:
        return {"error": "Description must be at least 10 characters."}, 400

    next_id = max(complaint["complaint_id"] for complaint in COMPLAINTS) + 1
    filed_at = now()
    complaint = {
        "complaint_id": next_id,
        "token": generate_token(next_id),
        "citizen_id": citizen_id,
        "category_id": category_id,
        "dept_id": category["dept_id"],
        "ward_no": (payload.get("ward_no") or citizen["ward_no"]).strip(),
        "description": description,
        "photo_path": None,
        "status": "Received",
        "priority": payload.get("priority") or "Normal",
        "sla_deadline": filed_at + timedelta(hours=category["sla_hours"]),
        "feedback_pending": 0,
        "filed_at": filed_at,
        "resolved_at": None,
    }
    COMPLAINTS.append(complaint)
    return serializable_complaint(complaint), 201


def create_mysql_complaint(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    try:
        citizen_id = int(payload.get("citizen_id"))
        category_id = int(payload.get("category_id"))
    except (TypeError, ValueError):
        return {"error": "Select a valid citizen and category."}, 400

    description = (payload.get("description") or "").strip()
    if len(description) < 10:
        return {"error": "Description must be at least 10 characters."}, 400

    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT citizen_id, ward_no FROM citizen WHERE citizen_id = %s",
            (citizen_id,),
        )
        citizen = cursor.fetchone()
        cursor.execute(
            "SELECT category_id, dept_id, sla_hours FROM category WHERE category_id = %s",
            (category_id,),
        )
        category = cursor.fetchone()
        if not citizen or not category:
            connection.rollback()
            cursor.close()
            return {"error": "Citizen or category was not found."}, 404

        cursor.execute("SELECT COALESCE(MAX(complaint_id), 0) + 1 AS next_id FROM complaint")
        next_id = cursor.fetchone()["next_id"]
        filed_at = now()
        sla_deadline = filed_at + timedelta(hours=int(category["sla_hours"]))
        ward_no = (payload.get("ward_no") or citizen["ward_no"]).strip()
        token = generate_token(next_id)
        cursor.execute(
            """
            INSERT INTO complaint
                (token, citizen_id, category_id, dept_id, ward_no, description, photo_path,
                 status, priority, sla_deadline, feedback_pending, filed_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, NULL, 'Received', %s, %s, 0, %s)
            """,
            (
                token,
                citizen_id,
                category_id,
                category["dept_id"],
                ward_no,
                description,
                payload.get("priority") or "Normal",
                sla_deadline,
                filed_at,
            ),
        )
        complaint_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        return mysql_complaints(query=token)[0] | {"complaint_id": complaint_id}, 201
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_demo_status(complaint_id: int, payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    new_status = payload.get("status")
    if new_status not in STATUSES:
        return {"error": "Choose a valid status."}, 400
    complaint = by_id(COMPLAINTS, "complaint_id", complaint_id)
    if not complaint:
        return {"error": "Complaint was not found."}, 404
    old_status = complaint["status"]
    complaint["status"] = new_status
    if new_status == "Resolved" and old_status != "Resolved":
        complaint["feedback_pending"] = 1
        complaint["resolved_at"] = now()
    STATUS_LOG.append(
        {
            "log_id": len(STATUS_LOG) + 1,
            "complaint_id": complaint_id,
            "staff_id": payload.get("staff_id") or 5,
            "old_status": old_status,
            "new_status": new_status,
            "note": (payload.get("note") or "").strip() or None,
            "changed_at": now(),
        }
    )
    return serializable_complaint(complaint), 200


def update_mysql_status(complaint_id: int, payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    new_status = payload.get("status")
    if new_status not in STATUSES:
        return {"error": "Choose a valid status."}, 400

    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT complaint_id, dept_id, status FROM complaint WHERE complaint_id = %s",
            (complaint_id,),
        )
        complaint = cursor.fetchone()
        if not complaint:
            connection.rollback()
            cursor.close()
            return {"error": "Complaint was not found."}, 404

        cursor.execute(
            """
            SELECT staff_id
            FROM staff
            WHERE dept_id = %s AND is_active = 1
            ORDER BY CASE WHEN role = 'staff' THEN 0 ELSE 1 END, staff_id
            LIMIT 1
            """,
            (complaint["dept_id"],),
        )
        staff = cursor.fetchone()
        if not staff:
            connection.rollback()
            cursor.close()
            return {"error": "No active staff account exists for this department."}, 400

        cursor.execute(
            "UPDATE complaint SET status = %s WHERE complaint_id = %s",
            (new_status, complaint_id),
        )
        cursor.execute(
            """
            INSERT INTO status_log (complaint_id, staff_id, old_status, new_status, note)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                complaint_id,
                staff["staff_id"],
                complaint["status"],
                new_status,
                (payload.get("note") or "").strip() or None,
            ),
        )
        connection.commit()
        cursor.close()
        updated = mysql_complaints(query=str(complaint_id))
        if not updated:
            updated = mysql_select(
                """
                SELECT c.complaint_id, c.token, c.citizen_id, ci.full_name AS citizen_name,
                       ci.phone AS citizen_phone, c.category_id, cat.category_name, c.dept_id,
                       d.dept_name, c.ward_no, c.description, c.photo_path, c.status,
                       c.priority, c.sla_deadline, c.feedback_pending, c.filed_at, c.resolved_at
                FROM complaint c
                JOIN citizen ci ON ci.citizen_id = c.citizen_id
                JOIN category cat ON cat.category_id = c.category_id
                JOIN department d ON d.dept_id = c.dept_id
                WHERE c.complaint_id = %s
                """,
                (complaint_id,),
            )
        return updated[0], 200
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def mysql_status() -> tuple[bool, str]:
    if not mysql_enabled():
        return True, "demo"
    try:
        rows = mysql_select("SELECT DATABASE() AS database_name")
        return True, rows[0]["database_name"] or "mysql"
    except Exception as exc:
        return False, str(exc)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/assets/erd")
def erd_asset():
    return send_from_directory(BASE_DIR / "ERD", "ERD2.png")


@app.get("/api/health")
def api_health():
    ok, detail = mysql_status()
    return jsonify(
        {
            "ok": ok,
            "source": "mysql" if mysql_enabled() else "demo",
            "detail": detail,
        }
    ), 200 if ok else 503


@app.get("/api/dashboard")
def api_dashboard():
    return jsonify(mysql_dashboard() if mysql_enabled() else demo_dashboard())


@app.get("/api/complaints")
def api_complaints():
    status = request.args.get("status")
    query = request.args.get("q")
    complaints = mysql_complaints(status, query) if mysql_enabled() else demo_complaints(status, query)
    return jsonify(
        {
            "source": "mysql" if mysql_enabled() else "demo",
            "count": len(complaints),
            "complaints": complaints,
        }
    )


@app.post("/api/complaints")
def api_create_complaint():
    payload = request.get_json(silent=True) or {}
    data, status = create_mysql_complaint(payload) if mysql_enabled() else create_demo_complaint(payload)
    return jsonify(data), status


@app.patch("/api/complaints/<int:complaint_id>/status")
def api_update_status(complaint_id: int):
    payload = request.get_json(silent=True) or {}
    data, status = (
        update_mysql_status(complaint_id, payload)
        if mysql_enabled()
        else update_demo_status(complaint_id, payload)
    )
    return jsonify(data), status


@app.get("/api/departments")
def api_departments():
    if mysql_enabled():
        departments = mysql_select(
            """
            SELECT dept_id, dept_name, head_name, contact_email, contact_phone
            FROM department
            ORDER BY dept_name
            """
        )
    else:
        departments = DEPARTMENTS
    return jsonify({"source": "mysql" if mysql_enabled() else "demo", "departments": departments})


@app.get("/api/categories")
def api_categories():
    if mysql_enabled():
        categories = mysql_select(
            """
            SELECT cat.category_id, cat.category_name, cat.dept_id, d.dept_name,
                   cat.sla_hours, cat.description
            FROM category cat
            JOIN department d ON d.dept_id = cat.dept_id
            ORDER BY cat.category_name
            """
        )
    else:
        categories = []
        for category in CATEGORIES:
            department = by_id(DEPARTMENTS, "dept_id", category["dept_id"]) or {}
            categories.append({**category, "dept_name": department.get("dept_name", "")})
    return jsonify({"source": "mysql" if mysql_enabled() else "demo", "categories": categories})


@app.get("/api/citizens")
def api_citizens():
    if mysql_enabled():
        citizens = mysql_select(
            """
            SELECT citizen_id, full_name, email, phone, ward_no
            FROM citizen
            ORDER BY full_name
            LIMIT 200
            """
        )
    else:
        citizens = CITIZENS
    return jsonify({"source": "mysql" if mysql_enabled() else "demo", "citizens": citizens})


@app.errorhandler(Exception)
def handle_error(exc: Exception):
    app.logger.exception("Unhandled error")
    return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True)
