from datetime import datetime
from pathlib import Path

import frontmatter


def parse_iso_datetime(value):
    """Parse stored source timestamps from frontmatter or API payloads."""
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    normalized = value.strip()

    if not normalized:
        return None

    try:
        return datetime.fromisoformat(normalized)

    except ValueError:
        try:
            return datetime.fromisoformat(
                normalized.replace("Z", "+00:00")
            )

        except ValueError:
            return None


def normalize_datetime_for_diff(value):
    """Drop timezone info before comparing mixed local and API timestamps."""
    if not value:
        return None

    if value.tzinfo is not None:
        return value.replace(tzinfo=None)

    return value


def note_file_uri(path):
    """Return an Obsidian-friendly local file URI for a note."""
    return Path(path).resolve().as_uri()


def extract_source_note_record(note_path):
    """Read one source note, including legacy nested frontmatter."""
    try:
        with open(
            note_path,
            "r",
            encoding="utf-8"
        ) as f:

            outer_post = frontmatter.load(f)

    except Exception:
        return None

    outer_meta = dict(
        outer_post.metadata or {}
    )

    inner_meta = {}
    inner_content = outer_post.content

    if inner_content.lstrip().startswith("---"):

        try:
            inner_post = frontmatter.loads(inner_content)

            inner_meta = dict(
                inner_post.metadata or {}
            )

            inner_content = inner_post.content

        except Exception:
            inner_meta = {}

    retrieved_at = (
        parse_iso_datetime(
            outer_meta.get("retrieved_at")
        ) or
        parse_iso_datetime(
            inner_meta.get("retrieved_at")
        ) or
        parse_iso_datetime(
            outer_meta.get("created")
        )
    )

    if not retrieved_at:

        try:
            retrieved_at = datetime.fromtimestamp(
                Path(note_path).stat().st_mtime
            )

        except Exception:
            retrieved_at = None

    return {
        "id": Path(note_path).stem,
        "note_title": inner_meta.get(
            "title",
            outer_meta.get(
                "title",
                Path(note_path).stem
            )
        ),
        "note_path": str(note_path),
        "note_uri": note_file_uri(note_path),
        "title": inner_meta.get(
            "title",
            outer_meta.get(
                "title",
                Path(note_path).stem
            )
        ),
        "full_title": outer_meta.get(
            "full_title",
            inner_meta.get(
                "full_title",
                outer_meta.get(
                    "title",
                    inner_meta.get(
                        "title",
                        Path(note_path).stem
                    )
                )
            )
        ),
        "site": inner_meta.get(
            "site",
            outer_meta.get("domain", "")
        ),
        "published": inner_meta.get(
            "published",
            outer_meta.get("published", "")
        ),
        "url": inner_meta.get(
            "source",
            outer_meta.get(
                "url",
                ""
            )
        ),
        "domain": outer_meta.get(
            "domain",
            inner_meta.get("domain", "")
        ),
        "topic": outer_meta.get(
            "topic",
            inner_meta.get("topic", "")
        ),
        "description": inner_meta.get(
            "description",
            outer_meta.get("description", "")
        ),
        "word_count": inner_meta.get(
            "word_count",
            outer_meta.get("word_count")
        ),
        "retrieved_at": retrieved_at.isoformat() if retrieved_at else "",
        "content_excerpt": inner_content.strip()[:2500],
    }


def build_recent_source_digest(source_records, max_sources=12):
    """Render recent source records into the GPT digest input."""
    snippets = []

    for record in source_records[:max_sources]:

        header = (
            f"Source ID: {record.get('id')}\n"
            f"Title: {record.get('title', '')}\n"
            f"Site: {record.get('site', '')}\n"
            f"Published: {record.get('published', '')}\n"
            f"Retrieved: {record.get('retrieved_at', '')}\n"
            f"URL: {record.get('url', '')}\n"
        )

        excerpt = record.get("content_excerpt", "").strip()

        if excerpt:

            header += (
                f"Excerpt:\n{excerpt}\n"
            )

        snippets.append(header)

    return "\n---\n".join(snippets)
