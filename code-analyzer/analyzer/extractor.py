"""AST extraction logic for functions, classes, and complexity."""

from __future__ import annotations

import ast
from typing import Any


def _arguments_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    # Collect positional, vararg, keyword-only, and kwarg names
    # to provide a complete signature overview for each function.
    # This output is plain text for easy display in UI tables.
    args = [arg.arg for arg in node.args.args]
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    args.extend(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    return args


def _count_loops(node: ast.AST) -> int:
    # Walk the subtree and count loop constructs.
    # We include both for and while nodes for clarity.
    # This provides a simple complexity indicator.
    return sum(
        1
        for subnode in ast.walk(node)
        if isinstance(subnode, (ast.For, ast.AsyncFor, ast.While))
    )


def _is_recursive(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    function_name: str,
) -> bool:
    # Recursion detection scans all call expressions in function body.
    # We check direct calls like "foo()" and attribute calls where
    # the final attribute matches the function name.
    for subnode in ast.walk(node):
        if not isinstance(subnode, ast.Call):
            continue
        if isinstance(subnode.func, ast.Name) and subnode.func.id == function_name:
            return True
        if isinstance(subnode.func, ast.Attribute) and subnode.func.attr == function_name:
            return True
    return False


def _extract_method(method_node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    # Convert method AST node into serializable metadata.
    # This includes identity, signature, documentation, and
    # basic complexity hints for interview-style analysis.
    name = method_node.name
    return {
        "name": name,
        "arguments": _arguments_from_node(method_node),
        "docstring": ast.get_docstring(method_node) or "",
        "line_number": getattr(method_node, "lineno", None),
        "complexity": {
            "loops": _count_loops(method_node),
            "is_recursive": _is_recursive(method_node, name),
        },
    }


def extract_code_details(tree: ast.AST) -> dict[str, Any]:
    # Traverse the AST once and gather function and class metadata.
    # Top-level functions are separated from class methods for
    # cleaner result rendering and precise counts.
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods: list[dict[str, Any]] = []
            for class_item in node.body:
                if isinstance(class_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(_extract_method(class_item))

            classes.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "line_number": getattr(node, "lineno", None),
                    "methods": methods,
                }
            )

    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_extract_method(node))

    return {"functions": functions, "classes": classes}

