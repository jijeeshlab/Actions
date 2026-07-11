import json
from pathlib import Path


INPUT_FILE = Path("doc-request.json")
OUTPUT_FILE = Path("dispatch-payload.json")


def load_request():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "doc-request.json not found"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def build_dispatch_payload(
    request
):

    return {
2
"event_type": "documentation_update_requested",
3
"client_payload": {
4
"source_repo": request.get("source_repo"),
5
"source_repo_full": request.get("source_repo_full"),
6
"source_pr_number": request.get("source_pr_number"),
7
"source_pr_title": request.get("source_pr_title"),
8
"source_pr_url": request.get("source_pr_url"),
9
"changed_files": request.get("changed_files"),
10
"impacted_services": request.get("impacted_services")
11
}
12
}


def save_dispatch_payload(
    payload
):

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

    request = load_request()

    payload = build_dispatch_payload(
        request
    )

    save_dispatch_payload(
        payload
    )

    print("")
    print("=" * 50)
    print("DISPATCH PAYLOAD")
    print("=" * 50)

    print(
        json.dumps(
            payload,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
