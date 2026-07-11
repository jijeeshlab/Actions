import ast
import json
from datetime import date
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
SOURCE_DIR = Path("source")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def inspect_python_file(file_path: Path) -> dict:
    if not file_path.exists():
        return {
            "file": str(file_path),
            "exists": False,
            "module_docstring": "",
            "functions": [],
        }

    content = file_path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "file": str(file_path),
            "exists": True,
            "module_docstring": "",
            "functions": [],
        }

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(
                {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "returns": ast.unparse(node.returns) if node.returns else "",
                    "docstring": ast.get_docstring(node) or "",
                }
            )

    return {
        "file": str(file_path),
        "exists": True,
        "module_docstring": ast.get_docstring(tree) or "",
        "functions": functions,
    }


def inspect_changed_files(changed_files: list[str]) -> list[dict]:
    summaries = []

    for changed_file in changed_files:
        source_file = SOURCE_DIR / changed_file
        summaries.append(inspect_python_file(source_file))

    return summaries


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- Not identified."

    return "\n".join([f"- {item}" for item in items])


def get_function_names(summaries: list[dict]) -> list[str]:
    names = []

    for summary in summaries:
        for function in summary.get("functions", []):
            names.append(function["name"])

    return names


def get_module_descriptions(summaries: list[dict]) -> list[str]:
    descriptions = []

    for summary in summaries:
        module_docstring = summary.get("module_docstring", "")
        if module_docstring:
            descriptions.append(module_docstring)

    return descriptions


def infer_service_overview(service: str, summaries: list[dict]) -> str:
    combined_text = " ".join(
        [
            summary.get("module_docstring", "")
            for summary in summaries
        ]
    ).lower()

    combined_functions = " ".join(
        [
            function.get("name", "")
            for summary in summaries
            for function in summary.get("functions", [])
        ]
    ).lower()

    combined = f"{combined
