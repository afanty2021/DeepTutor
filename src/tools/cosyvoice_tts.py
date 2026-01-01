#!/usr/bin/env python
"""
CosyVoice TTS Tool - Local text-to-speech using CosyVoice

Supports:
- CosyVoice 1.0
- CosyVoice 2.0
- Fun-CosyVoice 3.0 (recommended)

Requirements:
- CosyVoice installed: https://github.com/FunAudioLLM/CosyVoice
- Conda env: DeepTutor-env-3.11
- Model downloaded
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional
import subprocess
import sys

logger = logging.getLogger(__name__)


class CosyVoiceTTS:
    """
    CosyVoice TTS wrapper for local text-to-speech

    Supports multiple CosyVoice versions with different inference modes:
    - SFT: Supervised fine-tuning mode
    - Zero-shot: Zero-shot voice cloning
    - Cross-lingual: Cross-lingual synthesis
    - Instruct: Instruction-based synthesis
    """

    def __init__(
        self,
        model_dir: str = None,
        version: str = "3.0",
        mode: str = "instruct",
        conda_env: str = "DeepTutor-env-3.11",
    ):
        """
        Initialize CosyVoice TTS

        Args:
            model_dir: Path to CosyVoice model directory
            version: CosyVoice version ("1.0", "2.0", "3.0")
            mode: Inference mode ("sft", "zero_shot", "cross_lingual", "instruct")
            conda_env: Conda environment name
        """
        self.version = version
        self.mode = mode
        self.conda_env = conda_env

        # Set default model directory based on version
        if model_dir is None:
            # Check environment variable first
            model_dir = os.getenv("COSYVOICE_MODEL_DIR")

            if not model_dir:
                # Default to ModelScope cache directory
                modelscope_cache = Path.home() / ".cache" / "modelscope" / "hub" / "FunAudioLLM"
                if version == "3.0":
                    # ModelScope downloads with date suffix (e.g., Fun-CosyVoice3-0.5B-2512)
                    # Try to find the actual directory
                    base_name = "Fun-CosyVoice3-0.5B"
                    model_dir = self._find_model_directory(modelscope_cache, base_name)
                elif version == "2.0":
                    base_name = "CosyVoice2-0.5B"
                    model_dir = self._find_model_directory(modelscope_cache, base_name)
                else:  # version == "1.0"
                    base_name = "CosyVoice-300M-Instruct"
                    model_dir = self._find_model_directory(modelscope_cache, base_name)

        self.model_dir = model_dir
        self.sample_rate = 22050  # CosyVoice default sample rate

        # Lazy initialization - load model only when needed
        self._cosyvoice = None
        self._device = None  # Will be auto-detected on first load

        logger.info(f"CosyVoice TTS initialized: version={version}, mode={mode}")
        logger.info(f"Model directory: {model_dir}")

    def _find_model_directory(self, search_dir: Path, base_name: str) -> str:
        """
        Find the actual model directory, handling ModelScope's date suffix naming

        ModelScope downloads models with date suffixes (e.g., Fun-CosyVoice3-0.5B-2512)
        This method finds the actual directory.

        Args:
            search_dir: Parent directory to search in
            base_name: Base model name (without date suffix)

        Returns:
            Path to the model directory
        """
        # Priority 1: Check CosyVoice source repo first
        cosyvoice_repo = Path("/Users/berton/Github/CosyVoice/pretrained_models")
        repo_model_path = cosyvoice_repo / base_name
        if repo_model_path.exists():
            logger.info(f"Found model in CosyVoice repo: {repo_model_path}")
            return str(repo_model_path)

        # Priority 2: ModelScope cache directory with exact match
        exact_path = search_dir / base_name
        if exact_path.exists():
            return str(exact_path)

        # Priority 3: Try to find directories matching the base name with any suffix
        if search_dir.exists():
            matching_dirs = sorted(
                [d for d in search_dir.iterdir() if d.is_dir() and d.name.startswith(base_name)],
                key=lambda x: x.stat().st_mtime,  # Sort by modification time, newest last
                reverse=True
            )

            if matching_dirs:
                logger.info(f"Found model directory: {matching_dirs[0]}")
                return str(matching_dirs[0])

        # Fallback to base path (will fail if it doesn't exist, but provides clear error)
        return str(exact_path)

    def _get_best_device(self) -> str:
        """
        Detect the best available device for inference

        Returns:
            Device string: 'mps' (Apple Silicon), 'cuda', or 'cpu'
        """
        try:
            import torch

            # Try MPS (Apple Silicon) first
            if torch.backends.mps.is_available():
                return "mps"

            # Try CUDA (NVIDIA GPU)
            if torch.cuda.is_available():
                return "cuda"

        except Exception:
            pass

        return "cpu"

    def _ensure_model_loaded(self):
        """Ensure CosyVoice model is loaded"""
        if self._cosyvoice is not None:
            return

        try:
            # Import CosyVoice inside the correct conda environment
            # Add CosyVoice to path
            cosyvoice_path = Path("/Users/berton/Github/CosyVoice")
            if str(cosyvoice_path) not in sys.path:
                sys.path.insert(0, str(cosyvoice_path))

            from cosyvoice.cli.cosyvoice import AutoModel

            # Auto-detect device
            self._device = self._get_best_device()

            logger.info(f"Loading CosyVoice model from: {self.model_dir}")
            logger.info(f"Using device: {self._device}")

            # Load model with device (if supported)
            try:
                # Try with device parameter first (newer CosyVoice versions)
                self._cosyvoice = AutoModel(model_dir=self.model_dir, device=self._device)
            except TypeError:
                # Fallback for older versions that don't support device parameter
                logger.warning("AutoModel doesn't support device parameter, loading without it")
                self._cosyvoice = AutoModel(model_dir=self.model_dir)

            logger.info("CosyVoice model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load CosyVoice model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load CosyVoice: {e}")

    def list_available_spks(self) -> list:
        """List available speakers (for SFT mode)"""
        self._ensure_model_loaded()
        try:
            if hasattr(self._cosyvoice, 'list_available_spks'):
                return self._cosyvoice.list_available_spks()
            return []
        except Exception as e:
            logger.warning(f"Failed to list speakers: {e}")
            return []

    def synthesize(
        self,
        text: str,
        speaker: str = "中文女",
        prompt_text: str = None,
        prompt_audio: str = None,
        output_path: str = None,
        stream: bool = False,
    ) -> dict:
        """
        Synthesize speech from text

        Args:
            text: Input text to synthesize
            speaker: Speaker name (for SFT mode) or instruction
            prompt_text: Reference text (for zero-shot mode)
            prompt_audio: Reference audio path (for zero-shot/VC mode)
            output_path: Output audio file path
            stream: Use streaming inference

        Returns:
            Dict containing:
                - audio_path: Generated audio file path
                - sample_rate: Audio sample rate
                - duration: Audio duration in seconds
                - speaker: Used speaker name
        """
        self._ensure_model_loaded()

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Generate output path if not provided
        if output_path is None:
            from datetime import datetime
            import uuid

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uid = uuid.uuid4().hex[:6]
            output_path = f"cosyvoice_{timestamp}_{uid}.wav"

        logger.info(f"Synthesizing with CosyVoice: mode={self.mode}, speaker={speaker}")

        try:
            # Call appropriate inference method based on mode
            if self.mode == "sft":
                inference_func = self._cosyvoice.inference_sft
                args = (text, speaker)

            elif self.mode == "zero_shot":
                inference_func = self._cosyvoice.inference_zero_shot
                # Use default prompt if not provided
                if not prompt_audio:
                    prompt_text = prompt_text or "希望你以后能够做的比我还好呦。"
                    # For CosyVoice 3.0, use instruct prompt
                    if self.version == "3.0":
                        prompt_text = "You are a helpful assistant.<|endofprompt|>" + prompt_text

                args = (text, prompt_text, prompt_audio) if prompt_audio else (text, prompt_text, "")

            elif self.mode == "cross_lingual":
                inference_func = self._cosyvoice.inference_cross_lingual
                prompt_text = prompt_text or "希望你以后能够做的比我还好呦。"
                args = (text, prompt_audio) if prompt_audio else (text,)

            elif self.mode == "instruct":
                # Use instruct2 for better control
                # CosyVoice3 instruct mode requires a reference audio file
                inference_func = self._cosyvoice.inference_instruct2

                # Default reference audio if none provided
                if not prompt_audio:
                    prompt_audio = "/Users/berton/Github/CosyVoice/asset/zero_shot_prompt.wav"

                # Build instruction from speaker name
                if not prompt_text:
                    speaker_instructions = {
                        "中文女": "You are a helpful assistant. 请用自然、清晰的女声说这句话。<|endofprompt|>",
                        "中文男": "You are a helpful assistant. 请用自然、清晰的男声说这句话。<|endofprompt|>",
                        "英文女": "You are a helpful assistant. Please use natural female voice.<|endofprompt|>",
                        "英文男": "You are a helpful assistant. Please use natural male voice.<|endofprompt|>",
                    }
                    prompt_text = speaker_instructions.get(speaker, "You are a helpful assistant. 请用自然的声音说这句话。<|endofprompt|>")

                # Args: tts_text, instruct_text, prompt_wav, zero_shot_spk_id
                args = (text, prompt_text, prompt_audio, '')

            else:
                raise ValueError(f"Unknown mode: {self.mode}")

            # Run inference
            audio_data = None
            for i, result in enumerate(inference_func(*args, stream=stream)):
                if 'tts_speech' in result:
                    audio_data = result['tts_speech']
                    break  # Take first chunk

            if audio_data is None:
                raise RuntimeError("No audio generated")

            # Save audio file
            import torch

            # Convert to numpy and save
            import torchaudio

            # Ensure audio_data is a tensor
            if not isinstance(audio_data, torch.Tensor):
                audio_data = torch.from_numpy(audio_data)

            # Save using torchaudio
            torchaudio.save(output_path, audio_data, self.sample_rate)

            logger.info(f"Audio saved to: {output_path}")

            # Calculate duration
            duration = len(audio_data) / self.sample_rate

            return {
                "audio_path": output_path,
                "sample_rate": self.sample_rate,
                "duration": duration,
                "speaker": speaker,
                "mode": self.mode,
                "version": self.version,
            }

        except Exception as e:
            logger.error(f"CosyVoice synthesis failed: {e}", exc_info=True)
            raise RuntimeError(f"TTS synthesis failed: {e}")

    def convert_wav_to_mp3(self, wav_path: str, mp3_path: str = None) -> str:
        """
        Convert WAV audio to MP3 format

        Args:
            wav_path: Input WAV file path
            mp3_path: Output MP3 file path (default: same as wav with .mp3 extension)

        Returns:
            Path to converted MP3 file
        """
        if mp3_path is None:
            mp3_path = wav_path.replace('.wav', '.mp3')

        try:
            # Use ffmpeg for conversion
            import subprocess

            subprocess.run(
                ['ffmpeg', '-y', '-i', wav_path, mp3_path],
                check=True,
                capture_output=True,
            )

            logger.info(f"Converted to MP3: {mp3_path}")
            return mp3_path

        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg conversion failed: {e}")
            raise RuntimeError(f"Failed to convert to MP3: {e}")
        except FileNotFoundError:
            logger.warning("ffmpeg not found, returning WAV file")
            return wav_path


# Convenience function for quick usage
def synthesize_speech(
    text: str,
    speaker: str = "中文女",
    mode: str = "instruct",
    version: str = "3.0",
    output_format: str = "wav",
) -> dict:
    """
    Quick synthesis function

    Args:
        text: Text to synthesize
        speaker: Speaker name
        mode: Inference mode
        version: CosyVoice version
        output_format: Output format ("wav" or "mp3")

    Returns:
        Dict with synthesis results
    """
    tts = CosyVoiceTTS(version=version, mode=mode)

    # Synthesize to WAV
    result = tts.synthesize(text, speaker=speaker)

    # Convert to MP3 if requested
    if output_format == "mp3":
        mp3_path = tts.convert_wav_to_mp3(result["audio_path"])
        result["audio_path"] = mp3_path
        result["format"] = "mp3"
    else:
        result["format"] = "wav"

    return result


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    print("Testing CosyVoice TTS...")
    print("=" * 50)

    # Test 1: Simple instruct mode
    print("\n1. Testing instruct mode...")
    result = synthesize_speech(
        text="你好，这是一个测试。",
        speaker="中文女",
        mode="instruct",
        output_format="wav",
    )
    print(f"✅ Audio saved to: {result['audio_path']}")
    print(f"   Duration: {result['duration']:.2f}s")

    # Test 2: Convert to MP3
    print("\n2. Testing MP3 conversion...")
    tts = CosyVoiceTTS()
    mp3_path = tts.convert_wav_to_mp3(result['audio_path'])
    print(f"✅ MP3 saved to: {mp3_path}")

    print("\n" + "=" * 50)
    print("Test completed!")
