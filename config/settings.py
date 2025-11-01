import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger("hijacker.app")


class _Settings(BaseSettings):
    root_path: Path = Path(".").resolve().parent
    hot_word_model: str = "Hey-Wobble_en_windows_v3_0_0.ppn"
    agent_model: str = "qwen3:8b-q4_K_M"
    stt_model: str = "vosk-model-small-en-us-0.15"
    tts_model: str = "tts_models/en/vctk/vits"
    tts_speaker: str = "p262"
    tts_language: str = "en"
    system_prompt: str = ("You are a helpful assistant. "
                          "You always talk like a very wise and old magician!"
                          "Don't use any emojis! "
                          "On error retry a maximum amount of 2 times."
                          "NEVER use any markdown formatting. (e.g. **bold** or *italic*...)!")
    # TODO: load keys from .env


settings = _Settings()
