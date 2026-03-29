"""Summary and report helpers."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def complexity_summary(summary: dict[str, Any]) -> dict[str, int]:
    # Aggregate complexity details across functions and methods
    # to provide one compact indicator block for dashboards.
    # Counters are resilient to missing keys in partial payloads.
    loops_count = 0
    recursion_count = 0

    for function in summary.get("functions", []):
        complexity = function.get("complexity", {})
        loops_count += int(complexity.get("loops", 0))
        recursion_count += int(bool(complexity.get("is_recursive", False)))

    for cls in summary.get("classes", []):
        for method in cls.get("methods", []):
            complexity = method.get("complexity", {})
            loops_count += int(complexity.get("loops", 0))
            recursion_count += int(bool(complexity.get("is_recursive", False)))

    return {
        "total_loops": loops_count,
        "recursive_items": recursion_count,
    }


def build_summary(extracted: dict[str, Any], file_name: str | None = None) -> dict[str, Any]:
    # Build the canonical JSON response shape expected by
    # API consumers, templates, and CLI output handlers.
    # Optional file name tags each summary in multi-file mode.
    functions = extracted.get("functions", [])
    classes = extracted.get("classes", [])
    methods_count = sum(len(cls.get("methods", [])) for cls in classes)

    summary = {
        "file_name": file_name or "",
        "total_functions": len(functions),
        "total_classes": len(classes),
        "total_methods": methods_count,
        "functions": functions,
        "classes": classes,
    }
    summary["complexity"] = complexity_summary(summary)
    return summary


def save_summary_report(summary: dict[str, Any], output_dir: Path) -> Path:
    # Persist analysis JSON to disk for auditing and sharing.
    # The timestamp in file name avoids accidental overwrites.
    # Output directory is created lazily when first needed.
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_stem = summary.get("file_name", "analysis") or "analysis"
    safe_name = Path(file_stem).stem.replace(" ", "_")
    output_path = output_dir / f"{safe_name}_{timestamp}.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return output_path

