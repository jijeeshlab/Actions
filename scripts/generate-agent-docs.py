import ast
import json
import re
from datetime import date
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
SOURCE_DIR = Path("source")
AGENTS_DIR = Path("_actions/agents")


HLD_AGENT_FILE = AGENTS_DIR / "hld-agent.md"
LLD_AGENT_FILE = AGENTS_DIR / "lld-agent.md"
IMPACT_AGENT_FILE = AGENTS_DIR / "impact-agent.md"
DIAGRAM_AGENT_FILE = AGENTS_DIR / "diagram-agent.md"


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


def read_text_file(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def load_agent_context() -> dict:
    return {
        "hld_agent": read_text_file(HLD_AGENT_FILE),
        "lld_agent": read_text_file(LLD_AGENT_FILE),
        "impact_agent": read_text_file(IMPACT_AGENT_FILE),
        "diagram_agent": read_text_file(DIAGRAM_AGENT_FILE),
    }


def inspect_python_file(file_path: Path) -> dict:
    if not file_path.exists():
        return {
            "file": str(file_path),
            "type": "python",
            "exists": False,
            "module_docstring": "",
            "functions": [],
        }

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "file": str(file_path),
            "type": "python",
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
                    "args": [
                        arg.arg
                        for arg in node.args.args
                    ],
                    "returns": ast.unparse(node.returns) if node.returns else "",
                    "docstring": ast.get_docstring(node) or "",
                }
            )

    return {
        "file": str(file_path),
        "type": "python",
        "exists": True,
        "module_docstring": ast.get_docstring(tree) or "",
        "functions": functions,
    }


def inspect_shell_file(file_path: Path) -> dict:
    if not file_path.exists():
        return {
            "file": str(file_path),
            "type": "shell",
            "exists": False,
            "module_docstring": "",
            "functions": [],
        }

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    functions = []

    pattern = re.compile(
        r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\s*\{",
        re.MULTILINE
    )

    for match in pattern.finditer(content):
        name = match.group(1)

        functions.append(
            {
                "name": name,
                "args": [],
                "returns": "",
                "docstring": "Shell function detected from deployment script.",
            }
        )

    module_docstring = "Shell deployment automation script."

    return {
        "file": str(file_path),
        "type": "shell",
        "exists": True,
        "module_docstring": module_docstring,
        "functions": functions,
    }


def inspect_source_file(changed_file: str) -> dict:
    source_file = SOURCE_DIR / changed_file

    if changed_file.endswith(".py"):
        return inspect_python_file(source_file)

    if changed_file.endswith(".sh"):
        return inspect_shell_file(source_file)

    return {
        "file": str(source_file),
        "type": "unknown",
        "exists": source_file.exists(),
        "module_docstring": "Unsupported file type for deep parsing.",
        "functions": [],
    }


def inspect_changed_files(changed_files: list[str]) -> list[dict]:
    summaries = []

    for changed_file in changed_files:
        summaries.append(
            inspect_source_file(
                changed_file
            )
        )

    return summaries


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- To Be Determined (TBD)"

    return "\n".join(
        [
            f"- {item}"
            for item in items
        ]
    )


def function_names(summaries: list[dict]) -> list[str]:
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


def component_descriptions(summaries: list[dict]) -> list[str]:
    output = []

    for summary in summaries:
        file_name = (
            summary.get("file", "")
            .replace("source/", "")
        )

        module_docstring = summary.get(
            "module_docstring",
            ""
        )

        file_type = summary.get(
            "type",
            "unknown"
        )

        output.append(
            f"**{file_name}** ({file_type}): {module_docstring or 'Source component detected.'}"
        )

    return output


def function_detail_blocks(summaries: list[dict]) -> str:
    lines = []

    for summary in summaries:
        file_name = (
            summary.get("file", "")
            .replace("source/", "")
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
                "No functions detected in this source file."
            )
            lines.append("")
            continue

        for function in functions:
            args = ", ".join(
                function.get(
                    "args",
                    []
                )
            ) or "None"

            returns = function.get(
                "returns",
                ""
            ) or "Not specified"

            docstring = function.get(
                "docstring",
                ""
            ) or "No function-level documentation available."

            lines.append(
                f"#### Function: `{function['name']}`"
            )
            lines.append("")
            lines.append(f"**Description:** {docstring}")
            lines.append("")
            lines.append(f"**Parameters:** {args}")
            lines.append("")
            lines.append(f"**Returns:** {returns}")
            lines.append("")

    return "\n".join(lines)


def infer_overview(
    service_name: str,
    summaries: list[dict]
) -> str:
    combined = []

    for summary in summaries:
        combined.append(
            summary.get(
                "module_docstring",
                ""
            )
       
