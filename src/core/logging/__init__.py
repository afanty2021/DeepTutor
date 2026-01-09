"""
Backward compatibility module for deprecated src.core.logging.

This module provides compatibility imports for the new logging architecture.
"""

# Re-export from new logging module
from src.logging.logger import get_logger
from src.logging.handlers.websocket import LightRAGLogContext

__all__ = [
    "get_logger",
    "LightRAGLogContext",
]
