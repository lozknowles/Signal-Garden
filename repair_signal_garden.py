from pathlib import Path
from dotenv import load_dotenv
import argparse
from datetime import datetime
import json
import os
import re

import frontmatter


load_dotenv()

DEFAULT_VAULT_PATH = Path(os.getenv("SIGNAL_GARDEN_VAULT_PATH", r"C:\Loz"))


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def repair_queue(vault_path, dry_run=True):
    path = Path(vault_path) / "Memory" / "research_queue.json"
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


def repair_relationships(vault_path, dry_run=True):
    path = Path(vault_path) / "Memory" / "concept_relationships.json"
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


def normalize_title(title, max_length=72):
    cleaned = re.sub(r"\s+", " ", str(title or "").strip())
    cleaned = re.sub(r'[\\/*?:"<>|]', "", cleaned)
    if not cleaned:
        return "Untitled"
    if len(cleaned) <= max_length:
        return cleaned
    if ":" in cleaned:
        prefix = cleaned.split(":", 1)[0].strip()
        if 10 <= len(prefix) <= max_length:
            return prefix
    return cleaned[: max_length - 1].rstrip() + "..."


def infer_url(content):
    match = re.search(r"https?://[^\s\])>]+", content)
    return match.group(0) if match else ""


def infer_domain(url):
    if not url:
        return ""
    match = re.match(r"https?://(?:www\.)?([^/]+)", url)
    return match.group(1).lower() if match else ""


def repair_source_frontmatter(vault_path, dry_run=True):
    sources = Path(vault_path) / "Sources"
    if not sources.exists():
        print("source frontmatter: skipped; Sources folder missing")
        return

    changed_count = 0
    for note_path in sorted(sources.glob("*.md")):
        post = frontmatter.loads(note_path.read_text(encoding="utf-8"))
        before = dict(post.metadata)

        tags = post.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list):
            tags = []
        if "source" not in tags:
            tags.append("source")
        post["tags"] = tags

        url = str(post.get("url") or infer_url(post.content)).strip()
        if url:
            post["url"] = url
            post["domain"] = post.get("domain") or infer_domain(url)

        full_title = post.get("full_title") or post.get("title") or note_path.stem
        post["full_title"] = str(full_title)[:240]
        post["title"] = normalize_title(post.get("title") or full_title)
        post["source_type"] = post.get("source_type") or "web"
        post["retrieved_at"] = post.get("retrieved_at") or post.get("created") or datetime.now().isoformat()

        changed = before != dict(post.metadata)
        if changed:
            changed_count += 1
            print(f"{note_path.name}: {'would repair' if dry_run else 'repair'}")
            if not dry_run:
                note_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    if changed_count == 0:
        print("source frontmatter: ok")
    else:
        print(f"source frontmatter: {'would repair' if dry_run else 'repaired'} {changed_count} note(s)")


def main():
    parser = argparse.ArgumentParser(description="Repair lightweight Signal Garden state files.")
    parser.add_argument("--apply", action="store_true", help="Write repaired files. Defaults to dry-run.")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT_PATH), help="Obsidian vault path.")
    args = parser.parse_args()
    dry_run = not args.apply

    repair_queue(args.vault, dry_run=dry_run)
    repair_relationships(args.vault, dry_run=dry_run)
    repair_source_frontmatter(args.vault, dry_run=dry_run)

    if dry_run:
        print("Dry run only. Re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
