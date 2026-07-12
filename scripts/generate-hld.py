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


def inspect_python_file(file_path: Path) -> dict:

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

        summaries.append(
            inspect_python_file(
                source_file
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

    output = []

    for summary in summaries:

        for function in summary.get(
            "functions",
            []
        ):

            output.append(
                f"`{function['name']}()`"
            )

    return output


def component_descriptions(summaries: list[dict]) -> list[str]:

    output = []

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

        module_docstring = summary.get(
            "module_docstring",
            ""
        )

        if module_docstring:
            output.append(
                f"**{file_name}**: {module_docstring}"
            )
        else:
            output.append(
                f"**{file_name}**: Source module detected."
            )

    return output


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
        )

        for function in summary.get(
            "functions",
            []
        ):

            combined.append(
                function.get(
                    "name",
                    ""
                )
            )

            combined.append(
                function.get(
                    "docstring",
                    ""
                )
            )

    text = " ".join(combined).lower()

    if "network" in text or "vpn" in text or "load_balancer" in text or "dns" in text:
        return (
            "The greenfield network capability provides automated deployment "
            "of cloud networking services including zero-trust network provisioning, "
            "network segmentation validation, load balancer deployment, DNS integration, "
            "VPN gateway deployment, and storage gateway connectivity."
        )

    if "security" in text or "key" in text or "kms" in text or "vault" in text:
        return (
            "The security compliance capability provides automated security enforcement, "
            "key management, and compliance integration for cloud infrastructure services."
        )

    return (
        f"The {service_name} capability provides automated infrastructure services "
        "detected from source repository changes."
    )


def build_hld(
    service_info: dict,
    request: dict,
    summaries: list[dict]
) -> str:

    service_name = service_info["service"]
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

    changed_files = service_info.get(
        "changed_files",
        []
    ) or request.get(
        "changed_files",
        []
    )

    functions = function_names(
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
        "## 1. Introduction",
        "",
        "### 1.1. Overview",
        overview,
        "",
        f"This document was generated from source repository `{source_repo}` and pull request `{source_pr_number}`.",
        "",
        f"**Source PR Title**: {source_pr_title}",
        "",
        "### 1.2. Scope",
        "#### 1.2.1. In Scope",
        bullet_list(functions),
        "",
        "#### 1.2.2. Out of Scope",
        "- Manual deployment steps not represented in the source code.",
        "- Production approval and final architecture sign-off.",
        "- Runtime environment configuration not visible in the changed source files.",
        "",
        "### 1.3. Goals and Objectives",
        "- Keep architecture documentation synchronized with source code changes.",
        "- Reduce documentation drift between implementation and MkDocs content.",
        "- Provide reviewable HLD documentation through the Documentation-as-Code pipeline.",
        "- Establish source-to-document traceability.",
        "",
        "### 1.4. Acronyms and Abbreviations",
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
        bullet_list(functions),
        "",
        "### 2.2. Non-Functional Requirements (NFRs)",
        "- **Performance**: To Be Determined (TBD)",
        "- **Scalability**: To Be Determined (TBD)",
        "- **Availability/Reliability**: To Be Determined (TBD)",
        "- **Security**: Review required before publishing.",
        "- **Maintainability**: Generated documentation must remain Markdown-based and reviewable.",
        "- **Usability**: Documentation must be accessible from the MkDocs portal.",
        "",
        "---",
        "",
        "## 3. System Architecture",
        "",
        "### 3.1. Architectural Diagram",
        "```mermaid",
        "graph TD",
        "    Developer[Developer PR] --> SourceRepo[Source Repository]",
        "    SourceRepo --> Impact[Documentation Impact Workflow]",
        "    Impact --> Dispatch[Repository Dispatch]",
        "    Dispatch --> DocsRepo[doc-as-code Repository]",
        "    DocsRepo --> HLD[Generated HLD]",
        "    DocsRepo --> Review[Documentation Review]",
        "```",
        "",
        "### 3.2. System Components",
        bullet_list(components),
        "",
        "### 3.3. Technology Stack",
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
        "```mermaid",
        "graph LR",
        "    CodeChange[Code Change] --> ChangedFiles[Changed Files]",
        "    ChangedFiles --> Mapping[documentation-map.yaml]",
        "    Mapping --> Request[doc-request.json]",
        "    Request --> Generator[HLD and LLD Generator]",
        "    Generator --> Docs[Generated Markdown Documents]",
        "```",
        "",
        "### 4.2. Data Model/Storage",
        "Changed files used for this generation:",
        "",
        bullet_list(changed_files),
        "",
        "---",
        "",
        "## 5. Integration and APIs",
        "",
        "### 5.1. External System Integrations",
        "- Source code repository",
        "- Central Actions repository",
        "- Documentation template repository",
        "- MkDocs documentation repository",
        "",
        "### 5.2. API Strategy",
        "GitHub repository dispatch is used to trigger documentation generation in the documentation repository.",
        "",
        "---",
        "",
        "## 6. Security and Compliance",
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
        "Documentation is generated by GitHub Actions and committed to the MkDocs documentation repository.",
        "",
        "### 7.2. Monitoring and Logging",
        "- GitHub Actions logs provide workflow traceability.",
        "- Pull request history provides review traceability.",
        "- Generated files provide source-to-document linkage.",
        "",
        "---",
        "",
        "## 8. Risks and Assumptions",
        "- Generated documentation may require manual correction.",
        "- Business intent may not be fully represented by source code alone.",
        "- Documentation quality depends on source code comments and function names.",
        "- Human review remains mandatory before publication.",
        "",
        "---",
        "",
        "## 9. Open Questions",
        "- Should generated content update existing sections instead of replacing the full document?",
        "- Should AI-based generation be added after the deterministic pipeline is stable?",
        "- Should documentation updates require PR labels before generation?"
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

        changed_files = service.get(
            "changed_files",
            []
        ) or top_level_changed_files

        summaries = inspect_changed_files(
            changed_files
        )

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
                request,
                summaries
            ),
            encoding="utf-8"
        )

        print(
            f"HLD generated: {output_file}"
        )


if __name__ == "__main__":
    main()
