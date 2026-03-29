"""Entry point for AI Code Analyzer web and CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from flask import Flask

from analyzer.extractor import extract_code_details
from analyzer.parser import parse_code_to_ast
from analyzer.summarizer import build_summary, save_summary_report
from config import MAX_CONTENT_LENGTH, OUTPUT_DIR
from utils.file_loader import load_python_file, load_python_files_from_folder
from web.routes import web_bp


def create_app() -> Flask:
    # Initialize Flask app and register blueprint routes.
    # Centralized app factory keeps runtime and tests cleaner.
    # Config values are loaded here for predictable behavior.
    app = Flask(__name__, template_folder="web/templates", static_folder="static")
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.register_blueprint(web_bp)
    return app


def analyze_single_code(code_text: str, file_name: str) -> dict[str, Any]:
    # Execute parser -> extractor -> summarizer pipeline.
    # This reusable helper powers CLI and can be imported
    # by tests or scripts without depending on Flask app.
    tree = parse_code_to_ast(code_text)
    extracted = extract_code_details(tree)
    return build_summary(extracted, file_name=file_name)


def run_cli(file_path: str | None, folder_path: str | None) -> None:
    # Support command-line analysis for interview and automation use.
    # Either a single file or recursive folder can be processed.
    # Each result is printed and saved as a JSON report.
    if file_path:
        code_text = load_python_file(file_path)
        summary = analyze_single_code(code_text, file_name=Path(file_path).name)
        report_path = save_summary_report(summary, OUTPUT_DIR)
        print(json.dumps(summary, indent=2))
        print(f"Saved report: {report_path}")
        return

    if folder_path:
        file_map = load_python_files_from_folder(folder_path)
        all_reports: list[dict[str, Any]] = []
        for file_name, code_text in file_map.items():
            summary = analyze_single_code(code_text, file_name=Path(file_name).name)
            report_path = save_summary_report(summary, OUTPUT_DIR)
            summary["saved_report"] = str(report_path)
            all_reports.append(summary)

        print(json.dumps({"analyzed_files": len(all_reports), "reports": all_reports}, indent=2))
        return

    raise ValueError("CLI requires --file <path> or --folder <path>.")


if __name__ == "__main__":
    # Parse optional CLI arguments; default behavior starts web app.
    # This dual-mode entrypoint keeps startup simple for beginners.
    # Running "python app.py" launches Flask on localhost:5000.
    parser = argparse.ArgumentParser(description="AI Code Analyzer")
    parser.add_argument("--file", type=str, help="Analyze a single Python file")
    parser.add_argument("--folder", type=str, help="Analyze all Python files in a folder")
    args = parser.parse_args()

    if args.file or args.folder:
        run_cli(args.file, args.folder)
    else:
        app = create_app()
        app.run(host="127.0.0.1", port=5000, debug=False)

