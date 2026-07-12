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

        docstring = summary.get(
            "module_docstring",
            ""
        )

        if docstring:
            descriptions.append(
                docstring
            )

    return descriptions


def infer_service_overview(
    service: str,
    summaries: list[dict]
) -> str:

    content = []

    for summary in summaries:

        content.append(
            summary.get(
                "module_docstring",
                ""
            )
        )

        for function in summary.get(
            "functions",
            []
        ):

            content.append(
                function.get(
                    "name",
                    ""
                )
            )

    combined = (
        " ".join(content)
        .lower()
    )

    if "network" in combined:
        return (
            "Provides automated network "
            "deployment, connectivity and "
            "security services."
        )

    if "vpn" in combined:
        return (
            "Provides hybrid cloud "
            "connectivity services."
        )

    if "storage" in combined:
        return (
            "Provides storage automation "
            "services."
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

    functions = (
        get_function_names(
            summaries
        )
    )

    modules = (
        get_module_descriptions(
            summaries
        )
    )

    today = (
        date.today()
        .isoformat()
    )

    lines = [

        f"# High-Level Design (HLD): {service_name}",
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
        overview,
        "",
        "## 1.2 Scope",
        "",
        "### In Scope",
        "",
        bullet_list(functions),
        "",
        "### Out of Scope",
        "",
        "- Functionality not identified from source code.",
        "",
        "---",
        "",
        "# 2. Business Requirements",
        "",
        bullet_list(functions),
        "",
        "---",
        "",
        "# 3. System Architecture",
        "",
        "## 3.1 Architecture Overview",
        "",
        "```text",
        "Source Repository",
        "       |",
        "       v",
        "Documentation Generation",
        "       |",
        "       v",
        "Generated HLD",
        "```",
        "",
        "## 3.2 Components",
        "",
        bullet_list(modules),
        "",
        "---",
        "",
        "# 4. Data Flow",
        "",
        "Source Code -> Documentation Pipeline -> HLD",
        "",
        "---",
        "",
        "# 5. Integrations",
        "",
        "- GitHub",
        "- GitHub Actions",
        "- Documentation-as-Code",
        "",
        "---",
        "",
        "# 6. Security",
        "",
        "- Security review required.",
        "- Access control TBD.",
        "- Audit logging TBD.",
        "",
        "---",
        "",
        "# 7. Operations",
        "",
        "- Automated GitHub Actions execution",
        "- Generated documentation lifecycle",
        "",
        "---",
        "",
        "# 8. Risks",
        "",
        "- Generated content may require manual review.",
        "- Business requirements may not be fully visible in source code.",
        "",
        "---",
        "",
        "# 9. Open Questions",
        "",
        "- Additional integrations required?",
        "- Additional business requirements?"
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

    for service in services:

        output_file = Path(
            service["hld"]
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            build_hld(
                service,
                summaries
            ),
            encoding="utf-8"
        )

        print(
            f"HLD generated: {output_file}"
        )


if __name__ == "__main__":
    main()
