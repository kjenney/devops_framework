"""Structured logging setup for the DevOps Framework."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with structured output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        _configure_logger(logger)
    return logger


def _configure_logger(logger: logging.Logger) -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = _StructuredFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


class _StructuredFormatter(logging.Formatter):
    """JSON-like structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        extras: dict[str, Any] = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__ and not k.startswith("_")
        }
        base = (
            f"level={record.levelname} "
            f"logger={record.name} "
            f"msg={record.getMessage()!r}"
        )
        if extras:
            parts = " ".join(f"{k}={v!r}" for k, v in extras.items())
            return f"{base} {parts}"
        return base
