#!/usr/bin/env python
"""
NarratorAgent - Note Narration Agent (CosyVoice Support)

Converts note content into narration scripts and generates TTS audio using:
- CosyVoice (local, free) - Recommended
- OpenAI TTS (paid, fallback)
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import re
import sys
from typing import Any, Optional
from urllib.parse import urlparse
import uuid

import yaml

# Add project root for imports
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from lightrag.llm.openai import openai_complete_if_cache

from src.core.core import get_agent_params, get_llm_config, get_tts_config, load_config_with_main
from src.core.logging import get_logger

# Import shared stats from edit_agent
try:
    from .edit_agent import get_stats
except ImportError:
    # Fallback if edit_agent imports fail
    def get_stats():
        return None

# Import CosyVoice TTS tool
try:
    from src.tools.cosyvoice_tts import CosyVoiceTTS
    COSYVOICE_AVAILABLE = True
except ImportError:
    COSYVOICE_AVAILABLE = False
    CosyVoiceTTS = None

# Import OpenAI for fallback
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAIClient = None


def _load_prompts(language: str = "en") -> dict:
    """Load prompts from YAML file based on language"""
    prompts_dir = Path(__file__).parent / "prompts" / language
    prompt_file = prompts_dir / "narrator_agent.yaml"
    if prompt_file.exists():
        with open(prompt_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    # Fallback to English if language file not found
    fallback_file = Path(__file__).parent / "prompts" / "en" / "narrator_agent.yaml"
    if fallback_file.exists():
        with open(fallback_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


# Initialize logger with config
try:
    config = load_config_with_main("solve_config.yaml", _project_root)
    log_dir = config.get("paths", {}).get("user_log_dir") or config.get("logging", {}).get("log_dir")
    logger = get_logger("Narrator", log_dir=log_dir)
except Exception:
    logger = logging.getLogger(__name__)

# Storage path
USER_DIR = Path(__file__).parent.parent.parent.parent / "data" / "user" / "co-writer" / "audio"


def ensure_dirs():
    """Ensure directories exist"""
    USER_DIR.mkdir(parents=True, exist_ok=True)


class NarratorAgent:
    """Note Narration Agent - Generate narration script and convert to audio"""

    # Voice mappings for different TTS providers
    COSYVOICE_VOICES = {
        "alloy": "中文女",
        "female": "中文女",
        "male": "中文男",
        "zh-female": "中文女",
        "zh-male": "中文男",
    }

    OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, language: str = "en", use_cosyvoice: bool = None):
        self.language = language
        self._prompts = _load_prompts(language)

        # Load agent parameters
        try:
            self._agent_params = get_agent_params("narrator")
        except Exception:
            self._agent_params = {"temperature": 0.7, "max_tokens": 4000}

        # Load LLM config
        try:
            self.llm_config = get_llm_config()
        except Exception as e:
            logger.warning(f"Failed to load LLM config: {e}")
            self.llm_config = None

        # Determine which TTS to use
        if use_cosyvoice is None:
            # Auto-detect: prefer CosyVoice if available
            use_cosyvoice = COSYVOICE_AVAILABLE

        self.use_cosyvoice = use_cosyvoice

        # Initialize TTS
        if self.use_cosyvoice:
            self._init_cosyvoice()
        else:
            self._init_openai_tts()

    def _init_cosyvoice(self):
        """Initialize CosyVoice TTS"""
        if not COSYVOICE_AVAILABLE:
            raise ValueError("CosyVoice not available. Please install CosyVoice.")

        try:
            # Try to get CosyVoice config from environment
            import os
            model_dir = os.getenv("COSYVOICE_MODEL_DIR")
            version = os.getenv("COSYVOICE_VERSION", "3.0")
            mode = os.getenv("COSYVOICE_MODE", "instruct")
            conda_env = os.getenv("COSYVOICE_CONDA_ENV", "DeepTutor-env-3.11")

            self.cosyvoice = CosyVoiceTTS(
                model_dir=model_dir,
                version=version,
                mode=mode,
                conda_env=conda_env,
            )

            logger.info(f"✅ Using CosyVoice TTS (v{version}, mode={mode})")

            # Set default voice
            self.default_voice = "中文女"

        except Exception as e:
            logger.error(f"Failed to initialize CosyVoice: {e}", exc_info=True)
            raise

    def _init_openai_tts(self):
        """Initialize OpenAI TTS (fallback)"""
        try:
            self.tts_config = get_tts_config()
            self._validate_tts_config()

            logger.info("✅ Using OpenAI TTS (fallback)")
            self.default_voice = self.tts_config.get("voice", "alloy")

        except Exception as e:
            logger.warning(f"OpenAI TTS not available: {e}")
            self.tts_config = None
            self.default_voice = "alloy"

    def _validate_tts_config(self):
        """Validate OpenAI TTS configuration"""
        if not self.tts_config:
            raise ValueError("TTS config is None")

        required_keys = ["model", "api_key", "base_url"]
        missing_keys = [key for key in required_keys if key not in self.tts_config]
        if missing_keys:
            raise ValueError(f"TTS config missing required keys: {missing_keys}")

    async def generate_script(self, content: str, style: str = "friendly") -> dict[str, Any]:
        """
        Generate narration script

        Args:
            content: Note content (Markdown format)
            style: Narration style (friendly, academic, concise)

        Returns:
            Dict containing:
                - script: Narration script text
                - key_points: List of extracted key points
        """
        if not self.llm_config:
            raise ValueError("LLM configuration not available")

        target_length = 4000
        is_long_content = len(content) > 5000

        style_prompts = {
            "friendly": self._prompts.get("style_friendly", ""),
            "academic": self._prompts.get("style_academic", ""),
            "concise": self._prompts.get("style_concise", ""),
        }

        length_instruction = (
            self._prompts.get("length_instruction_long", "")
            if is_long_content
            else self._prompts.get("length_instruction_short", "")
        )

        system_template = self._prompts.get("generate_script_system_template", "")
        system_prompt = system_template.format(
            style_prompt=style_prompts.get(style, style_prompts["friendly"]),
            length_instruction=length_instruction,
        )

        if is_long_content:
            user_template = self._prompts.get("generate_script_user_long", "")
            user_prompt = user_template.format(content=content[:8000] + "...")
        else:
            user_template = self._prompts.get("generate_script_user_short", "")
            user_prompt = user_template.format(content=content)

        logger.info(f"Generating narration script with style: {style}")

        model = self.llm_config["model"]
        response = await openai_complete_if_cache(
            model=model,
            prompt=user_prompt,
            system_prompt=system_prompt,
            api_key=self.llm_config["api_key"],
            base_url=self.llm_config["base_url"],
            max_tokens=self._agent_params["max_tokens"],
            temperature=self._agent_params["temperature"],
        )

        # Track token usage
        stats = get_stats()
        if stats:
            stats.add_call(
                model=model, system_prompt=system_prompt, user_prompt=user_prompt, response=response
            )

        # Clean and truncate response
        script = response.strip()
        if len(script) > 4000:
            logger.warning(f"Generated script length {len(script)} exceeds 4000 limit. Truncating...")
            truncated = script[:3997]
            last_period = max(
                truncated.rfind("。"),
                truncated.rfind("！"),
                truncated.rfind("？"),
                truncated.rfind("."),
                truncated.rfind("!"),
                truncated.rfind("?"),
            )
            if last_period > 3500:
                script = truncated[: last_period + 1]
            else:
                script = truncated + "..."

        key_points = await self._extract_key_points(content)

        return {
            "script": script,
            "key_points": key_points,
            "style": style,
            "original_length": len(content),
            "script_length": len(script),
        }

    async def _extract_key_points(self, content: str) -> list:
        """Extract key points from notes"""
        if not self.llm_config:
            return []

        system_prompt = self._prompts.get("extract_key_points_system", "")
        user_template = self._prompts.get(
            "extract_key_points_user",
            "Please extract key points from the following notes:\n\n{content}",
        )
        user_prompt = user_template.format(content=content[:4000])

        try:
            model = self.llm_config["model"]
            response = await openai_complete_if_cache(
                model=model,
                prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=self.llm_config["api_key"],
                base_url=self.llm_config["base_url"],
                max_tokens=self._agent_params["max_tokens"],
                temperature=self._agent_params["temperature"],
            )

            stats = get_stats()
            if stats:
                stats.add_call(
                    model=model, system_prompt=system_prompt, user_prompt=user_prompt, response=response
                )

            # Try to parse JSON
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            logger.warning(f"Failed to extract key points: {e}")
            return []

    async def generate_audio(
        self,
        script: str,
        voice: str = None,
        output_format: str = "mp3"
    ) -> dict[str, Any]:
        """
        Convert narration script to audio

        Args:
            script: Narration script text
            voice: Voice role (CosyVoice: 中文女/中文男, OpenAI: alloy/echo/etc)
            output_format: Output format ("mp3" or "wav")

        Returns:
            Dict containing:
                - audio_path: Audio file path
                - audio_url: Audio access URL
                - audio_id: Unique audio identifier
                - voice: Voice used
        """
        ensure_dirs()

        # Validate input
        if not script or not script.strip():
            raise ValueError("Script cannot be empty")

        # Use default voice if not specified
        if voice is None:
            voice = self.default_voice

        audio_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]

        # Generate audio using appropriate TTS
        if self.use_cosyvoice:
            return await self._generate_audio_cosyvoice(script, voice, audio_id, output_format)
        else:
            return await self._generate_audio_openai(script, voice, audio_id)

    async def _generate_audio_cosyvoice(
        self,
        script: str,
        voice: str,
        audio_id: str,
        output_format: str
    ) -> dict[str, Any]:
        """Generate audio using CosyVoice"""
        logger.info(f"Using CosyVoice TTS - Voice: {voice}")

        try:
            # Map voice name if needed
            cosyvoice_voice = self.COSYVOICE_VOICES.get(voice, voice)

            # Synthesize to WAV
            audio_filename = f"narration_{audio_id}.wav"
            wav_path = USER_DIR / audio_filename

            result = self.cosyvoice.synthesize(
                text=script,
                speaker=cosyvoice_voice,
                output_path=str(wav_path),
                stream=False,
            )

            logger.info(f"CosyVoice audio saved: {result['audio_path']}")

            # Convert to MP3 if requested
            if output_format == "mp3":
                audio_filename = f"narration_{audio_id}.mp3"
                mp3_path = self.cosyvoice.convert_wav_to_mp3(str(wav_path))
                audio_path = mp3_path
            else:
                audio_path = str(wav_path)

            # Generate URL
            relative_path = f"co-writer/audio/{audio_filename}"
            audio_url = f"/api/outputs/{relative_path}"

            return {
                "audio_path": audio_path,
                "audio_url": audio_url,
                "audio_id": audio_id,
                "voice": voice,
                "tts_provider": "cosyvoice",
                "duration": result.get("duration", 0),
            }

        except Exception as e:
            logger.error(f"CosyVoice TTS generation failed: {e}", exc_info=True)
            raise ValueError(f"CosyVoice TTS generation failed: {e}")

    async def _generate_audio_openai(
        self,
        script: str,
        voice: str,
        audio_id: str
    ) -> dict[str, Any]:
        """Generate audio using OpenAI TTS (fallback)"""
        if not self.tts_config:
            raise ValueError("OpenAI TTS not configured")

        logger.info(f"Using OpenAI TTS - Voice: {voice}")

        # Truncate if too long
        if len(script) > 4096:
            logger.warning(f"Script length {len(script)} exceeds 4096 limit. Truncating...")
            truncated = script[:4093]
            last_period = max(
                truncated.rfind("。"),
                truncated.rfind("！"),
                truncated.rfind("？"),
                truncated.rfind("."),
                truncated.rfind("!"),
                truncated.rfind("?"),
            )
            if last_period > 3500:
                script = truncated[: last_period + 1]
            else:
                script = truncated + "..."

        audio_filename = f"narration_{audio_id}.mp3"
        audio_path = USER_DIR / audio_filename

        try:
            client = OpenAIClient(
                base_url=self.tts_config["base_url"],
                api_key=self.tts_config["api_key"]
            )

            response = client.audio.speech.create(
                model=self.tts_config["model"],
                voice=voice,
                input=script
            )

            response.stream_to_file(audio_path)

            logger.info(f"OpenAI audio saved to: {audio_path}")

            relative_path = f"co-writer/audio/{audio_filename}"
            audio_url = f"/api/outputs/{relative_path}"

            return {
                "audio_path": str(audio_path),
                "audio_url": audio_url,
                "audio_id": audio_id,
                "voice": voice,
                "tts_provider": "openai",
            }

        except Exception as e:
            logger.error(f"OpenAI TTS generation failed: {e}", exc_info=True)
            raise ValueError(f"OpenAI TTS generation failed: {e}")

    async def narrate(
        self,
        content: str,
        style: str = "friendly",
        voice: str = None,
        skip_audio: bool = False,
        output_format: str = "mp3"
    ) -> dict[str, Any]:
        """
        Complete narration flow: generate script + generate audio

        Args:
            content: Note content
            style: Narration style
            voice: Voice role
            skip_audio: Whether to skip audio generation
            output_format: Output format ("mp3" or "wav")

        Returns:
            Dict containing script info and optionally audio info
        """
        script_result = await self.generate_script(content, style)

        if voice is None:
            voice = self.default_voice

        result = {
            "script": script_result["script"],
            "key_points": script_result["key_points"],
            "style": style,
            "original_length": script_result["original_length"],
            "script_length": script_result["script_length"],
            "tts_provider": "cosyvoice" if self.use_cosyvoice else "openai",
        }

        if not skip_audio:
            try:
                audio_result = await self.generate_audio(
                    script_result["script"],
                    voice=voice,
                    output_format=output_format
                )
                result.update({
                    "audio_url": audio_result["audio_url"],
                    "audio_path": audio_result["audio_path"],
                    "audio_id": audio_result["audio_id"],
                    "voice": voice,
                    "has_audio": True,
                    "duration": audio_result.get("duration", 0),
                })
            except Exception as e:
                logger.error(f"Audio generation failed: {e}")
                result["has_audio"] = False
                result["audio_error"] = str(e)
        else:
            result["has_audio"] = False

        return result


__all__ = ["NarratorAgent"]
