import json
from pathlib import Path


DOC_REQUEST_FILE = Path("doc-request.json")
DIAGRAM_OUTPUT_DIR = Path("generated/diagrams")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def service_to_title(service_name: str) -> str:
    return service_name.replace("-", " ").replace("_", " ").title()


def generate_hld_diagram(service_name: str) -> str:
    title = service_to_title(service_name)

    return f"""# {title} - HLD Architecture Diagram

```mermaid
graph TD
    Developer[Developer Pull Request] --> SourceRepo[Source Repository]
    SourceRepo --> ImpactWorkflow[Documentation Impact Workflow]
    ImpactWorkflow --> DocMap[documentation-map.yaml]
    DocMap --> DocRequest[doc-request.json]
    DocRequest --> Dispatch[repository_dispatch]
    Dispatch --> DocRepo[doc-as-code Repository]
    DocRepo --> HLD[Generated HLD]
    DocRepo --> LLD[Generated LLD]
    HLD --> Review[Documentation Pull Request Review]
    LLD --> Review
    Review --> Publish[MkDocs Publication]
