import json


def load_json_file(path, default):
    """Load JSON state with a default for missing or unreadable files."""
    if not path.exists():
        return default

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return default


def save_json_file(path, payload):
    """Write formatted JSON state."""
    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            payload,
            f,
            indent=2
        )
