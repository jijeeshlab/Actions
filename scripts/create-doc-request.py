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


def build_dispatch_payload(request):

    impacted_services = []

    for svc in request.get(
        "impacted_services",
        []
    ):

        impacted_services.append(
            {
                "service": svc.get(
                    "service"
                ),
                "hld": svc.get(
                    "hld"
                ),
                "lld": svc.get(
                    "lld"
                )
            }
        )

    return {
        "event_type":
            "documentation_update_requested",

        "client_payload": {

            "source_repo":
                request.get(
                    "source_repo"
                ),

            "source_repo_full":
                request.get(
                    "source_repo_full"
                ),

            "source_pr_number":
                request.get(
                    "source_pr_number"
                ),

            "source_pr_title":
                request.get(
                    "source_pr_title"
                ),

            "impacted_services":
                impacted_services
        }
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
    print("=" * 60)
    print("DISPATCH PAYLOAD")
    print("=" * 60)

    print(
        json.dumps(
            payload,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
