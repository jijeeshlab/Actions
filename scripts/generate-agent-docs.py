import ast
import json
import re
from datetime import date
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
SOURCE_DIR = Path("source")
AGENTS_DIR = Path("_actions/agents")


AGENT_FILES = {
    "impact_agent": AGENTS_DIR / "impact-agent.md",
    "hld_agent": AGENTS_DIR / "hld-agent.md",
    "lld_agent": AGENTS_DIR / "lld-agent.md",
    "diagram_agent": AGENTS_DIR / "diagram-agent.md",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text_file(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def load_agents() -> dict:
    agents = {}

    for agent_key, agent_path in AGENT_FILES.items():
        agents[agent_key] = read_text_file(agent_path)

    return agents


def agent_loaded(agents: dict, agent_key: str) -> str:
    if agents.get(agent_key):
        return "Yes"

    return "No"


def agent_summary(agents: dict, agent_key: str) -> str:
    content = agents.get(agent_key, "")

    if not content:
        return "Agent file was not loaded."

    lines = []

    for line in content.splitlines():
        clean_line = line.strip()

        if clean_line:
            lines.append(clean_line)

    if not lines:
        return "Agent file was loaded but it is empty."

    return " ".join(lines[:6])


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
            function_args = []

            for arg in node.args.args:
                function_args.append(arg.arg)

            return_type = ""

            if node.returns:
                return_type = ast.unparse(node.returns)

            functions.append(
                {
                    "name": node.name,
                    "args": function_args,
                    "returns": return_type,
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
        re.MULTILINE,
    )

    for match in pattern.finditer(content):
        functions.append(
            {
                "name": match.group(1),
                "args": [],
                "returns": "",
                "docstring": "Shell deployment function detected.",
            }
        )

    return {
        "file": str(file_path),
        "type": "shell",
        "exists": True,
        "module_docstring": "Shell deployment automation script.",
        "functions": functions,
    }


def inspect_generic_file(file_path: Path) -> dict:
    return {
        "file": str(file_path),
        "type": "generic",
        "exists": file_path.exists(),
        "module_docstring": "Generic source file detected.",
        "functions": [],
    }


def inspect_source_file(changed_file: str) -> dict:
    source_file = SOURCE_DIR / changed_file

    if changed_file.endswith(".py"):
        return inspect_python_file(source_file)

    if changed_file.endswith(".sh"):
        return inspect_shell_file(source_file)

    return inspect_generic_file(source_file)


def inspect_changed_files(changed_files: list[str]) -> list[dict]:
    summaries = []

    for changed_file in changed_files:
        summaries.append(
            inspect_source_file(changed_file)
        )

    return summaries


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- To Be Determined (TBD)"

    lines = []

    for item in items:
        lines.append(f"- {item}")

    return "\n".join(lines)


def function_names(summaries: list[dict]) -> list[str]:
    names = []

    for summary in summaries:
        for function in summary.get("functions", []):
            names.append(
                f"`{function['name']}()`"
            )

    return names


def component_descriptions(summaries: list[dict]) -> list[str]:
    components = []

    for summary in summaries:
        file_name = summary.get("file", "")
        file_name = file_name.replace("source/", "")

        file_type = summary.get("type", "unknown")

        module_docstring = summary.get(
            "module_docstring",
            ""
        )

        if module_docstring:
            components.append(
                f"**{file_name}** ({file_type}): {module_docstring}"
            )
        else:
            components.append(
                f"**{file_name}** ({file_type}): Source component detected."
            )

    return components


def function_detail_blocks(summaries: list[dict]) -> str:
    lines = []

    for summary in summaries:
        file_name = summary.get("file", "")
        file_name = file_name.replace("source/", "")

        lines.append(f"### Source File: `{file_name}`")
        lines.append("")

        functions = summary.get("functions", [])

        if not functions:
            lines.append("No functions detected in this file.")
            lines.append("")
            continue

        for function in functions:
            args = ", ".join(
                function.get("args", [])
            )

            if not args:
                args = "None"

           
