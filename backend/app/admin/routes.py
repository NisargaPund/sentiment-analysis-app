from flask import Blueprint, request, session, current_app
from werkzeug.security import check_password_hash

from ..db import query_all, query_one
from ..activity import log_activity

admin_bp = Blueprint("admin", __name__)


def _admin_required(fn):
    """Require admin session."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return {"error": "unauthorized"}, 401
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return {"error": "username and password required"}, 400
    if username != current_app.config["ADMIN_USERNAME"]:
        return {"error": "invalid credentials"}, 401
    admin_pass = current_app.config.get("ADMIN_PASSWORD", "")
    admin_hash = current_app.config.get("ADMIN_PASSWORD_HASH") or ""
    if admin_hash and check_password_hash(admin_hash, password):
        pass  # ok
    elif password == admin_pass:
        pass  # ok (plain password from env)
    else:
        return {"error": "invalid credentials"}, 401
    session["admin_logged_in"] = True
    session.permanent = True
    log_activity("admin_login", actor_type="admin", payload={"username": username})
    return {"ok": True}


@admin_bp.post("/logout")
def logout():
    session.pop("admin_logged_in", None)
    log_activity("admin_logout", actor_type="admin")
    return {"ok": True}


@admin_bp.get("/me")
def me():
    if not session.get("admin_logged_in"):
        return {"admin": None}
    return {"admin": {"username": current_app.config["ADMIN_USERNAME"]}}


@admin_bp.get("/users")
@_admin_required
def get_users():
    log_activity("admin_view_users", actor_type="admin")
    rows = query_all("SELECT id, username, is_admin, created_at FROM users ORDER BY id")
    return {"users": [dict(r) for r in rows]}


@admin_bp.get("/searches")
@_admin_required
def get_searches():
    log_activity("admin_view_searches", actor_type="admin")
    rows = query_all(
        "SELECT id, user_id, keyword, tweet_count, positive, neutral, negative, created_at FROM searches ORDER BY created_at DESC LIMIT 500"
    )
    return {"searches": [dict(r) for r in rows]}


@admin_bp.get("/statistics")
@_admin_required
def get_statistics():
    log_activity("admin_view_statistics", actor_type="admin")
    users = query_one("SELECT COUNT(*) as c FROM users")
    searches = query_one("SELECT COUNT(*) as c FROM searches")
    activities = query_one("SELECT COUNT(*) as c FROM activity_log")
    return {
        "total_users": users["c"] if users else 0,
        "total_searches": searches["c"] if searches else 0,
        "total_activities": activities["c"] if activities else 0,
    }


@admin_bp.get("/activity")
@_admin_required
def get_activity():
    """Paginated activity log. Query params: limit (default 100), offset (default 0)."""
    log_activity("admin_view_activity_log", actor_type="admin")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = max(0, int(request.args.get("offset", 0)))
    rows = query_all(
        """SELECT id, action, actor_type, user_id, payload, ip_address, user_agent, created_at
           FROM activity_log ORDER BY created_at DESC LIMIT ? OFFSET ?""",
        (limit, offset),
    )
    total = query_one("SELECT COUNT(*) as c FROM activity_log")
    return {
        "activities": [dict(r) for r in rows],
        "total": total["c"] if total else 0,
        "limit": limit,
        "offset": offset,
    }


@admin_bp.get("/verify")
@_admin_required
def verify_storage():
    """Quick check that all tables exist and have consistent counts."""
    from ..db import query_one
    users_count = query_one("SELECT COUNT(*) as c FROM users")
    searches_count = query_one("SELECT COUNT(*) as c FROM searches")
    activity_count = query_one("SELECT COUNT(*) as c FROM activity_log")
    # Sample latest activity to confirm structure
    sample = query_one(
        "SELECT id, action, actor_type, user_id, created_at FROM activity_log ORDER BY id DESC LIMIT 1"
    )
    return {
        "ok": True,
        "tables": {
            "users": users_count["c"] if users_count else 0,
            "searches": searches_count["c"] if searches_count else 0,
            "activity_log": activity_count["c"] if activity_count else 0,
        },
        "latest_activity": dict(sample) if sample else None,
    }


@admin_bp.get("/export")
@_admin_required
def export_all():
    """Export all stored data: users, searches, activity_log."""
    log_activity("admin_export_data", actor_type="admin")
    users = query_all("SELECT id, username, is_admin, created_at FROM users ORDER BY id")
    searches = query_all(
        "SELECT id, user_id, keyword, tweet_count, positive, neutral, negative, created_at FROM searches ORDER BY created_at DESC"
    )
    activities = query_all(
        "SELECT id, action, actor_type, user_id, payload, ip_address, user_agent, created_at FROM activity_log ORDER BY created_at DESC"
    )
    return {
        "users": [dict(r) for r in users],
        "searches": [dict(r) for r in searches],
        "activity_log": [dict(r) for r in activities],
    }
