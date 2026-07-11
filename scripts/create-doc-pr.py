import json
import os
import subprocess
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run(command: list[str]) -> None:
    print(f"Running: {' '.join(command)}")

    subprocess.run(
        command,
        check=True
    )


def has_changes() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True
    )

    return bool(result.stdout.strip())


def sanitize(value: str) -> str:
    if not value:
        return "unknown"

    value = value.lower()
    value = value.replace("/", "-")
    value = value.replace("_", "-")
    value = value.replace(" ", "-")

    clean = []

    for char in value:
        if char.isalnum() or char == "-":
            clean.append(char)

    return "".join(clean).strip("-")


def build_branch_name(request: dict) -> str:

    source_repo = sanitize(
        request.get(
            "source_repo",
            "repo"
        )
    )

    pr_number = sanitize(
        str(
            request.get(
                "source_pr_number",
                "0"
            )
        )
    )

    return (
        f"ai-doc-update-"
        f"{source_repo}-"
        f"pr-{pr_number}"
    )


def build_pr_title(request: dict) -> str:

    source_repo = request.get(
        "source_repo",
        ""
    )

    source_pr_number = request.get(
        "source_pr_number",
        ""
    )

    return (
        f"AI Documentation Update "
        f"from {source_repo} "
        f"PR {source_pr_number}"
    )


def build_pr_body(request: dict) -> str:

    source_repo_full = request.get(
        "source_repo_full",
        ""
    )

    source_pr_title = request.get(
        "source_pr_title",
        ""
    )

    source_pr_url = request.get(
        "source_pr_url",
        ""
    )

    changed_files = request.get(
        "changed_files",
        []
    )

    impacted_services = request.get(
        "impacted_services",
        []
    )

    changed_files_md = "\n".join(
        [
            f"- `{f}`"
            for f in changed_files
        ]
    )

    services_md = []

    for svc in impacted_services:

        services_md.append(
            f"- **{svc.get('service')}**"
        )

        if svc.get("hld"):
            services_md.append(
                f"  - HLD: `{svc.get('hld')}`"
            )

        if svc.get("lld"):
            services_md.append(
                f"  - LLD: `{svc.get('lld')}`"
            )

    impacted_md = "\n".join(
        services_md
    )

    return f"""
## AI Generated Documentation Update

This pull request was generated automatically from a source code pull request.

### Source Repository

`{source_repo_full}`

### Source Pull Request

Title:

{source_pr_title}

URL:

{source_pr_url}

### Changed Files

{changed_files_md}

### Impacted Services

{impacted_md}

### Review Required

Please review:

- Generated HLD
- Generated LLD
- Mermaid diagrams
- MkDocs navigation updates

Before merging.
"""


def configure_git() -> None:

    run(
        [
            "git",
            "config",
            "user.name",
            "github-actions[bot]"
        ]
    )

    run(
        [
            "git",
            "config",
            "user.email",
            "github-actions[bot]@users.noreply.github.com"
        ]
    )


def create_pr(request: dict) -> None:

    if not has_changes():
        print(
            "No documentation changes detected."
        )
        return

    branch_name = build_branch_name(
        request
    )

    pr_title = build_pr_title(
        request
    )

    pr_body = build_pr_body(
        request
    )

    configure_git()

    run(
        [
            "git",
            "checkout",
            "-b",
            branch_name
        ]
    )

    run(
        [
            "git",
            "add",
            "."
        ]
    )

    run(
        [
            "git",
            "commit",
            "-m",
            pr_title
        ]
    )

    run(
        [
            "git",
            "push",
            "origin",
            branch_name
        ]
    )

    base_branch = os.getenv(
        "DOC_PR_BASE_BRANCH",
        "main"
    )

    run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            base_branch,
            "--head",
            branch_name
        ]
    )

    print("")
    print(
        "Documentation PR created successfully."
    )
    print(
        f"Branch: {branch_name}"
    )


def main() -> None:

    request = read_json(
        DOC_REQUEST_FILE
    )

    if not request.get(
        "impact_found",
        False
    ):

        print(
            "No documentation impact found."
        )

        return

    create_pr(request)


if __name__ == "__main__":
    main()
