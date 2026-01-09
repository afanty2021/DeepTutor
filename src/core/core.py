#!/usr/bin/env python
"""
Backward compatibility wrapper for deprecated src.core.core module.
This module provides compatibility functions that redirect to the new services architecture.

Deprecated: Please use src.services.config and src.services.llm instead.
"""

import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
import yaml

# PROJECT_ROOT points to the actual project root directory (DeepTutor/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load .env from project root directory
load_dotenv(PROJECT_ROOT / "DeepTutor.env", override=False)
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _to_int(value: Optional[str], default: int) -> int:
    """Convert environment variable to int, fallback to default value on failure."""
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _strip_value(value: Optional[str]) -> Optional[str]:
    """Remove leading/trailing whitespace and quotes from string."""
    if value is None:
        return None
    return value.strip().strip("\"'")


def get_llm_config() -> dict[str, Any]:
    """
    Return complete environment configuration for LLM.

    This function now uses the new services architecture.
    """
    from src.services.llm import config as llm_config
    from src.services.config import load_config_with_main

    # Load main configuration
    config = load_config_with_main("config/main.yaml")

    # Merge with environment variables
    return {
        "model": os.getenv("LLM_MODEL", "gpt-4o"),
        "api_key": os.getenv("LLM_BINDING_API_KEY", ""),
        "base_url": os.getenv("LLM_BINDING_HOST", "https://api.openai.com/v1"),
        "temperature": 0.7,
        "max_tokens": 4096,
    }


def get_embedding_config() -> dict[str, Any]:
    """
    Return configuration for embedding model.
    """
    return {
        "provider": os.getenv("EMBEDDING_PROVIDER", "openai"),
        "model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        "api_key": os.getenv("EMBEDDING_API_KEY", ""),
        "base_url": os.getenv("EMBEDDING_URL", ""),
        "dimensions": _to_int(os.getenv("EMBEDDING_DIMENSIONS"), 1536),
    }


def get_vision_config() -> dict[str, Any]:
    """
    Return configuration for vision model.
    """
    return {
        "model": os.getenv("VISION_MODEL", "gpt-4o"),
        "api_key": os.getenv("LLM_BINDING_API_KEY", ""),
        "base_url": os.getenv("LLM_BINDING_HOST", "https://api.openai.com/v1"),
    }


def get_tts_config() -> dict[str, Any]:
    """
    Return configuration for TTS (Text-to-Speech).
    """
    use_cosyvoice = os.getenv("USE_COSYVOICE", "true").lower() == "true"

    if use_cosyvoice:
        return {
            "provider": "cosyvoice",
            "version": os.getenv("COSYVOICE_VERSION", "3.0"),
            "mode": os.getenv("COSYVOICE_MODE", "instruct"),
            "conda_env": os.getenv("COSYVOICE_CONDA_ENV", "DeepTutor-env-3.11"),
            "voice": os.getenv("TTS_VOICE", "中文女"),
            "model_dir": os.getenv("COSYVOICE_MODEL_DIR", ""),
        }
    else:
        return {
            "provider": "openai",
            "model": os.getenv("TTS_MODEL", "tts-1"),
            "url": os.getenv("TTS_URL", "https://api.openai.com/v1"),
            "api_key": os.getenv("LLM_BINDING_API_KEY", ""),
        }


def get_agent_params(module_name: str) -> dict:
    """Get agent parameters from configuration.

    This is now redirected to the new services.config module.
    """
    from src.services.config import get_agent_params as _get_agent_params
    return _get_agent_params(module_name)


def load_config_with_main(config_file: str) -> dict:
    """Load configuration file and merge with main.yaml.

    This is now redirected to the new services.config module.
    """
    from src.services.config import load_config_with_main as _load_config
    return _load_config(config_file)


# Export commonly used functions
__all__ = [
    "get_llm_config",
    "get_embedding_config",
    "get_vision_config",
    "get_tts_config",
    "get_agent_params",
    "load_config_with_main",
    "PROJECT_ROOT",
]
