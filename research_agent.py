from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from duckduckgo_search import DDGS
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
# LOAD CONCEPT FREQUENCIES
# =========================================================

if FREQ_PATH.exists():

    with open(
        FREQ_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        CONCEPT_FREQ = json.load(f)

else:

    CONCEPT_FREQ = {}

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

    for topic in TOPICS:

        score = 0

        for concept in CONCEPT_FREQ:

            if concept.lower() in topic.lower():

                score += CONCEPT_FREQ[
                    concept
                ]

        scored.append(
            (
                score,
                topic
            )
        )

    scored.sort()

    return scored[0][1]

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
    # CONCEPT FREQUENCIES
    # =====================================

    dashboard += (
        "\n## Most Frequent Concepts\n\n"
    )

    sorted_concepts = sorted(

        CONCEPT_FREQ.items(),

        key=lambda x: x[1],

        reverse=True
    )

    for concept, count in sorted_concepts[:10]:

        dashboard += (
            f"- [[{concept}]] "
            f"({count})\n"
        )

    # =====================================
    # ACTIVE TAGS
    # =====================================

    dashboard += (
        "\n## Active Semantic Domains\n\n"
    )

    active_tags = set()

    for concept in CONCEPT_FREQ:

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
        f"{len(CONCEPT_FREQ)}\n"
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
# UPDATE CONCEPT FREQUENCIES
# =========================================================

for concept in concepts:

    CONCEPT_FREQ[concept] = (

        CONCEPT_FREQ.get(
            concept,
            0
        ) + 1
    )

with open(
    FREQ_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        CONCEPT_FREQ,
        f,
        indent=2
    )

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