"""Log every action to activity_log for admin audit."""
import json
import logging
from typing import Any, Dict, Optional

from flask import request

from .db import execute

logger = logging.getLogger(__name__)


def log_activity(
    action: str,
    *,
    user_id: Optional[int] = None,
    actor_type: str = "user",
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Record an action in activity_log. Call from request context."""
    try:
        ip_address = request.remote_addr if request else None
        user_agent = (request.user_agent.string if request and request.user_agent else None) or ""
        payload_str = json.dumps(payload, default=str) if payload else None
        execute(
            """INSERT INTO activity_log (action, actor_type, user_id, payload, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (action, actor_type, user_id, payload_str, ip_address or "", (user_agent or "")[:500]),
        )
    except Exception as e:
        logger.warning("Activity log insert failed: %s", e, exc_info=True)
