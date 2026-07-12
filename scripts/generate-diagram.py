import json
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
DIAGRAM_OUTPUT_DIR = Path("generated/diagrams")


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


def service_to_title(
    service_name: str
) -> str:

    return (
        service_name
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def generate_hld_diagram(
    service_name: str
) -> str:

    title = service_to_title(
        service_name
    )

    lines = [

        f"# {title} - HLD Architecture Diagram",
        "",
        "```mermaid",
        "graph TD",
        "",
        "Developer[Developer Pull Request] --> SourceRepo[Source Repository]",
        "SourceRepo --> ImpactWorkflow[Documentation Impact Workflow]",
        "ImpactWorkflow --> DocMap[documentation-map.yaml]",
        "DocMap --> DocRequest[doc-request.json]",
        "DocRequest --> Dispatch[repository_dispatch]",
        "Dispatch --> DocRepo[doc-as-code Repository]",
        "DocRepo --> HLD[Generated HLD]",
        "DocRepo --> LLD[Generated LLD]",
        "HLD --> Review[Documentation Review]",
        "LLD --> Review",
        "Review --> Publish[MkDocs Publication]",
        "",
        "```",
        "",
        "## Description",
        "",
        f"The diagram above represents the automated documentation generation flow for the service **{title}**.",
        "",
    ]

    return "\n".join(lines)


def write_diagram(
    service_name: str
):

    DIAGRAM_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        DIAGRAM_OUTPUT_DIR /
        f"{service_name}-diagram.md"
    )

    output_file.write_text(
        generate_hld_diagram(
            service_name
        ),
        encoding="utf-8"
    )

    print(
        f"Diagram generated: {output_file}"
    )


def main():

    request = read_json(
        DOC_REQUEST_FILE
    )

    impacted_services = request.get(
        "impacted_services",
        []
    )

    for service in impacted_services:

        service_name = (
            service.get(
                "service",
                "unknown-service"
            )
        )

        write_diagram(
            service_name
        )


if __name__ == "__main__":
    main()
