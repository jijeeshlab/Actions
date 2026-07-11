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


def first_function_name(summaries: list[dict]) -> str:
    for summary in summaries:
        for function in summary.get("functions", []):
            return function.get("name", "service_operation")

    return "service_operation"


def function_details(summaries: list[dict]) -> str:
    lines = []

    for summary in summaries:
        file_name = summary.get("file", "").replace("source/", "")

        lines.append(f"### Source File: `{file_name}`")
        lines.append("")

        if not summary.get("exists"):
            lines.append("The source file was not available during LLD generation.")
            lines.append("")
            continue

        module_docstring = summary.get("module_docstring", "")
        if module_docstring:
            lines.append(f"**Module Description:** {module_docstring}")
            lines.append("")

        functions = summary.get("functions", [])

        if not functions:
            lines.append("No Python functions were detected in this file.")
            lines.append("")
            continue

        for function in functions:
            args = function.get("args", [])
            returns = function.get("returns", "")
            docstring = function.get("docstring", "")

            lines.append(f"#### Function: `{function['name']}`")
            lines.append("")
            lines.append("- **Responsibility**:")
            lines.append(
                f"  - {docstring if docstring else 'No function-level documentation was provided.'}"
            )
            lines.append("")
            lines.append("- **Attributes/Properties**:")
            lines.append("  - Not applicable for this function-level simulation.")
            lines.append("")
            lines.append("- **Methods/Functions**:")
            lines.append(f"  - `{function['name']}({', '.join(args)})`")
            lines.append("")
            lines.append("- **Inputs**:")
            if args:
                for arg in args:
                    lines.append(f"  - `{arg}`")
            else:
                lines.append("  - No explicit inputs detected.")
            lines.append("")
            lines.append("- **Outputs**:")
            lines.append(f"  - `{returns if returns else 'Not specified'}`")
            lines.append("")

    return "\n".join(lines)


def get_changed_file_names(changed_files: list[str]) -> list[str]:
    return changed_files if changed_files else []


def generate_lld_content(
    service_config: dict,
    request: dict,
    summaries: list[dict]
) -> str:
    service = service_config["service"]
    today = date.today().isoformat()

    source_repo_full = request.get("source_repo_full", "")
    source_pr_number = request.get("source_pr_number", "")
    source_pr_title = request.get("source_pr_title", "")
    source_pr_url = request.get("source_pr_url", "")
    changed_files = service_config.get("changed_files", [])
    main_function = first_function_name(summaries)

    return f"""# Low-Level Design (LLD): {service}

**Author**: Jijeesh Valappil  
**Date**: {today}  
**Version**: 1.0  
**Related HLD**: To be linked after documentation review.

---

## 1. Introduction

### 1.1. Overview

This LLD provides the detailed design for `{service}` based on source code changes detected during pull request validation.

**Source Repository**: `{source_repo_full}`  
**Source PR**: `{source_pr_number}`  
**Source PR Title**: {source_pr_title}  
**Source PR URL**: {source_pr_url}

---

## 2. Detailed Design

### 2.1. Class Diagram

```mermaid
classDiagram
    class SourceRepository {{
        +pull_request()
        +changed_files()
    }}

    class DocumentationImpactWorkflow {{
        +read_documentation_map()
        +detect_impacted_service()
        +create_doc_request()
    }}

    class DocumentationGenerator {{
        +inspect_source_code()
        +generate_hld()
        +generate_lld()
    }}

    SourceRepository --> DocumentationImpactWorkflow
    DocumentationImpactWorkflow --> DocumentationGenerator
