"""File and folder loading utilities."""

from __future__ import annotations

from pathlib import Path


def load_python_file(file_path: str | Path) -> str:
    # Validate file existence and extension before reading.
    # This prevents confusing parser errors on bad paths.
    # All read failures are surfaced with clear text.
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".py":
        raise ValueError("Only .py files are supported.")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Could not read file: {path}") from exc


def load_python_files_from_folder(folder_path: str | Path) -> dict[str, str]:
    # Collect all Python files recursively for bulk analysis.
    # File content is loaded into a mapping by absolute path.
    # Empty folders raise an explicit message for users.
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f"Invalid folder path: {folder}")

    files = sorted(folder.rglob("*.py"))
    if not files:
        raise ValueError("No Python files found in folder.")

    loaded: dict[str, str] = {}
    for file_path in files:
        loaded[str(file_path)] = load_python_file(file_path)
    return loaded

