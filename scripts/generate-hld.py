import ast
import json
from datetime import date
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
SOURCE_DIR = Path("source")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def inspect_python_file(
    file_path: Path
) -> dict:

    if not file_path.exists():
        return {
            "file": str(file_path),
            "exists": False,
            "module_docstring": "",
            "functions": [],
        }

    content = file_path.read_text(
        encoding="utf-8"
    )

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

        if isinstance(
            node,
            ast.FunctionDef
        ):

            functions.append(
                {
                    "name": node.name,
                    "args": [
                        arg.arg
                        for arg in node.args.args
                    ],
                    "returns":
                        ast.unparse(node.returns)
                        if node.returns
                        else "",
                    "docstring":
                        ast.get_docstring(node)
                        or "",
                }
            )

    return {
        "file": str(file_path),
        "exists": True,
        "module_docstring":
            ast.get_docstring(tree)
            or "",
        "functions":
            functions,
    }


def inspect_changed_files(
    changed_files: list[str]
) -> list[dict]:

    summaries = []

    for changed_file in changed_files:

        source_file = (
            SOURCE_DIR / changed_file
        )

        summaries.append(
            inspect_python_file(
                source_file
            )
        )

    return summaries


def bullet_list(
    items: list[str]
) -> str:

    if not items:
        return "- Not identified."

    return "\n".join(
        [
            f"- {item}"
            for item in items
        ]
    )


def get_function_names(
    summaries: list[dict]
) -> list[str]:

    names = []

    for summary in summaries:

        for function in summary.get(
            "functions",
            []
        ):

            names.append(
                function["name"]
            )

    return names


def get_module_descriptions(
    summaries: list[dict]
) -> list[str]:

    descriptions = []

    for summary in summaries:

        module_docstring = (
            summary.get(
                "module_docstring",
                ""
            )
        )

        if module_docstring:
            descriptions.append(
                module_docstring
            )

    return descriptions


def infer_service_overview(
    service: str,
    summaries: list[dict]
) -> str:

    combined_text = " ".join(
        [
            summary.get(
                "module_docstring",
                ""
            )
            for summary in summaries
        ]
    ).lower()

    combined_functions = " ".join(
        [
            function.get("name", "")
            for summary in summaries
            for function in summary.get(
                "functions",
                []
            )
        ]
    ).lower()

    combined = (
        f"{combined_text} "
        f"{combined_functions}"
    )

    if "network" in combined:
        return (
            "Provides automated network "
            "deployment, segmentation, "
            "security and connectivity "
            "capabilities."
        )

    if "vpn" in combined:
        return (
            "Provides hybrid cloud "
            "connectivity services."
        )

    if "storage" in combined:
        return (
            "Provides storage automation "
            "and storage gateway services."
        )

    return (
        f"{service} provides "
        f"automated infrastructure "
        f"services."
    )


def build_hld(
    service_info: dict,
    summaries: list[dict]
) -> str:

    service_name = (
        service_info["service"]
    )

    overview = (
        infer_service_overview(
            service_name,
            summaries
        )
    )

    function_names = (
        get_function_names(
            summaries
        )
    )

    module_descriptions = (
        get_module_descriptions(
            summaries
        )
    )

    today = (
        date.today()
        .isoformat()
    )

    return f"""# High-Level Design (HLD): {service_name}

**Author**: Documentation Automation

**Date**: {today}

**Version**: 1.0

---

# 1. Introduction

## 1.1 Overview

{overview}

## 1.2 Scope

### In Scope

{bullet_list(function_names)}

### Out of Scope

- Functionality not identified from source code.

## 1.3 Goals and Objectives

- Infrastructure automation
- Standardized deployments
- Documentation-as-Code

## 1.4 Acronyms and Abbreviations

| Term | Definition |
|------|------------|
| HLD | High Level Design |
| LLD | Low Level Design |

---

# 2. Requirements

## 2.1 Functional Requirements

{bullet_list(function_names)}

## 2.2 Non-Functional Requirements

- Performance: TBD
- Scalability: TBD
- Availability: TBD
- Security: TBD
- Maintainability: TBD
- Usability: TBD

---

# 3. System Architecture

## 3.1 Architectural Diagram

```text
Source Repository
        |
        v
Documentation Pipeline
        |
        v
Generated HLD / LLD
