"""Application configuration for AI Code Analyzer."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
SAMPLES_DIR = BASE_DIR / "samples"
ALLOWED_EXTENSIONS = {"py"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

# OpenAI integration is optional and only used when key exists.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

