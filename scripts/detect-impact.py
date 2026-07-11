import json
import os
from pathlib import Path

import yaml


DOCUMENTATION_MAP = Path(".github/documentation-map.yaml")
CHANGED_FILES = Path("changed-files.txt")
OUTPUT_FILE = Path("doc-request.json")


def load_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_changed_files(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def process_mapping(mapping, changed_files):

    impacted_services = []

    paths = mapping.get("paths", {})

    for changed_file in changed_files:

        if changed_file in paths:

            service_data = paths[changed_file]

            impacted_services.append(
                {
                    "service": service_data["service"],
                    "documents": service_data.get(
                        "docs",
                        ["HLD", "LLD"]
                    ),
                    "hld": service_data.get("hld"),
                    "lld": service_data.get("lld"),
                    "changed_file": changed_file,
                }
            )

    return impacted_services


def build_request(
    changed_files,
    impacted_services
):

    return {
        "source_repo": os.getenv(
            "SOURCE_REPO",
            ""
        ),
        "source_repo_full": os.getenv(
            "SOURCE_REPO_FULL",
            ""
        ),
        "source_pr_number": os.getenv(
            "SOURCE_PR_NUMBER",
            ""
        ),
        "source_pr_title": os.getenv(
            "SOURCE_PR_TITLE",
            ""
        ),
        "source_pr_url": os.getenv(
            "SOURCE_PR_URL",
            ""
        ),
        "source_head_sha": os.getenv(
            "SOURCE_HEAD_SHA",
            ""
        ),
        "source_head_ref": os.getenv(
            "SOURCE_HEAD_REF",
            ""
        ),
        "source_base_ref": os.getenv(
            "SOURCE_BASE_REF",
            ""
        ),
        "changed_files": changed_files,
        "impact_found": len(
            impacted_services
        ) > 0,
        "impacted_services": impacted_services,
    }


def save_request(payload):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            payload,
            f,
            indent=2
        )


def main():

    mapping = load_yaml(
        DOCUMENTATION_MAP
    )

    changed_files = load_changed_files(
        CHANGED_FILES
    )

    impacted_services = process_mapping(
        mapping,
        changed_files
    )

    result = build_request(
        changed_files,
        impacted_services
    )

    save_request(result)

    print("")
    print("=" * 50)
    print("DOCUMENTATION IMPACT REPORT")
    print("=" * 50)

    print(
        json.dumps(
            result,
            indent=2
        )
    )

    if not impacted_services:
        print("")
        print(
            "No documentation impact detected."
        )
    else:
        print("")
        print(
            "Documentation impact detected."
        )


if __name__ == "__main__":
    main()
