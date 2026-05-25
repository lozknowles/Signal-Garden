from pathlib import Path
import json
import sys


VAULT_PATH = Path(r"C:\Loz")
PROJECT_PATH = Path(__file__).resolve().parent


CHECKS = []


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_check(ok, message):
    CHECKS.append((ok, message))


def validate_config():
    path = PROJECT_PATH / "areas.json"
    config = load_json(path, {})
    required = {
        "folders": list,
        "research_topics": list,
        "preferred_sources": list,
        "moc_categories": dict,
    }
    for key, expected_type in required.items():
        add_check(isinstance(config.get(key), expected_type), f"areas.json has {key}")
    add_check("Reading" in config.get("folders", []), "Reading folder is configured")
    add_check("Audio" in config.get("folders", []), "Audio folder is configured")


def validate_memory():
    memory = VAULT_PATH / "Memory"
    concept_state = load_json(memory / "concept_state.json", {})
    relationships = load_json(memory / "concept_relationships.json", {})
    queue = load_json(memory / "research_queue.json", [])

    add_check(isinstance(concept_state, dict), "concept_state.json is an object")
    add_check(isinstance(relationships, dict), "concept_relationships.json is an object")
    add_check(isinstance(queue, list), "research_queue.json is a list")

    for concept, record in list(concept_state.items())[:1000]:
        add_check(isinstance(record, dict), f"concept record is object: {concept}")
        add_check("last_seen" in record, f"concept has last_seen: {concept}")
        add_check("seen_count" in record, f"concept has seen_count: {concept}")

    for edge, record in list(relationships.items())[:1000]:
        add_check("|" in edge, f"relationship key contains pipe: {edge}")
        add_check(isinstance(record, dict), f"relationship record is object: {edge}")
        add_check("weight" in record, f"relationship has weight: {edge}")


def validate_sources():
    sources = VAULT_PATH / "Sources"
    if not sources.exists():
        add_check(False, "Sources folder exists")
        return
    source_files = list(sources.glob("*.md"))
    add_check(bool(source_files), "at least one source note exists")


def validate_open_notebook_artifacts():
    reports = VAULT_PATH / "Reports"
    bundles = list(reports.glob("Open Notebook Podcast Bundle - *.json")) if reports.exists() else []
    for bundle in bundles[-5:]:
        payload = load_json(bundle, {})
        add_check("sources" in payload, f"podcast bundle has sources: {bundle.name}")
        add_check("podcast_prompt" in payload, f"podcast bundle has prompt: {bundle.name}")


def main():
    validate_config()
    validate_memory()
    validate_sources()
    validate_open_notebook_artifacts()

    failed = [message for ok, message in CHECKS if not ok]

    for ok, message in CHECKS:
        prefix = "OK" if ok else "FAIL"
        print(f"{prefix}: {message}")

    print()
    print(f"Checks: {len(CHECKS)}")
    print(f"Failures: {len(failed)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
