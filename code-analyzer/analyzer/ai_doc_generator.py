"""Optional OpenAI docstring and function summary helper."""

from __future__ import annotations

from typing import Any

from config import OPENAI_API_KEY, OPENAI_MODEL

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]


def _client() -> Any | None:
    # Build OpenAI client only when package and key are available.
    # Returning None keeps caller logic simple and fully optional.
    # This avoids forcing API usage in local/offline executions.
    if not OPENAI_API_KEY or OpenAI is None:
        return None
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_docstring(code_snippet: str) -> str:
    # Ask the model for a concise production-style docstring.
    # On any API/runtime issue we degrade gracefully and return
    # an empty string so analysis flow never fails.
    client = _client()
    if client is None:
        return ""

    prompt = (
        "Generate a concise Python docstring for this function/method. "
        "Return only the docstring text without quotes:\n\n"
        f"{code_snippet}"
    )

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.2,
        )
        return (response.output_text or "").strip()
    except Exception:
        return ""


def summarize_function_plain_english(code_snippet: str) -> str:
    # Produce a short plain-English behavior summary suitable for UI.
    # This is optional enrichment and should never break core analysis.
    # Empty response is acceptable when service is unavailable.
    client = _client()
    if client is None:
        return ""

    prompt = (
        "Explain what this Python function does in 1-2 short sentences:\n\n"
        f"{code_snippet}"
    )
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.2,
        )
        return (response.output_text or "").strip()
    except Exception:
        return ""

