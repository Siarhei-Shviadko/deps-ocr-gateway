import contextvars
from typing import Any, Dict

__all__ = ["user"]

user: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("user")
