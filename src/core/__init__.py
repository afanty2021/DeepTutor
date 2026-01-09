"""
Backward compatibility module for deprecated src.core.

This module provides compatibility imports for the new services architecture.
"""

# Re-export commonly used functions from core.py
from src.core.core import (
    PROJECT_ROOT,
    get_agent_params,
    get_embedding_config,
    get_llm_config,
    get_tts_config,
    get_vision_config,
    load_config_with_main,
)

__all__ = [
    "PROJECT_ROOT",
    "get_llm_config",
    "get_embedding_config",
    "get_vision_config",
    "get_tts_config",
    "get_agent_params",
    "load_config_with_main",
]
