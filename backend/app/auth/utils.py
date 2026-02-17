from functools import wraps
from typing import Any, Callable, TypeVar

from flask import session

F = TypeVar("F", bound=Callable[..., Any])


def login_required(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        user_id = session.get("user_id")
        if not user_id:
            # Debug: log session state
            import logging
            logging.warning(f"Unauthorized: session keys = {list(session.keys())}, user_id = {user_id}")
            return {"error": "unauthorized"}, 401
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]

