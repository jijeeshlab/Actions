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
        "event_type":
            "documentation_update_requested",

        "client_payload":
            request
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
