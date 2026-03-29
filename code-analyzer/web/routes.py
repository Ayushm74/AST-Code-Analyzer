"""Flask routes for web UI and API."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, render_template, request

from analyzer.ai_doc_generator import generate_docstring, summarize_function_plain_english
from analyzer.extractor import extract_code_details
from analyzer.parser import parse_code_to_ast
from analyzer.summarizer import build_summary, save_summary_report
from config import OUTPUT_DIR
from utils.file_loader import load_python_file

web_bp = Blueprint("web", __name__)


def _enhance_with_ai(summary: dict[str, Any], raw_code: str) -> dict[str, Any]:
    # Add optional AI-generated content for functions and methods.
    # We parse source once more to map node names to source snippets.
    # Any missing snippets are skipped to keep flow robust.
    try:
        tree = ast.parse(raw_code)
    except SyntaxError:
        return summary

    source_map: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            source_map[node.name] = ast.get_source_segment(raw_code, node) or ""

    for fn in summary.get("functions", []):
        snippet = source_map.get(fn.get("name", ""), "")
        if snippet:
            if not fn.get("docstring"):
                fn["suggested_docstring"] = generate_docstring(snippet)
            fn["plain_english_summary"] = summarize_function_plain_english(snippet)

    for cls in summary.get("classes", []):
        for method in cls.get("methods", []):
            snippet = source_map.get(method.get("name", ""), "")
            if snippet:
                if not method.get("docstring"):
                    method["suggested_docstring"] = generate_docstring(snippet)
                method["plain_english_summary"] = summarize_function_plain_english(snippet)
    return summary


def _analyze_text(code_text: str, file_name: str = "pasted_code.py") -> dict[str, Any]:
    # Run full AST pipeline and persist JSON report automatically.
    # This helper centralizes behavior used by UI and API endpoints.
    # It guarantees a consistent response shape in all flows.
    tree = parse_code_to_ast(code_text)
    extracted = extract_code_details(tree)
    summary = build_summary(extracted, file_name=file_name)
    summary = _enhance_with_ai(summary, code_text)
    report_path = save_summary_report(summary, OUTPUT_DIR)
    summary["saved_report"] = str(report_path)
    return summary


@web_bp.route("/", methods=["GET"])
def index() -> str:
    # Render home page with upload and code paste controls.
    # Keeping this route minimal makes it easy to maintain.
    # Any analysis logic stays in dedicated handlers.
    return render_template("index.html")


@web_bp.route("/analyze", methods=["POST"])
def analyze() -> Any:
    # Accept either uploaded file or pasted code in one endpoint.
    # Validate input and return clear JSON errors when invalid.
    # On success return analysis payload ready for API clients.
    file = request.files.get("file")
    raw_code = (request.form.get("code") or "").strip()

    try:
        if file and file.filename:
            temp_path = Path(OUTPUT_DIR) / file.filename
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(temp_path)
            code_text = load_python_file(temp_path)
            summary = _analyze_text(code_text, file_name=file.filename)
            temp_path.unlink(missing_ok=True)
            return jsonify(summary)

        if raw_code:
            summary = _analyze_text(raw_code, file_name="pasted_code.py")
            return jsonify(summary)

        return jsonify({"error": "No input provided. Upload a file or paste code."}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@web_bp.route("/result", methods=["POST"])
def result() -> Any:
    # Handle web form submission and render template output.
    # The same analysis helper is used for consistency with API.
    # Errors are shown on the page instead of raising server traces.
    file = request.files.get("file")
    raw_code = (request.form.get("code") or "").strip()

    try:
        if file and file.filename:
            temp_path = Path(OUTPUT_DIR) / file.filename
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(temp_path)
            code_text = load_python_file(temp_path)
            summary = _analyze_text(code_text, file_name=file.filename)
            temp_path.unlink(missing_ok=True)
            return render_template("result.html", result=summary, error="")

        if raw_code:
            summary = _analyze_text(raw_code, file_name="pasted_code.py")
            return render_template("result.html", result=summary, error="")

        return render_template("result.html", result=None, error="No input provided.")
    except Exception as exc:
        return render_template("result.html", result=None, error=str(exc))

