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


def build_function_section(
    summaries: list[dict]
) -> str:

    sections = []

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

        sections.append(
            f"## Source File: {file_name}"
        )

        sections.append("")

        functions = summary.get(
            "functions",
            []
        )

        if not functions:

            sections.append(
                "No functions detected."
            )

            sections.append("")
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

            sections.append(
                f"### Function: {function['name']}"
            )

            sections.append("")

            sections.append(
                f"**Description:** {docstring}"
            )

            sections.append("")

            sections.append(
                f"**Parameters:** {args}"
            )

            sections.append("")

            sections.append(
                f"**Returns:** {returns}"
            )

            sections.append("")

    return "\n".join(sections)


def build_lld(
    service_info: dict,
    summaries: list[dict]
) -> str:

    service_name = (
        service_info["service"]
    )

    today = (
        date.today()
        .isoformat()
    )

    function_names = (
        get_function_names(
            summaries
        )
    )

    lines = [

        f"# Low-Level Design (LLD): {service_name}",
        "",
        "**Author:** Documentation Automation",
        "",
        f"**Date:** {today}",
        "",
        "**Version:** 1.0",
        "",
        "---",
        "",
        "# 1. Introduction",
        "",
        "## 1.1 Overview",
        "",
        (
            "This document describes the "
            "detailed implementation design "
            "for the identified service."
        ),
        "",
        "---",
        "",
        "# 2. Detailed Design",
        "",
        "## 2.1 Components",
        "",
        bullet_list(function_names),
        "",
        "---",
        "",
        "# 3. Function Details",
        "",
        build_function_section(
            summaries
        ),
        "",
        "---",
        "",
        "# 4. Sequence Flow",
        "",
        "```text",
        "Caller",
        "   |",
        "   v",
        "Function",
        "   |",
        "   v",
        "Return Result",
        "```",
        "",
        "---",
        "",
        "# 5. Error Handling",
        "",
        "- Input validation",
        "- Exception handling",
        "- Logging",
        "",
        "---",
        "",
        "# 6. Security Considerations",
        "",
        "- Review required",
        "- Access control TBD",
        "- Audit logging TBD",
        "",
        "---",
        "",
        "# 7. Unit Testing",
        "",
        bullet_list(function_names),
        "",
        "---",
        "",
        "# 8. Open Questions",
        "",
        "- Additional business rules?",
        "- Additional technical requirements?"
    ]

    return "\n".join(lines)


def main():

    request = read_json(
        DOC_REQUEST_FILE
    )

    services = request.get(
        "impacted_services",
        []
    )

    changed_files = request.get(
        "changed_files",
        []
    )

    summaries = inspect_changed_files(
        changed_files
    )

    for service_info in services:

        output_file = Path(
            service_info["lld"]
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            build_lld(
                service_info,
                summaries
            ),
            encoding="utf-8"
        )

        print(
            f"LLD generated: {output_file}"
        )


if __name__ == "__main__":
    main()
