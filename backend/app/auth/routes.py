from flask import Blueprint, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from ..db import execute, query_one
from ..activity import log_activity

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return {"error": "username and password are required"}, 400
    if len(password) < 6:
        return {"error": "password must be at least 6 characters"}, 400
    if len(username) < 1:
        return {"error": "username cannot be empty"}, 400

    try:
        existing = query_one("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return {"error": "username already exists"}, 409

        password_hash = generate_password_hash(password)
        user_id = execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, password_hash, 0),
        )
        
        if not user_id:
            return {"error": "Failed to create user account"}, 500
        
        session["user_id"] = int(user_id)
        session["username"] = username
        session.permanent = True  # Make session persistent
        log_activity("user_signup", user_id=int(user_id), payload={"username": username})
        return {"ok": True, "user": {"id": int(user_id), "username": username}}
    except sqlite3.IntegrityError as e:
        # Handle unique constraint violations
        if "UNIQUE constraint failed" in str(e) or "username" in str(e).lower():
            return {"error": "username already exists"}, 409
        import traceback
        traceback.print_exc()
        return {"error": f"Signup failed: username may already exist"}, 409
    except sqlite3.OperationalError as e:
        # Handle database errors (locked, missing column, etc.)
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        if "no such column" in error_msg.lower():
            if "is_admin" in error_msg:
                return {"error": "Database migration needed. Run: cd backend && python migrate_add_admin_column.py"}, 500
        if "database is locked" in error_msg.lower():
            return {"error": "Database is locked. Please close other programs using the database and try again."}, 500
        return {"error": f"Database error: {error_msg}"}, 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Signup failed: {str(e)}"}, 500


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return {"error": "username and password are required"}, 400

    try:
        user = query_one("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        if not user:
            return {"error": "invalid credentials"}, 401
        
        if not user.get("password_hash"):
            return {"error": "invalid credentials"}, 401
        
        if not check_password_hash(user["password_hash"], password):
            return {"error": "invalid credentials"}, 401

        session["user_id"] = int(user["id"])
        session["username"] = user["username"]
        session.permanent = True  # Make session persistent
        log_activity("user_login", user_id=int(user["id"]), payload={"username": user["username"]})
        return {"ok": True, "user": {"id": int(user["id"]), "username": user["username"]}}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Login failed: {str(e)}"}, 500


@auth_bp.post("/logout")
def logout():
    uid = session.get("user_id")
    uname = session.get("username")
    session.clear()
    if uid:
        log_activity("user_logout", user_id=int(uid), payload={"username": uname})
    return {"ok": True}


@auth_bp.get("/me")
def me():
    if not session.get("user_id"):
        return {"user": None}
    return {"user": {"id": session["user_id"], "username": session.get("username")}}

