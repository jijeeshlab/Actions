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
        return "- To Be Determined (TBD)"

    return "\n".join(
        [
            f"- {item}"
            for item in items
        ]
    )


def function_names(
    summaries: list[dict]
) -> list[str]:

    names = []

    for summary in summaries:

        for function in summary.get(
            "functions",
            []
        ):

            names.append(
                f"`{function['name']}()`"
            )

    return names


def build_component_breakdown(
    summaries: list[dict]
) -> str:

    lines = []

    for summary in summaries:

        file_name = (
            summary.get(
                "file",
                ""
            )
            .replace(
                "source/",
                ""
            )
        )

        lines.append(
            f"### Source File: `{file_name}`"
        )

        lines.append("")

        functions = summary.get(
            "functions",
            []
        )

        if not functions:

            lines.append(
                "No functions detected."
            )

            lines.append("")
            continue

        for function in functions:

            args = (
                ", ".join(
                    function["args"]
                )
                or "None"
            )

            returns = (
                function["returns"]
                or "None"
            )

            docstring = (
                function["docstring"]
                or "No documentation available."
            )

            lines.append(
                f"#### Function: `{function['name']}`"
            )

            lines.append("")
            lines.append(
                f"**Description:** {docstring}"
            )
            lines.append("")
            lines.append(
                f"**Parameters:** {args}"
            )
            lines.append("")
            lines.append(
                f"**Returns:** {returns}"
            )
            lines.append("")

    return "\n".join(lines)


def build_lld(
    service_info: dict,
    request: dict,
    summaries: list[dict]
) -> str:

    service_name = (
        service_info["service"]
    )

    today = (
        date.today()
        .isoformat()
    )

    source_repo = request.get(
        "source_repo_full",
        "TBD"
    )

    source_pr_number = request.get(
        "source_pr_number",
        "TBD"
    )

    source_pr_title = request.get(
        "source_pr_title",
        "TBD"
    )

    changed_files = (
        service_info.get(
            "changed_files",
            []
        )
        or request.get(
            "changed_files",
            []
        )
    )

    funcs = function_names(
        summaries
    )

    lines = [

        f"# Low-Level Design (LLD): {service_name}",
        "",
        "**Author**: Jijeesh Valappil",
        f"**Date**: {today}",
        "**Version**: 1.0",
        "",
        f"**Source Repository**: `{source_repo}`",
        f"**Source PR Number**: `{source_pr_number}`",
        f"**Source PR Title**: {source_pr_title}",
        "",
        "---",
        "",
        "# 1. Introduction",
        "",
        "## 1.1 Overview",
        "",
        (
            "This document describes the low-level "
            "implementation architecture generated "
            "from source code changes."
        ),
        "",
        "---",
        "",
        "# 2. Detailed Design",
        "",
        "## 2.1 Class Diagram",
        "",
        "```mermaid",
        "classDiagram",
        "    class SourceRepository",
        "    class DocumentationGenerator",
        "",
        "    SourceRepository --> DocumentationGenerator",
        "```",
        "",
        "## 2.2 Sequence Diagram",
        "",
        "```mermaid",
        "sequenceDiagram",
        "    participant Developer",
        "    participant SourceRepo",
        "    participant ActionsRepo",
        "    participant DocsRepo",
        "",
        "    Developer->>SourceRepo: Code Change",
        "    SourceRepo->>ActionsRepo: Detect Impact",
        "    ActionsRepo->>DocsRepo: Dispatch Event",
        "    DocsRepo->>DocsRepo: Generate Documentation",
        "```",
        "",
        "## 2.3 Component Breakdown",
        "",
        build_component_breakdown(
            summaries
        ),
        "",
        "---",
        "",
        "# 3. Function Inventory",
        "",
        bullet_list(funcs),
        "",
        "---",
        "",
        "# 4. Error Handling",
        "",
        "- Input validation",
        "- Logging",
        "- Exception handling",
        "",
        "---",
        "",
        "# 5. Security Considerations",
        "",
        "- GitHub Secrets used for authentication",
        "- Token values must never be logged",
        "- Review generated documentation before publication",
        "",
        "---",
        "",
        "# 6. Changed Files",
        "",
        bullet_list(changed_files),
        "",
        "---",
        "",
        "# 7. Open Questions",
        "",
        "- Additional business rules required?",
        "- Additional architectural requirements required?"
    ]

    return "\n".join(lines) + "\n"


def main():

    request = read_json(
        DOC_REQUEST_FILE
    )

    services = request.get(
        "impacted_services",
        []
    )

    top_level_changed_files = request.get(
        "changed_files",
        []
    )

    for service in services:

        changed_files = (
            service.get(
                "changed_files",
                []
            )
            or top_level_changed_files
        )

        summaries = inspect_changed_files(
            changed_files
        )

        output_file = Path(
            service["lld"]
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            build_lld(
                service,
                request,
                summaries
            ),
            encoding="utf-8"
        )

        print(
            f"LLD generated: {output_file}"
        )


if __name__ == "__main__":
    main()
