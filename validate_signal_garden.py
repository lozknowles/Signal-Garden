from pathlib import Path
from dotenv import load_dotenv
import argparse
import json
import os
import sys

import frontmatter


PROJECT_PATH = Path(__file__).resolve().parent
load_dotenv()

DEFAULT_VAULT_PATH = Path(os.getenv("SIGNAL_GARDEN_VAULT_PATH", r"C:\Loz"))
DEFAULT_CONFIG_PATH = Path(os.getenv("SIGNAL_GARDEN_CONFIG_PATH", "areas.json"))


CHECKS = []


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_check(ok, message):
    CHECKS.append((ok, message))


def resolve_config_path(config_path):
    path = Path(config_path)
    if not path.is_absolute():
        path = PROJECT_PATH / path
    return path


def validate_config(config_path):
    path = resolve_config_path(config_path)
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


def validate_memory(vault_path):
    memory = Path(vault_path) / "Memory"
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


def validate_sources(vault_path):
    sources = Path(vault_path) / "Sources"
    if not sources.exists():
        add_check(False, "Sources folder exists")
        return
    source_files = list(sources.glob("*.md"))
    add_check(bool(source_files), "at least one source note exists")

    for source_file in source_files[:1000]:
        post = frontmatter.loads(source_file.read_text(encoding="utf-8"))
        add_check(bool(post.get("title")), f"source has title: {source_file.name}")
        add_check(bool(post.get("url")), f"source has url: {source_file.name}")
        add_check(bool(post.get("domain")), f"source has domain: {source_file.name}")
        add_check(bool(post.get("retrieved_at")), f"source has retrieved_at: {source_file.name}")
        add_check(bool(post.get("source_type")), f"source has source_type: {source_file.name}")


def validate_open_notebook_artifacts(vault_path):
    reports = Path(vault_path) / "Reports"
    bundles = list(reports.glob("Open Notebook Podcast Bundle - *.json")) if reports.exists() else []
    for bundle in bundles[-5:]:
        payload = load_json(bundle, {})
        add_check("sources" in payload, f"podcast bundle has sources: {bundle.name}")
        add_check("podcast_prompt" in payload, f"podcast bundle has prompt: {bundle.name}")


def main():
    parser = argparse.ArgumentParser(description="Validate Signal Garden semantic state and artifacts.")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT_PATH), help="Obsidian vault path.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="areas.json path.")
    args = parser.parse_args()

    CHECKS.clear()
    validate_config(args.config)
    validate_memory(args.vault)
    validate_sources(args.vault)
    validate_open_notebook_artifacts(args.vault)

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
