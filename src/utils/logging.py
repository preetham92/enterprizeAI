"""
Structured logging configuration for the AI Orchestration Platform.
"""

import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime
from uuid import UUID

import structlog
from config.settings import settings


# -------------------------
# Helpers
# -------------------------

def json_serializer(obj: Any, **kwargs) -> Any:
    """
    Custom JSON serializer compatible with json.dumps.
    Handles UUID and other non-serializable objects.
    """
    if isinstance(obj, UUID):
        return str(obj)
    return str(obj)


def add_timestamp(_, __, event_dict: Dict) -> Dict:
    """Add ISO-8601 UTC timestamp to log entries."""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


# -------------------------
# Logging Configuration
# -------------------------

def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Standard logging (base layer)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            add_timestamp,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,

            # JSON renderer — FIXED
            structlog.processors.JSONRenderer(
                serializer=lambda obj, **kw: json.dumps(
                    obj, default=json_serializer
                )
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        cache_logger_on_first_use=True,
    )


# -------------------------
# Public API
# -------------------------

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)


# -------------------------
# Bootstrap logging ONCE
# -------------------------

configure_logging()
