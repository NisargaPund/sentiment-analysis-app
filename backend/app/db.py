import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS searches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  keyword TEXT NOT NULL,
  tweet_count INTEGER NOT NULL,
  positive REAL NOT NULL,
  neutral REAL NOT NULL,
  negative REAL NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS activity_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  actor_type TEXT NOT NULL DEFAULT 'user',
  user_id INTEGER,
  payload TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


def _ensure_is_admin_column(conn: sqlite3.Connection) -> None:
    """Add is_admin column to users table if it doesn't exist (for existing DBs)."""
    cur = conn.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    cur.close()
    if "is_admin" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        conn.commit()


def _ensure_activity_log_table(conn: sqlite3.Connection) -> None:
    """Create activity_log table if it doesn't exist (for existing DBs)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          action TEXT NOT NULL,
          actor_type TEXT NOT NULL DEFAULT 'user',
          user_id INTEGER,
          payload TEXT,
          ip_address TEXT,
          user_agent TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = _connect(g.app_config["SQLITE_PATH"])  # type: ignore[attr-defined]
        _ensure_is_admin_column(conn)  # Migrate existing DBs on first request
        _ensure_activity_log_table(conn)
        g.db = conn
    return g.db  # type: ignore[return-value]


def init_db(app: Flask) -> None:
    db_path = app.config["SQLITE_PATH"]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    _ensure_is_admin_column(conn)
    _ensure_activity_log_table(conn)
    conn.close()

    @app.before_request
    def _attach_config():
        g.app_config = app.config

    @app.teardown_appcontext
    def _close_db(exception: Optional[BaseException] = None):
        db = g.pop("db", None)
        if db is not None:
            db.close()


def query_one(sql: str, params: tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    cur = get_db().execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[Dict[str, Any]]:
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return [dict(row) for row in rows]


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return int(last_id)

