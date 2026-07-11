import json
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
MKDOCS_FILE = Path("mkdocs.yml")


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


def normalize_title(path_value: str) -> str:

    file_name = Path(path_value).stem

    return (
        file_name
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def mkdocs_contains_entry(
    mkdocs_content: str,
    doc_path: str
) -> bool:

    normalized = (
        doc_path
        .replace("\\", "/")
        .replace("docs/", "", 1)
    )

    return normalized in mkdocs_content


def build_nav_entries(
    impacted_services: list
) -> list[tuple]:

    entries = []

    for service in impacted_services:

        documents = service.get(
            "documents",
            []
        )

        if (
            "HLD" in documents
            and service.get("hld")
        ):

            entries.append(
                (
                    normalize_title(
                        service["hld"]
                    ),
                    service["hld"]
                )
            )

        if (
            "LLD" in documents
            and service.get("lld")
        ):

            entries.append(
                (
                    normalize_title(
                        service["lld"]
                    ),
                    service["lld"]
                )
            )

    return entries


def insert_navigation_entries(
    mkdocs_content: str,
    entries: list
) -> str:

    lines = mkdocs_content.splitlines()

    lines.append("")
    lines.append("  - AI Generated Documentation:")

    for title, path_value in entries:

        relative_path = (
            path_value
            .replace("docs/", "", 1)
        )

        lines.append(
            f"      - {title}: {relative_path}"
        )

    return "\n".join(lines) + "\n"


def main():

    request = read_json(
        DOC_REQUEST_FILE
    )

    impacted_services = request.get(
        "impacted_services",
        []
    )

    if not impacted_services:

        print(
            "No impacted services found."
        )
        return

    if not MKDOCS_FILE.exists():

        print(
            "mkdocs.yml not found."
        )
        return

    mkdocs_content = MKDOCS_FILE.read_text(
        encoding="utf-8"
    )

    requested_entries = build_nav_entries(
        impacted_services
    )

    new_entries = []

    for title, path_value in requested_entries:

        if not mkdocs_contains_entry(
            mkdocs_content,
            path_value
        ):

            new_entries.append(
                (
                    title,
                    path_value
                )
            )

    if not new_entries:

        print(
            "No new navigation entries required."
        )
        return

    updated_mkdocs = insert_navigation_entries(
        mkdocs_content,
        new_entries
    )

    MKDOCS_FILE.write_text(
        updated_mkdocs,
        encoding="utf-8"
    )

    print("")
    print("=" * 60)
    print("MKDOCS NAVIGATION UPDATED")
    print("=" * 60)

    for title, path_value in new_entries:

        print(
            f"Added: {title}"
        )
        print(
            f"Path : {path_value}"
        )
        print("")


if __name__ == "__main__":
    main()
