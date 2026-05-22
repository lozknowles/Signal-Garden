from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from duckduckgo_search import DDGS
from itertools import combinations
from pathlib import Path
from urllib.parse import urlparse
from html import escape as html_escape
import subprocess
import shutil

import frontmatter
import requests
import hashlib
import json
import os
import re

# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================================================
# PATH CONFIG
# =========================================================

VAULT_PATH = Path(r"C:\Loz")

CONFIG_PATH = Path(
    r"C:\HermesBridge\areas.json"
)

# =========================================================
# LOAD CONFIG
# =========================================================

with open(
    CONFIG_PATH,
    "r",
    encoding="utf-8"
) as f:

    CONFIG = json.load(f)

AREAS = CONFIG["folders"]

TOPICS = CONFIG["research_topics"]

PREFERRED_SOURCES = CONFIG[
    "preferred_sources"
]

MOC_CATEGORIES = CONFIG[
    "moc_categories"
]

# =========================================================
# CANONICAL CONCEPTS
# =========================================================

CANONICAL_CONCEPTS = {

    "ai agents":
        "AI Agents",

    "agent":
        "AI Agents",

    "agents":
        "AI Agents",

    "mcp":
        "MCP",

    "mcp server":
        "MCP",

    "knowledge graph":
        "Knowledge Graphs",

    "knowledge graphs":
        "Knowledge Graphs",

    "vector database":
        "Vector Databases",

    "vector databases":
        "Vector Databases",

    "local-first ai":
        "Local-First AI",

    "obsidian":
        "Obsidian",

    "persistent memory":
        "Persistent Memory",

    "federated learning":
        "Federated Learning",

    "voice ai":
        "Voice AI"
}

REVERSE_CANONICAL_CONCEPTS = {}

for raw_concept, canonical_concept in CANONICAL_CONCEPTS.items():

    REVERSE_CANONICAL_CONCEPTS.setdefault(
        canonical_concept,
        set()
    ).add(raw_concept)

for canonical_concept in list(
    REVERSE_CANONICAL_CONCEPTS.keys()
):

    REVERSE_CANONICAL_CONCEPTS[
        canonical_concept
    ].add(
        canonical_concept.lower()
    )

# =========================================================
# TAG TAXONOMY
# =========================================================

TAG_TAXONOMY = {

    "research": [

        "AI Agents",
        "MCP",
        "Knowledge Graphs",
        "Vector Databases"
    ],

    "architecture": [

        "Persistent Memory",
        "Federated Learning",
        "Local-First AI"
    ],

    "local-ai": [

        "Local-First AI",
        "Obsidian",
        "Voice AI"
    ],

    "memory-systems": [

        "Knowledge Graphs",
        "Persistent Memory",
        "Vector Databases"
    ],

    "ai-systems": [

        "AI Agents",
        "MCP",
        "Local-First AI"
    ]
}

# =========================================================
# OBSIDIAN CONNECTOR
# =========================================================

class ObsidianConnector:

    def __init__(self, vault_path):

        self.vault = Path(vault_path)

        self.ensure_structure()

    def ensure_structure(self):

        for folder in AREAS:

            (
                self.vault / folder
            ).mkdir(
                parents=True,
                exist_ok=True
            )

    def sanitize(self, text):

        return re.sub(
            r'[\\/*?:"<>|]',
            "",
            text
        )

    def path(
        self,
        folder,
        title
    ):

        return (
            self.vault /
            folder /
            f"{self.sanitize(title)}.md"
        )

    def save_note(
        self,
        folder,
        title,
        content,
        tags=None,
        overwrite=False,
        metadata=None
    ):

        note_path = self.path(
            folder,
            title
        )

        if note_path.exists() and not overwrite:

            with open(
                note_path,
                "r",
                encoding="utf-8"
            ) as f:

                post = frontmatter.load(f)

            existing_tags = set(
                post.get("tags", [])
            )

            new_tags = set(tags or [])

            post["tags"] = sorted(
                list(
                    existing_tags.union(
                        new_tags
                    )
                )
            )

            if metadata:

                for key, value in metadata.items():

                    if key == "tags":

                        continue

                    post[key] = value

            post.content += (
                "\n\n---\n\n" +
                content
            )

        else:

            post = frontmatter.Post(

                content,

                created=datetime.now().isoformat(),

                tags=tags or [],

                **(metadata or {})
            )

        with open(
            note_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                frontmatter.dumps(post)
            )

        print(f"Updated: {note_path}")

# =========================================================
# MEMORY PATHS
# =========================================================

MEMORY_PATH = (
    VAULT_PATH /
    "Memory" /
    "seen_hashes.json"
)

QUEUE_PATH = (
    VAULT_PATH /
    "Memory" /
    "research_queue.json"
)

FREQ_PATH = (
    VAULT_PATH /
    "Memory" /
    "concept_frequency.json"
)

STATE_PATH = (
    VAULT_PATH /
    "Memory" /
    "concept_state.json"
)

RELATIONSHIP_PATH = (
    VAULT_PATH /
    "Memory" /
    "concept_relationships.json"
)

# =========================================================
# LOAD SEMANTIC MEMORY
# =========================================================

if MEMORY_PATH.exists():

    with open(
        MEMORY_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        SEEN = json.load(f)

else:

    SEEN = []

# =========================================================
# LOAD RESEARCH QUEUE
# =========================================================

if QUEUE_PATH.exists():

    with open(
        QUEUE_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        RESEARCH_QUEUE = json.load(f)

else:

    RESEARCH_QUEUE = []

# =========================================================
# LOAD SEMANTIC STATE
# =========================================================

def load_json_file(path, default):

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


def today_iso():

    return date.today().isoformat()


def normalize_concept_record(value):

    if isinstance(value, dict):

        sightings = value.get("sightings", [])

        if not isinstance(sightings, list):

            sightings = []

        sightings = [
            s for s in sightings
            if isinstance(s, str)
        ][-30:]

        score = value.get(
            "score",
            value.get(
                "seen_count",
                value.get("count", 0)
            )
        )

        try:

            score = float(score)

        except (TypeError, ValueError):

            score = 0.0

        try:

            seen_count = int(
                value.get(
                    "seen_count",
                    value.get("count", 0)
                )
            )

        except (TypeError, ValueError):

            seen_count = 0

        return {
            "score": score,
            "seen_count": seen_count,
            "last_seen": value.get("last_seen"),
            "sightings": sightings
        }

    try:

        seen_count = int(value)

    except (TypeError, ValueError):

        seen_count = 0

    return {
        "score": float(seen_count),
        "seen_count": seen_count,
        "last_seen": None,
        "sightings": []
    }


def normalize_relationship_record(value):

    if isinstance(value, dict):

        sightings = value.get("sightings", [])

        if not isinstance(sightings, list):

            sightings = []

        sightings = [
            s for s in sightings
            if isinstance(s, str)
        ][-30:]

        try:

            weight = int(value.get("weight", 0))

        except (TypeError, ValueError):

            weight = 0

        return {
            "weight": weight,
            "last_seen": value.get("last_seen"),
            "sightings": sightings
        }

    return {
        "weight": 0,
        "last_seen": None,
        "sightings": []
    }


def recency_score_from_sightings(sightings, half_life_days=14):

    if not sightings:

        return 0.0

    today = date.today()
    score = 0.0

    for seen_at in sightings:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        days_old = max(
            (today - seen_day).days,
            0
        )

        score += 0.5 ** (
            days_old / half_life_days
        )

    return round(score, 4)


def concept_momentum(record):

    if record.get("sightings"):

        return recency_score_from_sightings(
            record["sightings"]
        )

    return float(record.get("score", 0.0))


def concept_velocity(record, window_days=7):

    if not record.get("sightings"):

        return 0

    today = date.today()
    count = 0

    for seen_at in record["sightings"]:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        if (today - seen_day).days <= window_days:

            count += 1

    return count


def sync_legacy_frequency_cache():

    global CONCEPT_FREQ

    CONCEPT_FREQ = {
        concept: record.get("seen_count", 0)
        for concept, record in CONCEPT_STATE.items()
    }


def persist_semantic_state():

    save_json_file(
        STATE_PATH,
        CONCEPT_STATE
    )

    save_json_file(
        FREQ_PATH,
        {
            concept: record.get("seen_count", 0)
            for concept, record in CONCEPT_STATE.items()
        }
    )

    save_json_file(
        RELATIONSHIP_PATH,
        CONCEPT_RELATIONSHIPS
    )


def update_concept_record(concept, seen_at):

    record = CONCEPT_STATE.get(
        concept,
        {
            "score": 0.0,
            "seen_count": 0,
            "last_seen": None,
            "sightings": []
        }
    )

    record["seen_count"] = int(
        record.get("seen_count", 0)
    ) + 1
    record["last_seen"] = seen_at

    sightings = list(
        record.get("sightings", [])
    )

    sightings.append(seen_at)
    record["sightings"] = sightings[-30:]
    record["score"] = recency_score_from_sightings(
        record["sightings"]
    )

    CONCEPT_STATE[concept] = record


def update_relationships(concepts, seen_at):

    if len(concepts) < 2:

        return

    for left, right in combinations(
        sorted(concepts),
        2
    ):

        key = f"{left}|{right}"

        record = CONCEPT_RELATIONSHIPS.get(
            key,
            {
                "weight": 0,
                "last_seen": None,
                "sightings": []
            }
        )

        record["weight"] = int(
            record.get("weight", 0)
        ) + 1
        record["last_seen"] = seen_at

        sightings = list(
            record.get("sightings", [])
        )
        sightings.append(seen_at)
        record["sightings"] = sightings[-30:]

        CONCEPT_RELATIONSHIPS[key] = record


def relationship_velocity(record, window_days=7):

    if not record.get("sightings"):

        return 0

    today = date.today()
    count = 0

    for seen_at in record["sightings"]:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        if (today - seen_day).days <= window_days:

            count += 1

    return count


if STATE_PATH.exists():

    raw_state = load_json_file(
        STATE_PATH,
        {}
    )

    CONCEPT_STATE = {
        concept: normalize_concept_record(value)
        for concept, value in raw_state.items()
    }

elif FREQ_PATH.exists():

    legacy_freq = load_json_file(
        FREQ_PATH,
        {}
    )

    CONCEPT_STATE = {
        concept: normalize_concept_record(value)
        for concept, value in legacy_freq.items()
    }

else:

    CONCEPT_STATE = {}

raw_relationships = load_json_file(
    RELATIONSHIP_PATH,
    {}
)

CONCEPT_RELATIONSHIPS = {
    key: normalize_relationship_record(value)
    for key, value in raw_relationships.items()
}

sync_legacy_frequency_cache()

# =========================================================
# HASHING
# =========================================================

def hash_text(text):

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()

def already_seen(text):

    return hash_text(text) in SEEN

def remember(text):

    h = hash_text(text)

    if h not in SEEN:

        SEEN.append(h)

        with open(
            MEMORY_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                SEEN,
                f,
                indent=2
            )

# =========================================================
# CONCEPT EXTRACTION
# =========================================================

def extract_concepts(text):

    found = set()

    lower = text.lower()

    for raw, canonical in CANONICAL_CONCEPTS.items():

        if raw in lower:

            found.add(canonical)

    return sorted(list(found))

# =========================================================
# TAG GENERATION
# =========================================================

def generate_tags(concepts):

    tags = set()

    for tag, mapped in TAG_TAXONOMY.items():

        for concept in concepts:

            if concept in mapped:

                tags.add(tag)

    tags.add("research")

    return sorted(list(tags))

# =========================================================
# WIKILINKING
# =========================================================

def wikify(text, concepts):

    for concept in concepts:

        text = re.sub(
            rf"\b{re.escape(concept)}\b",
            f"[[{concept}]]",
            text,
            flags=re.IGNORECASE
        )

    return text

# =========================================================
# EXTRACT CONTEXT
# =========================================================

def extract_concept_contexts(
    text,
    concepts
):

    contexts = {}

    paragraphs = text.split("\n\n")

    for concept in concepts:

        contexts[concept] = []

        for p in paragraphs:

            if concept.lower() in p.lower():

                cleaned = p.strip()

                if len(cleaned) > 80:

                    contexts[concept].append(
                        cleaned
                    )

    return contexts

# =========================================================
# SYNTHESIZE CONCEPT
# =========================================================

def synthesize_concept(
    concept,
    evidence
):

    joined = "\n\n".join(
        evidence[-20:]
    )

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                "content": f"""
You are building a semantic knowledge page.

Create a polished Obsidian note for:

{concept}

Include:
- definition
- practical relevance
- architectures
- implementation details
- related technologies
- emerging trends

Use markdown headings.

End with:

## Related Concepts
"""
            },

            {
                "role": "user",
                "content": joined
            }
        ]
    )

    return (
        response
        .choices[0]
        .message.content
    )

# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query):

    results = []

    try:

        with DDGS() as ddgs:

            raw = list(

                ddgs.text(
                    f"{query} AI LLM agents",
                    max_results=20
                )
            )

            for r in raw:

                url = r["href"].lower()

                if any(
                    domain in url
                    for domain in PREFERRED_SOURCES
                ):

                    results.append(
                        {
                            "title": r["title"],
                            "url": r["href"]
                        }
                    )

    except Exception as exc:

        print(
            f"Web search unavailable; continuing with recent source notes only: {exc}"
        )

    return results[:5]

# =========================================================
# DEFUDDLE
# =========================================================

def defuddle(url):

    try:

        response = requests.get(
            f"https://defuddle.md/{url}",
            timeout=30
        )

        if response.status_code == 200:

            return response.text

    except:
        pass

    return None

# =========================================================
# DAILY BRIEF
# =========================================================

def parse_iso_datetime(value):

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

    if not value:

        return None

    if value.tzinfo is not None:

        return value.replace(tzinfo=None)

    return value


def note_file_uri(path):

    return Path(path).resolve().as_uri()


def extract_source_note_record(note_path):

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


def collect_recent_source_notes(hours=24):

    sources_dir = VAULT_PATH / "Sources"

    if not sources_dir.exists():

        return []

    cutoff = datetime.now() - timedelta(hours=hours)

    records = []

    for note_path in sorted(
        sources_dir.glob("*.md")
    ):

        record = extract_source_note_record(note_path)

        if not record:

            continue

        seen_at = parse_iso_datetime(
            record.get("retrieved_at")
        )

        if seen_at and seen_at >= cutoff:

            records.append(record)

    records.sort(
        key=lambda item: item.get("retrieved_at", ""),
        reverse=True
    )

    return records


def build_recent_source_digest(source_records, max_sources=12):

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


def get_top_concepts(limit=5):

    ranked = sorted(
        CONCEPT_STATE.items(),
        key=lambda item: (
            concept_momentum(item[1]),
            item[1].get("seen_count", 0)
        ),
        reverse=True
    )

    return [
        concept
        for concept, _ in ranked[:limit]
    ]


def extract_matching_concepts(text, concepts):

    matches = []
    lower_text = text.lower()

    for concept in concepts:

        aliases = REVERSE_CANONICAL_CONCEPTS.get(
            concept,
            set()
        )

        for alias in aliases:

            if alias in lower_text:

                matches.append(concept)
                break

    return matches


def score_source_for_digging_deeper(record, highlight_lookup):

    score = 0

    reason = highlight_lookup.get(record["id"], "")

    if reason:

        score += 4

    published = parse_iso_datetime(
        record.get("published", "")
    )

    retrieved_at = parse_iso_datetime(
        record.get("retrieved_at", "")
    )

    age_anchor = published or retrieved_at

    if age_anchor:

        age_anchor = normalize_datetime_for_diff(
            age_anchor
        )

        age_hours = max(
            (
                normalize_datetime_for_diff(
                    datetime.now()
                ) - age_anchor
            ).total_seconds() / 3600,
            0
        )

        if age_hours <= 6:

            score += 3
        elif age_hours <= 24:

            score += 2
        elif age_hours <= 48:

            score += 1

    description = record.get("description", "") or ""
    snippet = record.get("content_excerpt", "") or ""
    text_blob = f"{record.get('title', '')} {description} {snippet}".lower()

    top_concepts = get_top_concepts(limit=5)
    matched_concepts = extract_matching_concepts(
        text_blob,
        top_concepts
    )

    score += len(matched_concepts) * 3

    if matched_concepts:

        score += 2

    if matched_concepts and len(matched_concepts) >= 2:

        score += 1

    for keyword in [
        "agent",
        "agents",
        "mcp",
        "federated",
        "memory",
        "workflow",
        "orchestr"
    ]:

        if keyword in text_blob:

            score += 1

    return score, reason, matched_concepts


def label_source_tier(score):

    if score >= 6:

        return "Must Read"

    if score >= 3:

        return "Worth Scanning"

    return "Background"


def rank_sources_for_followup(source_catalog, brief):

    highlight_lookup = {
        item.get("source_id"): item.get("reason", "")
        for item in brief.get("source_highlights", [])
    }

    ranked_sources = []

    for record in source_catalog:

        score, reason, matched_concepts = score_source_for_digging_deeper(
            record,
            highlight_lookup
        )

        ranked_sources.append(
            {
                "record": record,
                "score": score,
                "reason": reason,
                "matched_concepts": matched_concepts,
                "tier": label_source_tier(score)
            }
        )

    ranked_sources.sort(
        key=lambda item: (
            item["score"],
            item["record"].get("retrieved_at", "")
        ),
        reverse=True
    )

    return ranked_sources, highlight_lookup


def select_next_recommended_reading(ranked_sources, limit=3):

    if not ranked_sources:

        return []

    selected = []
    selected_ids = set()

    for tier in [
        "Must Read",
        "Worth Scanning",
        "Background"
    ]:

        tier_item = next(
            (
                item for item in ranked_sources
                if item["tier"] == tier and item["record"]["id"] not in selected_ids
            ),
            None
        )

        if tier_item:

            selected.append(tier_item)
            selected_ids.add(tier_item["record"]["id"])

        if len(selected) >= limit:

            return selected[:limit]

    for item in ranked_sources:

        if len(selected) >= limit:

            break

        source_id = item["record"]["id"]

        if source_id in selected_ids:

            continue

        selected.append(item)
        selected_ids.add(source_id)

    return selected[:limit]


def render_next_recommended_reading_markdown(
    source_items
):

    lines = [
        "## Next Recommended Reading",
        ""
    ]

    if not source_items:

        lines.append(
            "- No sources were found in the last 24 hours."
        )
        lines.append("")
        return "\n".join(lines)

    for item in source_items:

        record = item["record"]
        note_link = f"[[{record['note_title']}]]"
        article_link = f"[full article]({record.get('url', '')})"
        reason = item.get("reason", "")
        matched_concepts = item.get("matched_concepts", [])

        line = (
            f"- **{item['tier']}**: {note_link} · {article_link}"
        )

        if reason:

            line += f" — {reason}"

        if matched_concepts:

            line += (
                f" [concepts: {', '.join(matched_concepts)}]"
            )

        lines.append(line)

    lines.append("")
    return "\n".join(lines)


def render_next_recommended_reading_html(
    source_items
):

    if not source_items:

        return """
        <div class="empty-state">No sources were found in the last 24 hours.</div>
        """

    cards = []

    for item in source_items:

        record = item["record"]
        raw_title = record.get("title", "Untitled")
        title = html_escape(raw_title)
        note_title = html_escape(record.get("note_title", raw_title))
        url = html_escape(record.get("url", ""))
        note_uri = html_escape(record.get("note_uri", ""))
        reason = html_escape(item.get("reason", ""))
        matched_concepts = item.get("matched_concepts", [])
        concepts_html = ""

        if matched_concepts:

            concepts_html = (
                "<div class='item-meta'>"
                f"Concepts: {html_escape(', '.join(matched_concepts))}"
                "</div>"
            )

        cards.append(
            f"""
            <div class="followup-card">
              <div class="followup-tier">{html_escape(item['tier'])}</div>
              <div class="item-text"><a href="{note_uri}">{title}</a></div>
              <div class="item-meta">{note_title}</div>
              <div class="item-meta"><a href="{url}">Open full article</a></div>
              {f'<div class="item-meta">{reason}</div>' if reason else ''}
              {concepts_html}
            </div>
            """
        )

    return "\n".join(cards)

def build_source_catalog(source_records):

    catalog = []

    for index, record in enumerate(
        source_records,
        start=1
    ):

        source_id = record.get(
            "id",
            f"S{index}"
        )

        catalog.append(
            {
                "id": source_id,
                **record
            }
        )

    return catalog


def format_source_reference(record):

    note_link = record.get(
        "note_link",
        f"[[{record['note_title']}]]"
    )
    full_article = f"[full article]({record.get('url', '')})"

    return f"{note_link} ({full_article})"


def html_join_paragraphs(text):

    parts = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    if not parts:

        return ""

    return "".join(
        f"<p>{html_escape(part)}</p>"
        for part in parts
    )


def build_daily_brief_html(
    topic,
    brief,
    source_catalog,
    concepts,
    digging_deeper_title,
    digging_deeper_uri
):

    headline = html_escape(
        brief.get(
            "headline",
            f"Daily brief for {topic}"
        )
    )

    header_image_path = Path(r"C:\HermesBridge\header.png")
    header_image_uri = (
        header_image_path.resolve().as_uri()
        if header_image_path.exists()
        else ""
    )
    published_date_text = datetime.now().strftime("%d %B %Y")

    summary_points = brief.get(
        "summary_points",
        []
    )

    developments = brief.get(
        "key_developments",
        []
    )

    themes = brief.get(
        "emerging_themes",
        []
    )

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        brief
    )

    next_recommended = select_next_recommended_reading(
        ranked_sources
    )

    next_recommended_html = render_next_recommended_reading_html(
        next_recommended
    )

    highlights = brief.get(
        "source_highlights",
        []
    )

    summary_html = "".join(
        f"<li>{html_escape(point)}</li>"
        for point in summary_points
    ) or "<li>No summary points were generated.</li>"

    developments_html = ""

    if developments:

        cards = []

        for item in developments:

            text = html_escape(item.get("text", "").strip())
            refs = build_html_source_refs(
                item.get("source_ids", []),
                source_catalog
            )
            cards.append(
                f"""
                <div class="item-card">
                  <div class="item-text">{text}</div>
                  {f'<div class="item-meta">{refs}</div>' if refs else ''}
                </div>
                """
            )

        developments_html = "\n".join(cards)
    else:
        developments_html = """
        <div class="empty-state">No key developments were extracted for this brief.</div>
        """

    themes_html = ""

    if themes:

        cards = []

        for item in themes:

            text = html_escape(item.get("text", "").strip())
            refs = build_html_source_refs(
                item.get("source_ids", []),
                source_catalog
            )
            cards.append(
                f"""
                <div class="item-card item-card-accent">
                  <div class="item-text">{text}</div>
                  {f'<div class="item-meta">{refs}</div>' if refs else ''}
                </div>
                """
            )

        themes_html = "\n".join(cards)
    else:
        themes_html = """
        <div class="empty-state">No emerging themes were identified yet.</div>
        """

    source_cards = []

    for record in source_catalog:

        source_id = html_escape(record["id"])
        raw_title = record.get("title", "Untitled")
        title = html_escape(raw_title)
        note_title = html_escape(record.get("note_title", raw_title))
        url = html_escape(record.get("url", ""))
        note_uri = html_escape(record.get("note_uri", ""))
        domain = html_escape(record.get("domain", ""))
        retrieved_at = html_escape(record.get("retrieved_at", ""))
        reason = ""

        for item in highlights:

            if item.get("source_id") == record["id"]:

                reason = html_escape(item.get("reason", ""))
                break

        source_cards.append(
            f"""
            <div class="source-card">
              <div class="source-id">{source_id}</div>
              <div class="source-title"><a href="{note_uri}">{title}</a></div>
              <div class="source-meta">{note_title} · {domain}</div>
              <div class="source-meta"><a href="{url}">{url}</a></div>
              <div class="source-meta">Retrieved {retrieved_at}</div>
              {f'<div class="source-reason">{reason}</div>' if reason else ''}
            </div>
            """
        )

    source_cards_html = "\n".join(source_cards) or """
    <div class="empty-state">No sources were found in the last 24 hours.</div>
    """

    stats = {
        "sources": len(source_catalog),
        "developments": len(developments),
        "themes": len(themes),
        "concepts": len(concepts)
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Signal Garden Daily Brief</title>
  <style>
    @page {{
      size: A4;
      margin: 16mm 14mm 18mm 14mm;
    }}
    :root {{
      --bg: #f4efe6;
      --panel: rgba(255, 255, 255, 0.76);
      --panel-strong: rgba(255, 255, 255, 0.92);
      --ink: #1f2937;
      --muted: #5f6b7a;
      --accent: #375b4a;
      --accent-2: #8a5b31;
      --line: rgba(31, 41, 55, 0.12);
      --shadow: 0 14px 40px rgba(31, 41, 55, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Aptos", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(55, 91, 74, 0.14), transparent 34%),
        radial-gradient(circle at top right, rgba(138, 91, 49, 0.14), transparent 30%),
        linear-gradient(180deg, #fbf8f2 0%, var(--bg) 100%);
    }}
    .page {{
      padding: 18px;
    }}
    .shell {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .header-art {{
      position: relative;
      margin: 18px 18px 8px;
      border-radius: 22px;
      overflow: hidden;
      background: white;
    }}
    .header-art img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .header-date {{
      position: absolute;
      left: 7.8%;
      top: 50.7%;
      width: 33.5%;
      height: 8.4%;
      display: flex;
      align-items: center;
      padding-left: 24px;
      font-size: 17px;
      font-weight: 600;
      color: #245924;
      letter-spacing: 0.02em;
      text-shadow: 0 1px 0 rgba(255, 255, 255, 0.65);
      pointer-events: none;
    }}
    .report-strip {{
      padding: 0 22px 6px;
    }}
    .hero {{
      padding: 28px 28px 22px;
      background:
        linear-gradient(135deg, rgba(55, 91, 74, 0.96), rgba(44, 72, 60, 0.95));
      color: #f8fafc;
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: 0.18em;
      font-size: 11px;
      opacity: 0.78;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: 34px;
      line-height: 1.05;
    }}
    .subhead {{
      margin-top: 10px;
      font-size: 15px;
      max-width: 720px;
      color: rgba(248, 250, 252, 0.84);
    }}
    .meta-row {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      padding: 18px 20px 4px;
    }}
    .stat {{
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
    }}
    .stat-label {{
      display: block;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .stat-value {{
      font-size: 24px;
      font-weight: 700;
      color: var(--accent);
    }}
    .content {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      padding: 16px 20px 22px;
    }}
    .section {{
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 18px 18px 16px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .section h2 {{
      margin: 0 0 12px;
      font-size: 20px;
    }}
    .section h3 {{
      margin: 0 0 10px;
      font-size: 16px;
      color: var(--accent);
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
    }}
    li {{
      margin: 0 0 8px;
      line-height: 1.45;
    }}
    .item-grid {{
      display: grid;
      gap: 10px;
    }}
    .item-card {{
      background: rgba(244, 239, 230, 0.72);
      border: 1px solid rgba(55, 91, 74, 0.12);
      border-radius: 16px;
      padding: 14px 14px 12px;
    }}
    .item-card-accent {{
      background: rgba(55, 91, 74, 0.08);
      border-color: rgba(55, 91, 74, 0.18);
    }}
    .followup-card {{
      background: linear-gradient(180deg, rgba(55, 91, 74, 0.08), rgba(255, 255, 255, 0.9));
      border: 1px solid rgba(55, 91, 74, 0.18);
      border-radius: 16px;
      padding: 14px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .followup-tier {{
      display: inline-block;
      margin-bottom: 8px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--accent-2);
    }}
    .item-text {{
      font-size: 15px;
      line-height: 1.5;
      font-weight: 600;
    }}
    .item-text a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .item-meta, .source-meta, .source-reason {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
      word-break: break-word;
    }}
    .source-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .source-card {{
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .source-id {{
      display: inline-block;
      font-size: 11px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--accent-2);
      margin-bottom: 8px;
    }}
    .source-title {{
      font-size: 15px;
      font-weight: 700;
      line-height: 1.35;
    }}
    .source-title a,
    .source-ref a {{
      color: var(--accent);
      text-decoration: none;
    }}
    .source-meta a {{
      color: var(--accent);
      text-decoration: none;
      word-break: break-all;
    }}
    .footer {{
      padding: 0 22px 22px;
      color: var(--muted);
      font-size: 11px;
    }}
    .empty-state {{
      color: var(--muted);
      font-style: italic;
      padding: 4px 0;
    }}
    @media print {{
      body {{
        background: white;
      }}
      .page {{
        padding: 0;
      }}
      .shell {{
        box-shadow: none;
        border: none;
      }}
      a {{
        color: inherit;
        text-decoration: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="shell">
      <div class="header-art">
        <img src="{html_escape(header_image_uri)}" alt="Signal Garden header artwork" />
        <div class="header-date">{html_escape(published_date_text)}</div>
      </div>
      <div class="report-strip">
        <div class="eyebrow">Signal Garden Daily Brief</div>
        <div class="subhead">Generated {html_escape(datetime.now().isoformat())} · Topic: {html_escape(topic.title())}</div>
      </div>
      <div class="meta-row">
        <div class="stat"><span class="stat-label">Sources</span><span class="stat-value">{stats['sources']}</span></div>
        <div class="stat"><span class="stat-label">Developments</span><span class="stat-value">{stats['developments']}</span></div>
        <div class="stat"><span class="stat-label">Themes</span><span class="stat-value">{stats['themes']}</span></div>
        <div class="stat"><span class="stat-label">Concepts</span><span class="stat-value">{stats['concepts']}</span></div>
      </div>
      <div class="content">
        <div class="section">
          <h2>Executive Summary</h2>
          <ul>
            {summary_html}
          </ul>
        </div>
        <div class="section">
          <h2>Next Recommended Reading</h2>
          <div class="item-grid">
            {next_recommended_html}
          </div>
        </div>
        <div class="section">
          <h2>Key Developments</h2>
          <div class="item-grid">
            {developments_html}
          </div>
        </div>
        <div class="section">
          <h2>Emerging Themes</h2>
          <div class="item-grid">
            {themes_html}
          </div>
        </div>
        <div class="section">
          <h2>Source Appendix</h2>
          <div class="source-grid">
            {source_cards_html}
          </div>
        </div>
        <div class="section">
          <h2>Digging Deeper</h2>
          <p>Open the full Obsidian follow-up note: <a href="{html_escape(digging_deeper_uri)}">{html_escape(digging_deeper_title)}</a></p>
          <div class="item-grid">
            {''.join(
                f'<div class="item-card"><div class="item-text"><a href="{html_escape(record.get("note_uri", ""))}">{html_escape(record.get("title", "Untitled"))}</a></div><div class="item-meta"><a href="{html_escape(record.get("url", ""))}">full article</a></div></div>'
                for record in source_catalog[:6]
            ) if source_catalog else '<div class="empty-state">No recent sources to dig into.</div>'}
          </div>
        </div>
      </div>
      <div class="footer">
        Source links remain clickable in the HTML version. The PDF is generated from this same report.
      </div>
    </div>
  </div>
</body>
</html>"""


def build_html_source_refs(source_ids, source_catalog):

    if not source_ids:

        return ""

    lookup = {
        item["id"]: item
        for item in source_catalog
    }

    refs = []

    for source_id in source_ids:

        record = lookup.get(source_id)

        if not record:

            continue

        note_title = html_escape(
            record.get(
                "note_title",
                record.get("title", "Source")
            )
        )
        url = html_escape(record.get("url", ""))
        note_uri = html_escape(record.get("note_uri", ""))

        refs.append(
            (
                f"<span class='source-ref'>"
                f"{html_escape(source_id)}: "
                f"<a href=\"{note_uri}\">{note_title}</a> "
                f"(<a href=\"{url}\">full article</a>)"
                f"</span>"
            )
        )

    return " · ".join(refs)


def export_html_to_pdf(html_path, pdf_path):

    edge_paths = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]

    edge_exe = next(
        (
            path for path in edge_paths
            if Path(path).exists()
        ),
        shutil.which("msedge")
    )

    if not edge_exe:

        print("Edge was not found; skipping PDF export.")

        return False

    html_url = Path(html_path).resolve().as_uri()

    command = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        html_url
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120
    )

    if completed.returncode != 0:

        print(
            "PDF export failed:",
            completed.stderr.strip() or completed.stdout.strip()
        )

        return False

    return True


def render_source_refs(source_ids, source_catalog):

    if not source_ids:

        return ""

    lookup = {
        item["id"]: item
        for item in source_catalog
    }

    refs = []

    for source_id in source_ids:

        record = lookup.get(source_id)

        if not record:

            continue

        refs.append(
            f"{source_id}: {format_source_reference(record)}"
        )

    return "; ".join(refs)


def generate_daily_brief(
    topic,
    source_catalog,
    recent_source_digest,
    concepts
):

    if not source_catalog:

        return {
            "headline": f"Daily brief for {topic}",
            "summary_points": [
                "No source notes were found in the last 24 hours."
            ],
            "key_developments": [],
            "emerging_themes": [],
            "source_highlights": []
        }

    sources_text = "\n".join(
        [
            f"{item['id']}: {item['title']} | {item['domain']} | {item['url']}"
            for item in source_catalog
        ]
    )

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": """
You write a concise daily news brief for a local research system.

Return valid JSON only with these keys:
- headline: string
- summary_points: array of strings
- key_developments: array of objects with text and source_ids
- emerging_themes: array of objects with text and source_ids
- source_highlights: array of objects with source_id and reason

Rules:
- Use only the provided source IDs.
- Focus on what happened in the last 24 hours.
- Every factual bullet must include at least one source_id.
- Prefer short, readable bullets.
- Do not invent sources.
"""
                },
                {
                    "role": "user",
                    "content": f"""
TOPIC:
{topic}

RECENT CONCEPTS:
{", ".join(concepts) if concepts else "None"}

SOURCE CATALOG:
{sources_text}

RECENT SOURCE NOTES:
{recent_source_digest}
"""
                }
            ]
        )

        return json.loads(
            response.choices[0].message.content
        )

    except Exception:

        return {
            "headline": f"Daily brief for {topic}",
            "summary_points": [
                "Signal Garden reviewed the last 24 hours of source notes and updated semantic memory."
            ],
            "key_developments": [],
            "emerging_themes": [],
            "source_highlights": [
                {
                    "source_id": item["id"],
                    "reason": "Captured during this research run."
                }
                for item in source_catalog[:5]
            ]
        }


def render_daily_brief(
    topic,
    brief,
    source_catalog
):

    lines = []

    lines.append(
        "# Daily Brief"
    )
    lines.append(
        ""
    )
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append(
        f"Topic: [[{topic.title()}]]"
    )
    lines.append(
        ""
    )
    lines.append(
        f"## {brief.get('headline', f'Daily brief for {topic}')}"
    )
    lines.append(
        ""
    )

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        brief
    )

    next_recommended = select_next_recommended_reading(
        ranked_sources
    )

    summary_points = brief.get(
        "summary_points",
        []
    )

    lines.append(
        "### Summary"
    )
    lines.append("")

    if summary_points:

        for point in summary_points:

            lines.append(
                f"- {point}"
            )
    else:

        lines.append(
            "- No summary points were generated for this brief."
        )

    lines.append("")

    lines.extend(
        render_next_recommended_reading_markdown(
            next_recommended
        ).splitlines()
    )

    developments = brief.get(
        "key_developments",
        []
    )

    if developments:

        lines.append(
            "### Key Developments"
        )
        lines.append("")

        for item in developments:

            lines.append(
                f"- {item.get('text', '').strip()}"
            )

            sources = render_source_refs(
                item.get("source_ids", []),
                source_catalog
            )

            if sources:

                lines.append(
                    f"  - Sources: {sources}"
                )

        lines.append("")

    themes = brief.get(
        "emerging_themes",
        []
    )

    if themes:

        lines.append(
            "### Emerging Themes"
        )
        lines.append("")

        for item in themes:

            lines.append(
                f"- {item.get('text', '').strip()}"
            )

            sources = render_source_refs(
                item.get("source_ids", []),
                source_catalog
            )

            if sources:

                lines.append(
                    f"  - Sources: {sources}"
                )

        lines.append("")

    highlights = brief.get(
        "source_highlights",
        []
    )

    if highlights:

        lines.append(
            "### Read Full Articles"
        )
        lines.append("")

        for item in highlights:

            source_id = item.get("source_id")

            match = next(
                (
                    record for record in source_catalog
                    if record["id"] == source_id
                ),
                None
            )

            if not match:

                continue

            lines.append(
                f"- {format_source_reference(match)} - {item.get('reason', '').strip()}"
            )

        lines.append("")

    lines.append(
        "### Source Index"
    )
    lines.append("")

    for record in source_catalog:

        lines.append(
            f"- {record['id']}: {format_source_reference(record)}"
        )

    return "\n".join(lines)


def render_digging_deeper_markdown(
    topic,
    source_catalog,
    brief,
    deeper_note_title
):

    ranked_sources, highlight_lookup = rank_sources_for_followup(
        source_catalog,
        brief
    )

    lines = []

    lines.append(
        f"# {deeper_note_title}"
    )
    lines.append("")
    lines.append(
        f"Topic: [[{topic.title()}]]"
    )
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append("")

    next_recommended = select_next_recommended_reading(
        ranked_sources
    )

    lines.extend(
        render_next_recommended_reading_markdown(
            next_recommended
        ).splitlines()
    )

    grouped = {
        "Must Read": [],
        "Worth Scanning": [],
        "Background": []
    }

    for item in ranked_sources:

        grouped[item["tier"]].append(item)

    for section_name in [
        "Must Read",
        "Worth Scanning",
        "Background"
    ]:

        section_items = grouped[section_name]

        lines.append(
            f"## {section_name}"
        )
        lines.append("")

        if not section_items:

            lines.append(
                "- No sources in this tier."
            )
            lines.append("")
            continue

        for item in section_items:

            record = item["record"]
            reason = item["reason"]
            matched_concepts = item.get(
                "matched_concepts",
                []
            )
            note_link = f"[[{record['note_title']}]]"
            article_link = f"[full article]({record.get('url', '')})"

            line = (
                f"- {note_link} · {article_link}"
            )

            if reason:

                line += f" — {reason}"

            if matched_concepts:

                line += (
                    f" [concepts: {', '.join(matched_concepts)}]"
                )

            lines.append(line)

        lines.append("")

    lines.append("")
    lines.append(
        "## Recent Sources"
    )
    lines.append("")

    if source_catalog:

        for record in source_catalog:

            note_link = f"[[{record['note_title']}]]"
            article_link = f"[full article]({record.get('url', '')})"
            published = record.get("published", "")
            retrieved_at = record.get("retrieved_at", "")
            description = record.get("description", "").strip()
            snippet = record.get("content_excerpt", "").strip()
            reason = highlight_lookup.get(record["id"], "")

            lines.append(
                f"### {record['title']}"
            )
            lines.append("")
            lines.append(
                f"- Obsidian note: {note_link}"
            )
            lines.append(
                f"- Article: {article_link}"
            )

            if published:

                lines.append(
                    f"- Published: {published}"
                )

            if retrieved_at:

                lines.append(
                    f"- Retrieved: {retrieved_at}"
                )

            if reason:

                lines.append(
                    f"- Why it matters: {reason}"
                )

            if description:

                lines.append(
                    f"- Description: {description}"
                )

            if snippet:

                lines.append(
                    ""
                )
                lines.append("Excerpt:")
                lines.append("")
                lines.append(snippet)

            lines.append("")

    else:

        lines.append("- No source notes were found in the last 24 hours.")

    return "\n".join(lines)

# =========================================================
# SMART TOPIC SELECTION
# =========================================================

def choose_research_topic():

    if RESEARCH_QUEUE:

        topic = RESEARCH_QUEUE.pop(0)

        with open(
            QUEUE_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                RESEARCH_QUEUE,
                f,
                indent=2
            )

        return topic

    scored = []

    for index, topic in enumerate(TOPICS):

        score = 0

        for concept, record in CONCEPT_STATE.items():

            if concept.lower() in topic.lower():

                score += concept_momentum(
                    record
                )

        scored.append(
            (
                score,
                -index,
                topic
            )
        )

    scored.sort(
        reverse=True
    )

    return scored[0][2]

# =========================================================
# AUTONOMOUS DISCOVERY
# =========================================================

def discover_new_topics(concepts):

    discovered = []

    for concept in concepts:

        if concept not in TOPICS:

            discovered.append(concept)

    return discovered

# =========================================================
# DASHBOARD
# =========================================================

def generate_dashboard():

    dashboard = "# Signal Garden Dashboard\n\n"

    dashboard += (
        f"Last Updated: "
        f"{datetime.now()}\n\n"
    )

    # =====================================
    # RESEARCH QUEUE
    # =====================================

    dashboard += (
        "## Current Research Queue\n\n"
    )

    if RESEARCH_QUEUE:

        for i, topic in enumerate(
            RESEARCH_QUEUE,
            start=1
        ):

            dashboard += (
                f"{i}. [[{topic}]]\n"
            )

    else:

        dashboard += (
            "- Queue is empty\n"
        )

    # =====================================
    # CONCEPT MOMENTUM
    # =====================================

    dashboard += (
        "\n## Most Active Concepts\n\n"
    )

    sorted_concepts = sorted(
        CONCEPT_STATE.items(),
        key=lambda item: (
            concept_momentum(item[1]),
            item[1].get("seen_count", 0)
        ),
        reverse=True
    )

    if sorted_concepts:

        for concept, record in sorted_concepts[:10]:

            dashboard += (
                f"- [[{concept}]] "
                f"(score {concept_momentum(record):.2f}, "
                f"seen {record.get('seen_count', 0)}, "
                f"velocity {concept_velocity(record)})\n"
            )

    else:

        dashboard += (
            "- No concepts tracked yet\n"
        )

    # =====================================
    # FASTEST RISING
    # =====================================

    dashboard += (
        "\n## Fastest Rising Concepts\n\n"
    )

    rising_concepts = sorted(
        CONCEPT_STATE.items(),
        key=lambda item: (
            concept_velocity(item[1]),
            concept_momentum(item[1])
        ),
        reverse=True
    )

    top_rising = [
        item for item in rising_concepts
        if concept_velocity(item[1]) > 0
    ][:5]

    if top_rising:

        for concept, record in top_rising:

            dashboard += (
                f"- [[{concept}]] "
                f"(last 7d {concept_velocity(record)}, "
                f"last seen {record.get('last_seen')})\n"
            )

    else:

        dashboard += (
            "- No recent movement yet\n"
        )

    # =====================================
    # ACTIVE TAGS
    # =====================================

    dashboard += (
        "\n## Active Semantic Domains\n\n"
    )

    active_tags = set()

    for concept in CONCEPT_STATE:

        generated = generate_tags(
            [concept]
        )

        for tag in generated:

            active_tags.add(tag)

    for tag in sorted(active_tags):

        dashboard += (
            f"- #{tag}\n"
        )

    # =====================================
    # CONCEPT RELATIONSHIPS
    # =====================================

    dashboard += (
        "\n## Active Concept Relationships\n\n"
    )

    sorted_relationships = sorted(
        CONCEPT_RELATIONSHIPS.items(),
        key=lambda item: (
            item[1].get("weight", 0),
            relationship_velocity(item[1])
        ),
        reverse=True
    )

    top_relationships = sorted_relationships[:10]

    if top_relationships:

        for key, record in top_relationships:

            left, right = key.split("|", 1)

            dashboard += (
                f"- [[{left}]] ↔ [[{right}]] "
                f"(weight {record.get('weight', 0)}, "
                f"velocity {relationship_velocity(record)})\n"
            )

    else:

        dashboard += (
            "- No relationships tracked yet\n"
        )

    # =====================================
    # SYSTEM STATUS
    # =====================================

    dashboard += (
        "\n## System Status\n\n"
    )

    dashboard += (
        f"- Sources Indexed: "
        f"{len(SEEN)}\n"
    )

    dashboard += (
        f"- Concepts Tracked: "
        f"{len(CONCEPT_STATE)}\n"
    )

    dashboard += (
        f"- Relationships Tracked: "
        f"{len(CONCEPT_RELATIONSHIPS)}\n"
    )

    dashboard += (
        f"- Queue Length: "
        f"{len(RESEARCH_QUEUE)}\n"
    )

    # =====================================
    # SAVE DASHBOARD
    # =====================================

    vault.save_note(

        "MOCs",

        "Signal Garden Dashboard",

        dashboard,

        tags=["dashboard"],

        overwrite=True
    )

# =========================================================
# INITIALIZE
# =========================================================

vault = ObsidianConnector(
    VAULT_PATH
)

TOPIC = choose_research_topic()

print(f"\nTOPIC: {TOPIC}\n")

# =========================================================
# SEARCH
# =========================================================

results = web_search(TOPIC)

source_records = []

today_stamp = today_iso()

for result in results:

    print(
        f"Fetching: {result['title']}"
    )

    article = defuddle(
        result["url"]
    )

    if not article:
        continue

    if already_seen(article):

        print("Skipping duplicate")

        continue

    remember(article)

    domain = urlparse(
        result["url"]
    ).netloc.replace(
        "www.",
        ""
    )

    source_records.append(
        {
            "title": result["title"][:100],
            "url": result["url"],
            "domain": domain,
            "retrieved_at": datetime.now().isoformat(),
            "topic": TOPIC,
            "content": article,
            "note_title": result["title"][:100]
        }
    )

    vault.save_note(

        "Sources",

        result["title"][:100],

        article,

        tags=["source"],

        metadata={
            "url": result["url"],
            "domain": domain,
            "retrieved_at": datetime.now().isoformat(),
            "topic": TOPIC,
            "source_type": "web"
        }
    )

# =========================================================
# COMBINE ARTICLES
# =========================================================

combined = "\n\n---\n\n".join(
    [
        record["content"]
        for record in source_records
    ]
)

# =========================================================
# GPT SYNTHESIS
# =========================================================

response = client.chat.completions.create(

    model="gpt-4o-mini",

    messages=[

        {
            "role": "system",
            "content": """
Write an Obsidian markdown research report.

Use:
- headings
- concise analysis
- bullet points
- implementation ideas
- architecture insights
- emerging trends

End with:
## Related Concepts
"""
        },

        {
            "role": "user",
            "content":
                f"""
TOPIC:
{TOPIC}

ARTICLES:
{combined}
"""
        }
    ]
)

research = (
    response
    .choices[0]
    .message.content
)

# =========================================================
# SEMANTIC PROCESSING
# =========================================================

concepts = extract_concepts(
    research
)

# =========================================================
# UPDATE CONCEPT STATE
# =========================================================

seen_at = today_iso()

for concept in concepts:

    update_concept_record(
        concept,
        seen_at
    )

update_relationships(
    concepts,
    seen_at
)

# =========================================================
# PERSIST SEMANTIC STATE
# =========================================================

persist_semantic_state()

sync_legacy_frequency_cache()

# =========================================================
# DISCOVER NEW TOPICS
# =========================================================

new_topics = discover_new_topics(
    concepts
)

for topic in new_topics:

    if topic not in RESEARCH_QUEUE:

        RESEARCH_QUEUE.append(topic)

with open(
    QUEUE_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        RESEARCH_QUEUE,
        f,
        indent=2
    )

# =========================================================
# TAGS + LINKS
# =========================================================

tags = generate_tags(
    concepts
)

linked = wikify(
    research,
    concepts
)

print(f"\nTags: {tags}")

print(f"\nConcepts: {concepts}")

# =========================================================
# SAVE RESEARCH NOTE
# =========================================================

vault.save_note(

    "Research",

    TOPIC.title(),

    f"""
# Research Update

Generated:
{datetime.now()}

{linked}
""",

    tags=tags
)

# =========================================================
# DAILY BRIEF
# =========================================================

recent_source_notes = collect_recent_source_notes(
    hours=24
)

source_catalog = build_source_catalog(
    recent_source_notes
)

recent_source_digest = build_recent_source_digest(
    source_catalog
)

digging_deeper_title = f"Digging Deeper - {today_stamp}"

daily_brief = generate_daily_brief(
    TOPIC,
    source_catalog,
    recent_source_digest,
    concepts
)

daily_brief_content = render_daily_brief(
    TOPIC,
    daily_brief,
    source_catalog
)

daily_brief_content += (
    f"\n\n## Digging Deeper\n\n"
    f"Open the follow-up note: [[{digging_deeper_title}]]\n"
)

vault.save_note(

    "Daily",

    f"Daily Brief - {today_stamp}",

    daily_brief_content,

    tags=[
        "daily",
        "brief",
        "news"
    ],
    overwrite=True,

    metadata={
        "topic": TOPIC,
        "generated_at": datetime.now().isoformat(),
        "source_count": len(source_catalog)
    }
)

digging_deeper_content = render_digging_deeper_markdown(
    TOPIC,
    source_catalog,
    daily_brief,
    digging_deeper_title
)

vault.save_note(

    "Daily",

    digging_deeper_title,

    digging_deeper_content,

    tags=[
        "daily",
        "brief",
        "digging-deeper"
    ],
    overwrite=True,

    metadata={
        "topic": TOPIC,
        "generated_at": datetime.now().isoformat(),
        "source_count": len(source_catalog)
    }
)

reports_dir = VAULT_PATH / "Reports"
reports_dir.mkdir(
    parents=True,
    exist_ok=True
)

daily_brief_html = build_daily_brief_html(
    TOPIC,
    daily_brief,
    source_catalog,
    concepts,
    digging_deeper_title,
    (
        vault.path("Daily", digging_deeper_title)
        .resolve()
        .as_uri()
    )
)

html_path = reports_dir / f"Daily Brief - {today_stamp}.html"
pdf_path = reports_dir / f"Daily Brief - {today_stamp}.pdf"

with open(
    html_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        daily_brief_html
    )

if export_html_to_pdf(
    html_path,
    pdf_path
):

    print(
        f"Daily PDF exported: {pdf_path}"
    )
else:

    print(
        f"Daily PDF export skipped or failed for: {pdf_path}"
    )

# =========================================================
# CONCEPT MEMORY EXTRACTION
# =========================================================

concept_contexts = extract_concept_contexts(
    linked,
    concepts
)

for concept, contexts in concept_contexts.items():

    memory_text = "\n\n---\n\n".join(
        contexts
    )

    vault.save_note(

        "ConceptMemory",

        concept,

        memory_text,

        tags=["memory"]
    )

    memory_file = vault.path(
        "ConceptMemory",
        concept
    )

    with open(
        memory_file,
        "r",
        encoding="utf-8"
    ) as f:

        memory_content = f.read()

    synthesized = synthesize_concept(

        concept,

        [memory_content]
    )

    concept_tags = generate_tags(
        [concept]
    )

    vault.save_note(

        "Areas",

        concept,

        synthesized,

        tags=concept_tags,

        overwrite=True
    )

# =========================================================
# MOC GENERATION
# =========================================================

for moc, mapped in MOC_CATEGORIES.items():

    matched = []

    for concept in concepts:

        if concept in mapped:

            matched.append(concept)

    if matched:

        content = (
            f"# {moc} MOC\n\n"
        )

        for m in matched:

            content += (
                f"- [[{m}]]\n"
            )

        vault.save_note(

            "MOCs",

            f"{moc} MOC",

            content,

            tags=["moc"],

            overwrite=True
        )

# =========================================================
# GENERATE DASHBOARD
# =========================================================

generate_dashboard()

# =========================================================
# COMPLETE
# =========================================================

print("\nResearch completed successfully.")
print("\nObsidian vault updated.")

print("\nResearch Queue:")
print(RESEARCH_QUEUE)

print("\nConcept Frequencies:")
print(CONCEPT_FREQ)
