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


def load_agents() -> dict:
    agents = {}

    for agent_key, agent_path in AGENT_FILES.items():
        agents[agent_key] = read_text_file(
            agent_path
        )

    return agents


def agent_loaded(
    agents: dict,
    agent_key: str
) -> str:
    if agents.get(agent_key):
        return "Yes"

    return "No"


def agent_summary(
    agents: dict,
    agent_key: str
) -> str:
    content = agents.get(
        agent_key,
        ""
    )

    if not content:
        return "Agent file was not loaded."

    lines = []

    for line in content.splitlines():
        clean_line = line.strip()

        if clean_line:
            lines.append(clean_line)

    if not lines:
        return "Agent file was loaded but it is empty."

    return " ".join(
        lines[:8]
    )


def extract_python_functions_with_regex(
    content: str
) -> list[dict]:
    functions = []

    pattern = re.compile(
        r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)",
        re.MULTILINE | re.D*TALL
    )

    for match in patte*n.finditer(content):
        name * match.group(1)
        raw_args =*match.group(2)

        args = []
*        for raw_arg in raw_args.sp*it(","):
            clean_arg = r*w_arg.strip()

            if not *lean_arg:
                continue*
            if ":" in clean_arg:
*               clean_arg = clean_a*g.split(":")[0].strip()

         *  if "=" in clean_arg:
           *    clean_arg = clean_arg.split("=*)[0].strip()

            if clean*arg and clean_arg not in ["self", "cls"]:
                args.append*clean_arg)

        functions.appe*d(
            {
                "*ame": name,
                "args"* args,
                "returns": *Not detected",
                "do*string": "Function detected by fal*back parser.",
            }
     *  )

    return functions


def in*pect_python_file(
    file_path: P*th
) -> dict:
    if not file_path*exists():
        print(
         *  f"WARNING: Python file not found* {file_path}"
        )

        r*turn {
            "file": str(fil*_path),
            "type": "pytho*",
            "exists": False,
  *         "module_docstring": "",
 *          "functions": [],
       *    "parse_status": "file_not_foun*",
        }

    content = file_p*th.read_text(
        encoding="ut*-8",
        errors="ignore"
    )*
    try:
        tree = ast.parse*content)

        functions = []

*       for node in ast.walk(tree):*            if isinstance(node, as*.FunctionDef):
                fun*tion_args = []

                fo* arg in node.args.args:
          *         function_args.append(arg.*rg)

                return_type =*""

                if node.return*:
                    return_type * ast.unparse(node.returns)

      *         functions.append(
       *            {
                    *   "name": node.name,
            *           "args": function_args,
*                       "returns": *eturn_type,
                      * "docstring": ast.get_docstring(no*e) or "",
                    }
  *             )

        print(
   *        f"Python AST parse success* {file_path}"
        )

        p*int(
            f"Functions detec*ed by AST: {len(functions)}"
     *  )

        return {
            *file": str(file_path),
           *"type": "python",
            "exi*ts": True,
            "module_doc*tring": ast.get_docstring(tree) or*"",
            "functions": funct*ons,
            "parse_status": "*st_success",
        }

    except*SyntaxError as error:
        prin*("")
        print("==============*===================")
        prin*("PYTHON AST PARSE FAILED")
      * print("==========================*=======")
        print(f"File: {f*le_path}")
        print(f"Error: *error}")
        print("Fallback p*rser will be used.")
        print*"=================================*")
        print("")

        fall*ack_functions = extract_python_fun*tions_with_regex(
            cont*nt
        )

        print(
     *      f"Functions detected by fall*ack parser: {len(fallback_function*)}"
        )

        return {
  *         "file": str(file_path),
 *          "type": "python",
      *     "exists": True,
            "*odule_docstring": (
              * "Python file detected, but AST pa*sing failed. "
                "Fa*lback function detection was used.*
            ),
            "funct*ons": fallback_functions,
        *   "parse_status": "ast_failed_reg*x_fallback",
        }


def inspe*t_shell_file(
    file_path: Path
* -> dict:
    if not file_path.exists():
        print(
            f"WARNING: Shell file not found: {file_path}"
        )

        return {
            "file": str(file_path),
            "type": "shell",
            "exists": False,
            "module_docstring": "",
            "functions": [],
            "parse_status": "file_not_found",
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
        functions.append(
            {
                "name": match.group(1),
                "args": [],
                "returns": "",
                "docstring": "Shell deployment function detected.",
            }
        )

    print(
        f"Shell functions detected: {len(functions)} from {file_path}"
    )

    return {
        "file": str(file_path),
        "type": "shell",
        "exists": True,
        "module_docstring": "Shell deployment automation script.",
        "functions": functions,
        "parse_status": "shell_success",
    }


def inspect_generic_file(
    file_path: Path
) -> dict:
    return {
        "file": str(file_path),
        "type": "generic",
        "exists": file_path.exists(),
        "module_docstring": "Generic source file detected.",
        "functions": [],
        "parse_status": "generic",
    }


def inspect_source_file(
    changed_file: str
) -> dict:
    source_file = SOURCE_DIR / changed_file

    print("")
    print("==================================")
    print("INSPECTING CHANGED FILE")
    print("==================================")
    print(f"Changed file: {changed_file}")
    print(f"Resolved path: {source_file}")
    print(f"Exists: {source_file.exists()}")
    print("==================================")
    print("")

    if changed_file.endswith(".py"):
        return inspect_python_file(
            source_file
        )

    if changed_file.endswith(".sh"):
        return inspect_shell_file(
            source_file
        )

    return inspect_generic_file(
        source_file
    )


def inspect_changed_files(
    changed_files: list[str]
) -> list[dict]:
    summaries = []

    print("")
    print("==================================")
    print("CHANGED FILES RECEIVED")
    print("==================================")

    if not changed_files:
        print("No changed files received.")

    for changed_file in changed_files:
        print(f"- {changed_file}")

        summaries.append(
            inspect_source_file(
                changed_file
            )
        )

    print("==================================")
    print("")

    return summaries


def bullet_list(
    items: list[str]
) -> str:
    if not items:
        return "- To Be Determined (TBD)"

    lines = []

    for item in items:
        lines.append(
            f"- {item}"
        )

    return "\n".join(lines)


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


def component_descriptions(
    summaries: list[dict]
) -> list[str]:
    components = []

    for summary in summaries:
        file_name = summary.get(
            "file",
            ""
        ).replace(
            "source/",
            ""
        )

        file_type = summary.get(
            "type",
            "unknown"
        )

        parse_status = summary.get(
            "parse_status",
            "unknown"
        )

        module_docstring = summary.get(
            "module_docstring",
            ""
        )

        if module_docstring:
            components.append(
                f"**{file_name}** ({file_type}, {parse_status}): {module_docstring}"
            )
        else:
            components.append(
                f"**{file_name}** ({file_type}, {parse_status}): Source component detected."
            )

    return components


def function_detail_blocks(
    summaries: list[dict]
) -> str:
    lines = []

    for summary in summaries:
        file_name = summary.get(
            "file",
            ""
        ).replace(
            "source/",
            ""
        )

        parse_status = summary.get(
            "parse_status",
            "unknown"
        )

        lines.append(
            f"### Source File: `{file_name}`"
        )
        lines.append("")
        lines.append(
            f"**Parse Status:** `{parse_status}`"
        )
        lines.append("")

        functions = summary.get(
            "functions",
            []
        )

        if not functions:
            lines.append(
                "No functions detected in this file."
            )
            lines.append("")
            continue

        for function in functions:
            args = ", ".join(
                function.get(
                    "args",
                    []
                )
            )

            if not args:
                args = "None"

            returns = function.get(
                "returns",
                ""
            )

            if not returns:
                returns = "Not specified"

            docstring = function.get(
                "docstring",
                ""
            )

            if not docstring:
                docstring = "No function-level documentation available."

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


def infer_overview(
    service_name: str,
    summaries: list[dict]
) -> str:
    collected_text = []

    for summary in summaries:
        collected_text.append(
            summary.get(
                "module_docstring",
                ""
            )
        )

        for function in summary.get(
            "functions",
            []
        ):
            collected_text.append(
                function.get(
                    "name",
                    ""
                )
            )

            collected_text.append(
                function.get(
                    "docstring",
                    ""
                )
            )

    combined_text = " ".join(
        collected_text
    ).lower()

    if (
        "banking" in combined_text
        or "payment" in combined_text
        or "fraud" in combined_text
        or "loan" in combined_text
        or "credit" in combined_text
    ):
        return (
            "The platform provides banking, payment, fraud detection, credit, "
            "and financial service deployment capabilities."
        )

    if (
        "healthcare" in combined_text
        or "patient" in combined_text
        or "medical" in combined_text
        or "clinical" in combined_text
    ):
        return (
            "The platform provides healthcare, patient management, medical record, "
            "and clinical analytics deployment capabilities."
        )

    if (
        "retail" in combined_text
        or "ecommerce" in combined_text
        or "inventory" in combined_text
        or "order" in combined_text
    ):
        return (
            "The platform provides retail, ecommerce, inventory, and order "
            "management deployment capabilities."
        )

    if (
        "logistics" in combined_text
        or "shipment" in combined_text
        or "warehouse" in combined_text
        or "route" in combined_text
    ):
        return (
            "The platform provides logistics, shipment tracking, route optimization, "
            "and warehouse management deployment capabilities."
        )

    if (
        "network" in combined_text
        or "vpn" in combined_text
        or "dns" in combined_text
        or "load" in combined_text
        or "gateway" in combined_text
    ):
        return (
            "The greenfield network capability provides automated cloud "
            "network deployment, connectivity, DNS, gateway, and traffic "
            "management services."
        )

    if (
        "kubernetes" in combined_text
        or "ingress" in combined_text
        or "mesh" in combined_text
    ):
        return (
            "The platform provides container platform automation including "
            "Kubernetes cluster, ingress, and service mesh deployment."
        )

    if (
        "backup" in combined_text
        or "replication" in combined_text
        or "recovery" in combined_text
    ):
        return (
            "The platform provides backup, replication, and disaster recovery "
            "automation for resilient infrastructure operations."
        )

    if (
        "secret" in combined_text
        or "vault" in combined_text
        or "security" in combined_text
    ):
        return (
            "The platform provides security and secrets management capabilities "
            "for controlled infrastructure deployment."
        )

    if (
        "observability" in combined_text
        or "monitoring" in combined_text
        or "logging" in combined_text
    ):
        return (
            "The platform provides observability, monitoring, and logging "
            "capabilities for operational visibility."
        )

    return (
        f"The {service_name} capability provides automated infrastructure "
        "services detected from source repository changes."
    )


def build_hld(
    service_info: dict,
    request: dict,
    summaries: list[dict],
    agents: dict
) -> str:
    service_name = service_info.get(
        "service",
        "unknown-service"
    )

    today = date.today().isoformat()

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

    components = component_descriptions(
        summaries
    )

    overview = infer_overview(
        service_name,
        summaries
    )

    lines = [
        f"# High-Level Design (HLD): {service_name}",
        "",
        "**Author**: Jijeesh Valappil",
        f"**Date**: {today}",
        "**Version**: 1.0",
        "",
        "---",
        "",
        "## Agent Context",
        "",
        "| Agent File | Loaded |",
        "|------------|--------|",
        f"| impact-agent.md | {agent_loaded(agents, 'impact_agent')} |",
        f"| hld-agent.md | {agent_loaded(agents, 'hld_agent')} |",
        f"| diagram-agent.md | {agent_loaded(agents, 'diagram_agent')} |",
        "",
        "### HLD Agent Summary",
        "",
        agent_summary(
            agents,
            "hld_agent"
        ),
        "",
        "---",
        "",
        "## 1. Introduction",
        "",
        "### 1.1. Overview",
        "",
        overview,
        "",
        f"This document was generated from source repository `{source_repo}` and pull request `{source_pr_number}`.",
        "",
        f"**Source PR Title**: {source_pr_title}",
        "",
        "### 1.2. Scope",
        "",
        "#### 1.2.1. In Scope",
        "",
        bullet_list(
            funcs
        ),
        "",
        "#### 1.2.2. Out of Scope",
        "",
        "- Manual approval and final architecture sign-off.",
        "- Runtime configuration not visible in the changed source files.",
        "- Business requirements not represented by the source code.",
        "",
        "### 1.3. Goals and Objectives",
        "",
        "- Keep architecture documentation synchronized with source code changes.",
        "- Reduce documentation drift.",
        "- Provide reviewable HLD documentation through the Documentation-as-Code pipeline.",
        "- Establish source-to-document traceability.",
        "",
        "### 1.4. Acronyms and Abbreviations",
        "",
        "| Term | Definition |",
        "|------|------------|",
        "| HLD | High-Level Design |",
        "| LLD | Low-Level Design |",
        "| PR | Pull Request |",
        "| CI/CD | Continuous Integration and Continuous Deployment |",
        "| Docs-as-Code | Documentation managed through Git, Markdown, pull requests, and automation |",
        "",
        "---",
        "",
        "## 2. Requirements",
        "",
        "### 2.1. Functional Requirements",
        "",
        bullet_list(
            funcs
        ),
        "",
        "### 2.2. Non-Functional Requirements (NFRs)",
        "",
        "- **Performance**: To Be Determined (TBD)",
        "- **Scalability**: To Be Determined (TBD)",
        "- **Availability/Reliability**: To Be Determined (TBD)",
        "- **Security**: Generated documentation requires review before publication.",
        "- **Maintainability**: Documentation must remain Markdown-based and reviewable.",
        "- **Usability**: Documentation must be accessible through the MkDocs portal.",
        "",
        "---",
        "",
        "## 3. System Architecture",
        "",
        "### 3.1. Architectural Diagram",
        "",
        "```mermaid",
        "graph TD",
        "    Developer[Developer PR] --> SourceRepo[Source Repository]",
        "    SourceRepo --> Impact[Documentation Impact Workflow]",
        "    Impact --> Dispatch[Repository Dispatch]",
        "    Dispatch --> DocsRepo[doc-as-code Repository]",
        "    DocsRepo --> AgentDocs[Agent-Aware Documentation Generator]",
        "    AgentDocs --> HLD[Generated HLD]",
        "    AgentDocs --> LLD[Generated LLD]",
        "    HLD --> Review[Documentation Review]",
        "    LLD --> Review",
        "```",
        "",
        "### 3.2. System Components",
        "",
        bullet_list(
            components
        ),
        "",
        "### 3.3. Technology Stack",
        "",
        "- GitHub",
        "- GitHub Actions",
        "- Python",
        "- Markdown",
        "- MkDocs",
        "- Mermaid",
        "",
        "---",
        "",
        "## 4. Data Flow and Storage",
        "",
        "### 4.1. Data Flow Diagram",
        "",
        "```mermaid",
        "graph LR",
        "    CodeChange[Code Change] --> ChangedFiles[Changed Files]",
        "    ChangedFiles --> Mapping[documentation-map.yaml]",
        "    Mapping --> Request[doc-request.json]",
        "    Request --> Agents[Agent Markdown Files]",
        "    Agents --> Generator[generate-agent-docs.py]",
        "    Generator --> Docs[Generated Markdown Documents]",
        "```",
        "",
        "### 4.2. Data Model/Storage",
        "",
        "Changed files used for this generation:",
        "",
        bullet_list(
            changed_files
        ),
        "",
        "---",
        "",
        "## 5. Integration and APIs",
        "",
        "### 5.1. External System Integrations",
        "",
        "- Source code repository",
        "- Central Actions repository",
        "- Documentation template repository",
        "- MkDocs documentation repository",
        "",
        "### 5.2. API Strategy",
        "",
        "GitHub repository dispatch is used to trigger documentation generation in the documentation repository.",
        "",
        "---",
        "",
        "## 6. Security and Compliance",
        "",
        "- Repository tokens must be stored in GitHub Secrets.",
        "- Generated documentation must be reviewed before merge.",
        "- Secrets, keys, credentials, and customer-sensitive identifiers must not be copied into documentation.",
        "- Automation must follow least privilege access principles.",
        "",
        "---",
        "",
        "## 7. Deployment and Operations",
        "",
        "### 7.1. Deployment Strategy",
        "",
        "Documentation is generated by GitHub Actions and committed to the MkDocs documentation repository.",
        "",
        "### 7.2. Monitoring and Logging",
        "",
        "- GitHub Actions logs provide workflow traceability.",
        "- Pull request history provides review traceability.",
        "- Generated files provide source-to-document linkage.",
        "",
        "---",
        "",
        "## 8. Risks and Assumptions",
        "",
        "- Generated documentation may require manual correction.",
        "- Business intent may not be fully represented by source code alone.",
        "- Documentation quality depends on source code comments and function names.",
        "- Human review remains mandatory before publication.",
        "",
        "---",
        "",
        "## 9. Open Questions",
        "",
        "- Should generated content update existing sections instead of replacing the full document?",
        "- Should real LLM-based generation be added after deterministic generation is stable?",
        "- Should documentation updates require PR labels before generation?",
    ]

    return "\n".join(lines) + "\n"


def build_lld(
    service_info: dict,
    request: dict,
    summaries: list[dict],
    agents: dict
) -> str:
    service_name = service_info.get(
        "service",
        "unknown-service"
    )

    today = date.today().isoformat()

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
        f"**Related HLD**: {service_info.get('hld', 'To Be Linked')}",
        "",
        "---",
        "",
        "## Agent Context",
        "",
        "| Agent File | Loaded |",
        "|------------|--------|",
        f"| lld-agent.md | {agent_loaded(agents, 'lld_agent')} |",
        f"| diagram-agent.md | {agent_loaded(agents, 'diagram_agent')} |",
        "",
        "### LLD Agent Summary",
        "",
        agent_summary(
            agents,
            "lld_agent"
        ),
        "",
        "---",
        "",
        "## 1. Introduction",
        "",
        "### 1.1. Overview",
        "",
        f"This document provides the low-level design for `{service_name}` based on source code changes.",
        "",
        f"**Source Repository**: `{source_repo}`",
        f"**Source PR**: `{source_pr_number}`",
        f"**Source PR Title**: {source_pr_title}",
        "",
        "---",
        "",
        "## 2. Detailed Design",
        "",
        "### 2.1. Class Diagram",
        "",
        "```mermaid",
        "classDiagram",
        "    class SourceRepository {",
        "        +changed_files()",
        "    }",
        "    class AgentAwareDocumentationGenerator {",
        "        +load_agents()",
        "        +inspect_source_code()",
        "        +generate_hld()",
        "        +generate_lld()",
        "    }",
        "    SourceRepository --> AgentAwareDocumentationGenerator",
        "```",
        "",
        "### 2.2. Sequence Diagram(s)",
        "",
        "```mermaid",
        "sequenceDiagram",
        "    participant Developer",
        "    participant SourceRepo",
        "    participant ActionsRepo",
        "    participant DocsRepo",
        "    Developer->>SourceRepo: Create or update PR",
        "    SourceRepo->>ActionsRepo: Trigger documentation impact workflow",
        "    ActionsRepo->>DocsRepo: Send repository_dispatch event",
        "    DocsRepo->>DocsRepo: Load agent files and generate HLD/LLD",
        "```",
        "",
        "### 2.3. Component Breakdown",
        "",
        function_detail_blocks(
            summaries
        ),
        "",
        "---",
        "",
        "## 3. Database Design",
        "",
        "### 3.1. Database Schema",
        "",
        "No database schema was detected in the changed source files.",
        "",
        "| Table Name | Column Name | Data Type | Constraints | Description |",
        "|------------|-------------|-----------|-------------|-------------|",
        "| Not applicable | Not applicable | Not applicable | Not applicable | No database layer detected |",
        "",
        "### 3.2. Data Access Layer (DAL)",
        "",
        "No dedicated data access layer was identified from the changed source files.",
        "",
        "---",
        "",
        "## 4. API Endpoint Specification",
        "",
        "No API endpoint was detected in the changed source files.",
        "",
        "---",
        "",
        "## 5. Error Handling",
        "",
        "- Validate input parameters before processing.",
        "- Log operational events without exposing sensitive data.",
        "- Return predictable status values.",
        "- Avoid silent failures.",
        "",
        "---",
        "",
        "## 6. Security Considerations",
        "",
        "- Validate all inputs.",
        "- Do not log secrets, tokens, keys, passwords, or customer-sensitive identifiers.",
        "- Use GitHub Secrets for automation credentials.",
        "- Review generated documentation before publishing.",
        "",
        "---",
        "",
        "## 7. Unit Test Cases",
        "",
        bullet_list(
            funcs
        ),
        "",
        "---",
        "",
        "## 8. Open Questions",
        "",
        "- Should AI generation update only impacted sections instead of regenerating full documents?",
        "- Should class and sequence diagrams be generated from code structure or architecture metadata?",
        "- Should PR labels control whether documentation generation runs?",
        "",
        "---",
        "",
        "## Changed Files",
        "",
        bullet_list(
            changed_files
        ),
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    request = read_json(
        DOC_REQUEST_FILE
    )

    agents = load_agents()

    services = request.get(
        "impacted_services",
        []
    )

    top_level_changed_files = request.get(
        "changed_files",
        []
    )

    print("")
    print("==================================")
    print("GENERATOR REQUEST SUMMARY")
    print("==================================")
    print(f"Impacted services: {len(services)}")
    print(f"Top-level changed files: {top_level_changed_files}")
    print("==================================")
    print("")

    if not services:
        print(
            "No impacted services found. Nothing to generate."
        )
        return

    for service in services:
        changed_files = (
            service.get(
                "changed_files",
                []
            )
            or top_level_changed_files
        )

        print("")
        print("==================================")
        print("SERVICE GENERATION CONTEXT")
        print("==================================")
        print(f"Service: {service.get('service')}")
        print(f"HLD: {service.get('hld')}")
        print(f"LLD: {service.get('lld')}")
        print(f"Changed files: {changed_files}")
        print("==================================")
        print("")

        summaries = inspect_changed_files(
            changed_files
        )

        hld_path = service.get(
            "hld"
        )

        lld_path = service.get(
            "lld"
        )

        if hld_path:
            hld_output = Path(
                hld_path
            )

            hld_output.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            hld_output.write_text(
                build_hld(
                    service,
                    request,
                    summaries,
                    agents
                ),
                encoding="utf-8"
            )

            print(
                f"HLD generated: {hld_output}"
            )

        if lld_path:
            lld_output = Path(
                lld_path
            )

            lld_output.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            lld_output.write_text(
                build_lld(
                    service,
                    request,
                    summaries,
                    agents
                ),
                encoding="utf-8"
            )

            print(
                f"LLD generated: {lld_output}"
            )


if __name__ == "__main__":
    main()
