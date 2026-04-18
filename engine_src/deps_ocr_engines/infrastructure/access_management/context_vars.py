import contextvars
from typing import Any, Dict

user: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("user")
