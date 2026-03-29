"""AST parser utilities."""

from __future__ import annotations

import ast


def parse_code_to_ast(code: str) -> ast.AST:
    # Guard against empty payloads early so callers receive
    # a clear and user-friendly message before parsing starts.
    # This keeps error handling consistent for web and CLI paths.
    if not code or not code.strip():
        raise ValueError("Input code is empty.")

    # Parse source into a Python AST tree using built-in parser.
    # Syntax issues are rethrown with cleaner text for UI/API.
    # Returning the tree keeps this function focused and reusable.
    try:
        return ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f"Invalid Python code: {exc}") from exc

