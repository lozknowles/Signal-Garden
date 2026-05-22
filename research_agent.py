from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, date
from duckduckgo_search import DDGS
from itertools import combinations
from pathlib import Path

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
        overwrite=False
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

            post.content += (
                "\n\n---\n\n" +
                content
            )

        else:

            post = frontmatter.Post(

                content,

                created=datetime.now().isoformat(),

                tags=tags or []
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

    dashboard = "# Hermes Dashboard\n\n"

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

        "Hermes Dashboard",

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

articles = []

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

    articles.append(article)

    vault.save_note(

        "Sources",

        result["title"][:100],

        article,

        tags=["source"]
    )

# =========================================================
# COMBINE ARTICLES
# =========================================================

combined = "\n\n---\n\n".join(
    articles
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
