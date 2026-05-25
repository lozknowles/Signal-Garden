from pathlib import Path
import argparse
import json


VAULT_PATH = Path(r"C:\Loz")


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def repair_queue(dry_run=True):
    path = VAULT_PATH / "Memory" / "research_queue.json"
    queue = load_json(path, [])
    repaired = []
    seen = set()

    for topic in queue:
        if not isinstance(topic, str):
            continue
        topic = topic.strip()
        key = topic.lower()
        if not topic or key in seen:
            continue
        seen.add(key)
        repaired.append(topic)

    changed = repaired != queue
    print(f"research_queue.json: {'would repair' if dry_run and changed else 'repair' if changed else 'ok'}")
    if changed and not dry_run:
        save_json(path, repaired)


def repair_relationships(dry_run=True):
    path = VAULT_PATH / "Memory" / "concept_relationships.json"
    relationships = load_json(path, {})
    repaired = {}

    for key, record in relationships.items():
        if not isinstance(key, str) or "|" not in key or not isinstance(record, dict):
            continue
        left, right = [part.strip() for part in key.split("|", 1)]
        if not left or not right or left == right:
            continue
        canonical_key = "|".join(sorted([left, right]))
        existing = repaired.setdefault(canonical_key, {
            "weight": 0,
            "last_seen": record.get("last_seen"),
            "sightings": []
        })
        existing["weight"] += int(record.get("weight", 0))
        existing["sightings"].extend(record.get("sightings", []))
        if record.get("last_seen"):
            existing["last_seen"] = max(existing.get("last_seen") or "", record["last_seen"])

    changed = repaired != relationships
    print(f"concept_relationships.json: {'would repair' if dry_run and changed else 'repair' if changed else 'ok'}")
    if changed and not dry_run:
        save_json(path, repaired)


def main():
    parser = argparse.ArgumentParser(description="Repair lightweight Signal Garden state files.")
    parser.add_argument("--apply", action="store_true", help="Write repaired files. Defaults to dry-run.")
    args = parser.parse_args()
    dry_run = not args.apply

    repair_queue(dry_run=dry_run)
    repair_relationships(dry_run=dry_run)

    if dry_run:
        print("Dry run only. Re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
