# ===========================================
# CaseMind AI — AI Client (Groq / OpenAI-compatible)
# ===========================================
# Handles secure initialization of the Groq API client via the
# OpenAI-compatible SDK. Reads the API key from a .env file and
# provides a reusable, cached client instance for use across the
# application.
#
# NOTE: This module is internally powered by Groq (using the OpenAI
# SDK's OpenAI-compatible interface). The function names below
# (get_groq_client / is_groq_configured) are kept for backward
# compatibility with the rest of the codebase, but they now return
# and validate a Groq-backed client.

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
#  Load environment variables from .env at the project root
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
#  Groq configuration
# ---------------------------------------------------------------------------
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Vision-capable models (for the Image Agent). Primary is tried first;
# if the account/tier rejects it (e.g. decommissioned), the client falls
# back to the secondary model automatically.
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_VISION_MODEL_FALLBACK = "qwen/qwen3.6-27b"

# ---------------------------------------------------------------------------
#  Module-level singleton
# ---------------------------------------------------------------------------
_client: OpenAI | None = None


def is_groq_configured() -> bool:
    """Check whether a Groq API key is present in the environment.

    Kept as ``is_groq_configured`` for backward compatibility with
    existing imports elsewhere in the project — internally it checks
    ``GROQ_API_KEY``.
    """
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key) and key != "your_groq_api_key_here"


def get_groq_client() -> OpenAI:
    """
    Return a configured Groq client (OpenAI-compatible SDK) singleton.

    Kept as ``get_groq_client`` for backward compatibility with
    existing imports elsewhere in the project — internally it builds
    and returns an ``OpenAI`` client pointed at the Groq API.

    The client is created once and reused for the lifetime of the process.
    Raises ``RuntimeError`` if the API key is missing or still set to the
    placeholder value from ``.env.example``.
    """
    global _client

    if _client is not None:
        return _client

    if not is_groq_configured():
        raise RuntimeError(
            "Groq API key is not configured. "
            "Please set GROQ_API_KEY in your .env file."
        )

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    _client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    return _client


# ---------------------------------------------------------------------------
#  Convenience aliases (clearer names for new code)
# ---------------------------------------------------------------------------
is_groq_configured = is_groq_configured
get_groq_client = get_groq_client
