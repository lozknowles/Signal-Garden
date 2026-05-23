from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from duckduckgo_search import DDGS
from itertools import combinations
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlparse
from html import escape as html_escape, unescape as html_unescape
import sys
import subprocess
import smtplib
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

PRIORITY_TOPICS = CONFIG.get(
    "priority_topics",
    []
)

PREFERRED_SOURCES = CONFIG[
    "preferred_sources"
]

MOC_CATEGORIES = CONFIG[
    "moc_categories"
]

MOBILE_QUERY_HINTS = {
    "mobile development": [
        "mobile app architecture",
        "native mobile development",
        "cross-platform mobile development",
        "Android iOS React Native PWA"
    ],
    "mobile app architecture": [
        "mobile app architecture",
        "native mobile development",
        "cross-platform mobile development",
        "Android iOS React Native PWA"
    ],
    "native mobile development": [
        "native mobile development",
        "Android iOS native app development",
        "official documentation"
    ],
    "cross-platform mobile development": [
        "cross-platform mobile development",
        "React Native Flutter Progressive Web Apps"
    ],
    "react native": [
        "React Native",
        "React Native official guide",
        "React Native architecture"
    ],
    "progressive web apps": [
        "Progressive Web Apps",
        "PWA service worker manifest",
        "web app architecture"
    ],
    "android development": [
        "Android development",
        "Android developer guide",
        "Kotlin Android app architecture"
    ],
    "ios development": [
        "iOS development",
        "Apple developer guide",
        "SwiftUI app architecture"
    ],
    "augmented reality apps": [
        "augmented reality apps",
        "ARKit ARCore mobile development",
        "location based AR"
    ],
    "augmented reality": [
        "augmented reality apps",
        "ARKit ARCore mobile development",
        "location based AR"
    ],
    "speech interfaces on mobile": [
        "speech interfaces on mobile",
        "mobile speech recognition",
        "voice assistant app development"
    ],
    "speech interfaces": [
        "speech interfaces on mobile",
        "mobile speech recognition",
        "voice assistant app development"
    ],
    "gpx mapping and route tracking": [
        "GPX mapping and route tracking",
        "mapkit gpx route tracking",
        "location tracking app development"
    ],
    "gpx mapping": [
        "GPX mapping and route tracking",
        "mapkit gpx route tracking",
        "location tracking app development"
    ],
    "route tracking": [
        "GPX mapping and route tracking",
        "mapkit gpx route tracking",
        "location tracking app development"
    ],
    "image-based location detection": [
        "image-based location detection",
        "visual place recognition mobile",
        "photo geolocation app"
    ]
}

MOBILE_SEARCH_DOMAINS = {
    "mobile development": [
        "developer.android.com",
        "developer.apple.com",
        "reactnative.dev",
        "docs.expo.dev",
        "flutter.dev"
    ],
    "mobile app architecture": [
        "developer.android.com",
        "developer.apple.com",
        "reactnative.dev",
        "docs.expo.dev",
        "flutter.dev"
    ],
    "native mobile development": [
        "developer.android.com",
        "developer.apple.com",
        "kotlinlang.org",
        "swift.org",
        "docs.expo.dev"
    ],
    "cross-platform mobile development": [
        "reactnative.dev",
        "flutter.dev",
        "docs.expo.dev",
        "ionicframework.com",
        "capacitorjs.com"
    ],
    "react native": [
        "reactnative.dev",
        "docs.expo.dev",
        "expo.dev",
        "github.com",
        "developer.android.com"
    ],
    "progressive web apps": [
        "developer.mozilla.org",
        "web.dev",
        "learn.microsoft.com",
        "github.com",
        "developers.google.com"
    ],
    "android development": [
        "developer.android.com",
        "kotlinlang.org",
        "developers.google.com",
        "github.com",
        "stackoverflow.com"
    ],
    "ios development": [
        "developer.apple.com",
        "swift.org",
        "github.com",
        "docs.expo.dev",
        "reactnative.dev"
    ],
    "augmented reality apps": [
        "developer.apple.com",
        "developer.android.com",
        "unity.com",
        "github.com",
        "docs.unity.com"
    ],
    "augmented reality": [
        "developer.apple.com",
        "developer.android.com",
        "unity.com",
        "github.com",
        "docs.unity.com"
    ],
    "speech interfaces on mobile": [
        "developer.android.com",
        "developer.apple.com",
        "reactnative.dev",
        "github.com",
        "learn.microsoft.com"
    ],
    "speech interfaces": [
        "developer.android.com",
        "developer.apple.com",
        "reactnative.dev",
        "github.com",
        "learn.microsoft.com"
    ],
    "gpx mapping and route tracking": [
        "mapbox.com",
        "openstreetmap.org",
        "developer.android.com",
        "developer.apple.com",
        "github.com"
    ],
    "gpx mapping": [
        "mapbox.com",
        "openstreetmap.org",
        "developer.android.com",
        "developer.apple.com",
        "github.com"
    ],
    "route tracking": [
        "mapbox.com",
        "openstreetmap.org",
        "developer.android.com",
        "developer.apple.com",
        "github.com"
    ],
    "image-based location detection": [
        "developers.google.com",
        "developer.android.com",
        "developer.apple.com",
        "github.com",
        "mapbox.com"
    ]
}

MOBILE_RESULT_KEYWORDS = {
    "mobile development": [
        "mobile",
        "android",
        "ios",
        "react native",
        "pwa",
        "flutter"
    ],
    "mobile app architecture": [
        "mobile",
        "android",
        "ios",
        "react native",
        "pwa",
        "flutter"
    ],
    "native mobile development": [
        "android",
        "ios",
        "kotlin",
        "swift",
        "native"
    ],
    "cross-platform mobile development": [
        "react native",
        "flutter",
        "pwa",
        "cross-platform"
    ],
    "react native": [
        "react native",
        "expo",
        "reactnative"
    ],
    "progressive web apps": [
        "pwa",
        "progressive web app",
        "service worker",
        "web app"
    ],
    "android development": [
        "android",
        "kotlin",
        "jetpack",
        "android studio"
    ],
    "ios development": [
        "ios",
        "swift",
        "swiftui",
        "xcode"
    ],
    "augmented reality apps": [
        "augmented reality",
        "arkit",
        "arcore",
        "unity"
    ],
    "augmented reality": [
        "augmented reality",
        "arkit",
        "arcore",
        "unity"
    ],
    "speech interfaces on mobile": [
        "speech",
        "voice",
        "recognition",
        "dictation"
    ],
    "speech interfaces": [
        "speech",
        "voice",
        "recognition",
        "dictation"
    ],
    "gpx mapping and route tracking": [
        "gpx",
        "route tracking",
        "mapping",
        "mapbox",
        "openstreetmap"
    ],
    "gpx mapping": [
        "gpx",
        "route tracking",
        "mapping",
        "mapbox",
        "openstreetmap"
    ],
    "route tracking": [
        "gpx",
        "route tracking",
        "mapping",
        "mapbox",
        "openstreetmap"
    ],
    "image-based location detection": [
        "visual place",
        "location detection",
        "geolocation",
        "image"
    ]
}

OCR_QUERY_HINTS = {
    "open source ocr": [
        "open source OCR",
        "open source document OCR",
        "OCR engine"
    ],
    "ocr": [
        "OCR",
        "optical character recognition",
        "open source OCR"
    ],
    "document ocr": [
        "document OCR",
        "open source document OCR",
        "OCR engine"
    ]
}

OCR_SEARCH_DOMAINS = {
    "open source ocr": [
        "github.com",
        "tesseract-ocr.github.io",
        "huggingface.co",
        "github.io",
        "readthedocs.io"
    ],
    "ocr": [
        "github.com",
        "tesseract-ocr.github.io",
        "huggingface.co",
        "github.io",
        "readthedocs.io"
    ],
    "document ocr": [
        "github.com",
        "tesseract-ocr.github.io",
        "huggingface.co",
        "github.io",
        "readthedocs.io"
    ]
}

OCR_RESULT_KEYWORDS = {
    "open source ocr": [
        "ocr",
        "tesseract",
        "easyocr",
        "paddleocr",
        "text recognition"
    ],
    "ocr": [
        "ocr",
        "tesseract",
        "easyocr",
        "paddleocr",
        "text recognition"
    ],
    "document ocr": [
        "ocr",
        "tesseract",
        "easyocr",
        "paddleocr",
        "text recognition"
    ]
}

MOBILE_SCOPE_TOPICS = {
    "mobile development",
    "mobile app architecture",
    "native mobile development",
    "cross-platform mobile development",
    "react native",
    "progressive web apps",
    "android development",
    "ios development",
    "augmented reality",
    "augmented reality apps",
    "speech interfaces",
    "speech interfaces on mobile",
    "gpx",
    "gpx mapping",
    "gpx mapping and route tracking",
    "route tracking",
    "image-based location detection"
}

OCR_SCOPE_TOPICS = {
    "ocr",
    "optical character recognition",
    "open source ocr",
    "document ocr"
}

MOBILE_PLATFORM_LABELS = {
    "android development": "Android",
    "ios development": "iOS",
    "mobile development": "Mobile umbrella"
}

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
        "Voice AI",

    "ocr":
        "OCR",

    "optical character recognition":
        "OCR",

    "open source ocr":
        "Open Source OCR",

    "document ocr":
        "Open Source OCR",

    "mobile app architecture":
        "Mobile Development",

    "mobile development":
        "Mobile Development",

    "native mobile development":
        "Mobile Development",

    "cross-platform mobile development":
        "Mobile Development",

    "react native":
        "React Native",

    "progressive web apps":
        "Progressive Web Apps",

    "android development":
        "Android Development",

    "ios development":
        "iOS Development",

    "augmented reality":
        "Augmented Reality",

    "augmented reality apps":
        "Augmented Reality",

    "speech interfaces":
        "Speech Interfaces",

    "speech interfaces on mobile":
        "Speech Interfaces",

    "gpx":
        "GPX Mapping",

    "gpx mapping":
        "GPX Mapping",

    "route tracking":
        "GPX Mapping",

    "image-based location detection":
        "Visual Location Detection"
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


def normalize_note_title(title, max_length=72):

    cleaned = re.sub(
        r"\s+",
        " ",
        str(title).strip()
    )

    cleaned = re.sub(
        r'[\\/*?:"<>|]',
        "",
        cleaned
    )

    if not cleaned:

        return "Untitled"

    if len(cleaned) <= max_length:

        return cleaned

    if ":" in cleaned:

        prefix = cleaned.split(":", 1)[0].strip()

        if 10 <= len(prefix) <= max_length:

            return prefix

    trimmed = cleaned[: max_length - 1].rstrip()

    return f"{trimmed}…"


def normalize_topic_label(value):

    return re.sub(
        r"\s+",
        " ",
        str(value).strip()
    ).lower()


TOPIC_DISPLAY_OVERRIDES = {
    "ai agents": "AI Agents",
    "mcp": "MCP",
    "gpx mapping": "GPX Mapping",
    "mobile development": "Mobile Development",
    "android development": "Android Development",
    "ios development": "iOS Development",
    "react native": "React Native",
    "progressive web apps": "Progressive Web Apps",
    "augmented reality": "Augmented Reality",
    "speech interfaces": "Speech Interfaces",
    "visual location detection": "Visual Location Detection",
    "open source ocr": "Open Source OCR",
    "ocr": "OCR",
    "federated learning": "Federated Learning"
}


def format_topic_display(value):

    topic = str(value).strip()
    override = TOPIC_DISPLAY_OVERRIDES.get(
        normalize_topic_label(topic)
    )

    if override:

        return override

    return topic.title()


def resolve_recent_source_scope(topic):

    if not topic:

        return None

    topic_key = normalize_topic_label(topic)

    if topic_key in MOBILE_SCOPE_TOPICS:

        return MOBILE_SCOPE_TOPICS

    if topic_key in OCR_SCOPE_TOPICS:

        return OCR_SCOPE_TOPICS

    return {topic_key}


def build_mobile_platform_balance(source_catalog):

    balance = {}

    for record in source_catalog:

        topic_key = normalize_topic_label(
            record.get("topic", "")
        )

        label = MOBILE_PLATFORM_LABELS.get(topic_key)

        if label:

            balance[label] = balance.get(label, 0) + 1
            continue

        if topic_key in MOBILE_SCOPE_TOPICS:

            balance["Shared mobile"] = balance.get(
                "Shared mobile",
                0
            ) + 1

    return balance


def build_topic_coverage(source_catalog, limit=8):

    coverage = {}

    for record in source_catalog:

        topic = record.get("topic", "").strip() or "Unassigned"
        key = normalize_topic_label(topic)
        entry = coverage.setdefault(
            key,
            {
                "topic": topic,
                "count": 0,
                "latest": "",
                "domains": set()
            }
        )

        entry["count"] += 1
        entry["domains"].add(record.get("domain", ""))

        retrieved_at = record.get("retrieved_at", "")

        if retrieved_at > entry["latest"]:

            entry["latest"] = retrieved_at

    ranked = sorted(
        coverage.values(),
        key=lambda item: (
            item["count"],
            item["latest"]
        ),
        reverse=True
    )

    return ranked[:limit]


def format_topic_coverage_lines(topic_coverage):

    if not topic_coverage:

        return ["- No active areas were found in the last 24 hours."]

    lines = []

    for item in topic_coverage:

        domain_count = len(
            [
                domain
                for domain in item.get("domains", set())
                if domain
            ]
        )

        lines.append(
            f"- {item['topic']}: {item['count']} source notes"
            + (
                f" across {domain_count} domains"
                if domain_count
                else ""
            )
        )

    return lines


def build_new_area_coverage(topic_coverage, limit=5):

    if not topic_coverage:

        return []

    emerging = [
        item
        for item in topic_coverage
        if item.get("count", 0) <= 2
    ]

    if not emerging:

        emerging = list(topic_coverage)

    emerging.sort(
        key=lambda item: (
            item.get("count", 0),
            item.get("latest", "")
        )
    )

    return emerging[:limit]


def format_new_area_lines(topic_coverage):

    emerging = build_new_area_coverage(
        topic_coverage
    )

    if not emerging:

        return ["- No new areas were identified in the last 24 hours."]

    lines = []

    for item in emerging:

        domain_count = len(
            [
                domain
                for domain in item.get("domains", set())
                if domain
            ]
        )

        lines.append(
            f"- {item['topic']}: {item['count']} source notes"
            + (
                f" across {domain_count} domains"
                if domain_count
                else ""
            )
        )

    return lines

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

EMAIL_STATE_PATH = (
    VAULT_PATH /
    "Logs" /
    "pdf_email_state.json"
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

queue_updated = False

for priority_topic in PRIORITY_TOPICS:

    if priority_topic not in RESEARCH_QUEUE and priority_topic in TOPICS:

        RESEARCH_QUEUE.append(priority_topic)
        queue_updated = True

if queue_updated:

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


def load_email_state():

    return load_json_file(
        EMAIL_STATE_PATH,
        {
            "last_sent_day": None,
            "last_sent_pdf": None,
            "last_sent_at": None
        }
    )


def save_email_state(state):

    save_json_file(
        EMAIL_STATE_PATH,
        state
    )


def parse_bool_env(name, default=False):

    value = os.getenv(name)

    if value is None:

        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


def send_pdf_email(
    pdf_path,
    subject,
    body_text,
    body_html,
    to_addresses,
    from_address,
    smtp_host,
    smtp_port=587,
    smtp_username=None,
    smtp_password=None,
    use_tls=True
):

    if not pdf_path.exists():

        return False, "PDF attachment not found."

    if not to_addresses:

        return False, "No email recipients configured."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = ", ".join(to_addresses)
    message.set_content(body_text)

    if body_html:

        message.add_alternative(
            body_html,
            subtype="html"
        )

    with open(
        pdf_path,
        "rb"
    ) as f:

        pdf_data = f.read()

    message.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=pdf_path.name
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:

        if use_tls:

            server.starttls()

        if smtp_username and smtp_password:

            server.login(
                smtp_username,
                smtp_password
            )

        server.send_message(message)

    return True, "Email sent successfully."


def send_text_email(
    subject,
    body_text,
    body_html,
    to_addresses,
    from_address,
    smtp_host,
    smtp_port=587,
    smtp_username=None,
    smtp_password=None,
    use_tls=True
):

    if not to_addresses:

        return False, "No email recipients configured."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = ", ".join(to_addresses)
    message.set_content(body_text)

    if body_html:

        message.add_alternative(
            body_html,
            subtype="html"
        )

    with smtplib.SMTP(smtp_host, smtp_port) as server:

        if use_tls:

            server.starttls()

        if smtp_username and smtp_password:

            server.login(
                smtp_username,
                smtp_password
            )

        server.send_message(message)

    return True, "Email sent successfully."


def build_pdf_email_body(
    topic,
    summary_points,
    next_recommended,
    digging_deeper_title,
    digging_deeper_uri,
    digging_deeper_items,
    pdf_path,
    today_stamp
):

    plain_lines = [
        f"Signal Garden daily PDF for {topic}.",
        "",
        f"Attached file: {pdf_path.name}",
        f"Date: {today_stamp}",
        "",
        "Top summary points:"
    ]

    if summary_points:

        for point in summary_points[:5]:

            plain_lines.append(f"- {point}")
    else:

        plain_lines.append("- No summary points were generated.")

    plain_lines.extend(
        [
            "",
            "Next Recommended Reading:"
        ]
    )

    if next_recommended:

        for item in next_recommended:

            record = item["record"]
            title = record.get("title", "Untitled")
            note_uri = record.get("note_uri", "")
            url = record.get("url", "")
            reason = item.get("reason", "")
            matched_concepts = item.get("matched_concepts", [])
            tier_label = item.get("focus_label", item["tier"])

            plain_line = (
                f"- {tier_label}: {title}"
                f" | Obsidian: {note_uri}"
                f" | Full article: {url}"
            )

            if reason:

                plain_line += f" | {reason}"

            if matched_concepts:

                plain_line += (
                    f" | Concepts: {', '.join(matched_concepts)}"
                )

            plain_lines.append(plain_line)
    else:

        plain_lines.append("- No sources were found in the last 24 hours.")

    plain_lines.extend(
        [
            "",
            "Digging Deeper:"
        ]
    )

    if digging_deeper_title and digging_deeper_uri:

        plain_lines.append(
            f"- Open the follow-up note: {digging_deeper_title} | {digging_deeper_uri}"
        )

    if digging_deeper_items:

        for item in digging_deeper_items:

            record = item["record"]
            title = record.get("title", "Untitled")
            note_uri = record.get("note_uri", "")
            url = record.get("url", "")
            reason = item.get("reason", "")
            plain_line = (
                f"- {item['tier']}: {title}"
                f" | Obsidian: {note_uri}"
                f" | Full article: {url}"
            )

            if reason:

                plain_line += f" | {reason}"

            plain_lines.append(plain_line)
    else:

        plain_lines.append("- No deeper-reading sources were found.")

    plain_lines.extend(
        [
            "",
            "This message is sent once per day to avoid duplicate delivery from the 30-minute scheduler."
        ]
    )

    html_lines = [
        "<div style='font-family:Arial,sans-serif;line-height:1.6;color:#1f2937;'>",
        f"<h2>Signal Garden daily PDF for {html_escape(topic)}</h2>",
        f"<p><strong>Attached file:</strong> {html_escape(pdf_path.name)}<br/>",
        f"<strong>Date:</strong> {html_escape(today_stamp)}</p>",
        "<h3>Top summary points</h3>",
        "<ul>"
    ]

    if summary_points:

        for point in summary_points[:5]:

            html_lines.append(f"<li>{html_escape(point)}</li>")
    else:

        html_lines.append("<li>No summary points were generated.</li>")

    html_lines.append("</ul>")
    html_lines.append("<h3>Next Recommended Reading</h3>")

    if next_recommended:

        html_lines.append("<ul>")

        for item in next_recommended:

            record = item["record"]
            title = html_escape(record.get("title", "Untitled"))
            note_uri = html_escape(record.get("note_uri", ""))
            url = html_escape(record.get("url", ""))
            reason = html_escape(item.get("reason", ""))
            matched_concepts = item.get("matched_concepts", [])
            tier_label = html_escape(item.get("focus_label", item["tier"]))

            html_lines.append(
                "<li>"
                f"<strong>{tier_label}</strong>: "
                f"<a href=\"{note_uri}\">{title}</a> "
                f"(<a href=\"{url}\">full article</a>)"
            )

            if reason:

                html_lines.append(
                    f"<div>{reason}</div>"
                )

            if matched_concepts:

                html_lines.append(
                    f"<div><em>Concepts:</em> {html_escape(', '.join(matched_concepts))}</div>"
                )

            html_lines.append("</li>")

        html_lines.append("</ul>")
    else:

        html_lines.append("<p>No sources were found in the last 24 hours.</p>")

    html_lines.append("<h3>Digging Deeper</h3>")

    if digging_deeper_title and digging_deeper_uri:

        html_lines.append(
            f"<p>Open the follow-up note: <a href=\"{html_escape(digging_deeper_uri)}\">{html_escape(digging_deeper_title)}</a></p>"
        )

    if digging_deeper_items:

        html_lines.append("<ul>")

        for item in digging_deeper_items:

            record = item["record"]
            title = html_escape(record.get("title", "Untitled"))
            note_uri = html_escape(record.get("note_uri", ""))
            url = html_escape(record.get("url", ""))
            reason = html_escape(item.get("reason", ""))

            html_lines.append(
                "<li>"
                f"<strong>{html_escape(item['tier'])}</strong>: "
                f"<a href=\"{note_uri}\">{title}</a> "
                f"(<a href=\"{url}\">full article</a>)"
            )

            if reason:

                html_lines.append(f"<div>{reason}</div>")

            html_lines.append("</li>")

        html_lines.append("</ul>")
    else:

        html_lines.append("<p>No deeper-reading sources were found.</p>")

    html_lines.append(
        "<p style='color:#6b7280;font-size:12px;'>This message is sent once per day to avoid duplicate delivery from the 30-minute scheduler.</p>"
    )
    html_lines.append("</div>")

    return "\n".join(plain_lines), "\n".join(html_lines)


def maybe_email_daily_pdf(
    pdf_path,
    topic,
    daily_brief,
    source_catalog,
    digging_deeper_title,
    digging_deeper_uri,
    today_stamp
):

    if not parse_bool_env("PDF_EMAIL_ENABLED", False):

        print("PDF email skipped: PDF_EMAIL_ENABLED is not enabled.")
        return

    to_raw = os.getenv("PDF_EMAIL_TO", "").strip()
    from_address = os.getenv("PDF_EMAIL_FROM", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_port_raw = os.getenv("SMTP_PORT", "587").strip()
    use_tls = parse_bool_env("SMTP_USE_TLS", True)
    include_next_reading = parse_bool_env(
        "PDF_EMAIL_BODY_INCLUDE_NEXT_READING",
        True
    )
    max_next_reading_raw = os.getenv(
        "PDF_EMAIL_MAX_NEXT_READING",
        "3"
    ).strip()

    if not (to_raw and from_address and smtp_host):

        print("PDF email skipped: missing PDF_EMAIL_TO, PDF_EMAIL_FROM, or SMTP_HOST.")
        return

    to_addresses = [
        address.strip()
        for address in to_raw.split(",")
        if address.strip()
    ]

    if not to_addresses:

        print("PDF email skipped: no valid recipients found.")
        return

    try:

        smtp_port = int(smtp_port_raw)

    except ValueError:

        smtp_port = 587

    try:

        max_next_reading = int(max_next_reading_raw)

    except ValueError:

        max_next_reading = 3

    state = load_email_state()

    if state.get("last_sent_day") == today_stamp and state.get("last_sent_pdf") == pdf_path.name:

        print(
            f"PDF email already sent for {today_stamp}; skipping duplicate."
        )
        return

    subject_prefix = os.getenv(
        "PDF_EMAIL_SUBJECT_PREFIX",
        "Signal Garden Daily Brief"
    ).strip()

    subject = f"{subject_prefix} - {today_stamp}"

    brief_for_ranking = dict(daily_brief)
    brief_for_ranking["topic_coverage"] = build_topic_coverage(
        source_catalog
    )

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        brief_for_ranking
    )

    next_recommended = select_next_recommended_reading(
        ranked_sources,
        topic_coverage=topic_coverage
    )

    if not include_next_reading:

        next_recommended = []
    else:

        next_recommended = next_recommended[:max_next_reading]

    digging_deeper_items = ranked_sources[:3]

    body_text, body_html = build_pdf_email_body(
        topic=topic,
        summary_points=daily_brief.get("summary_points", []),
        next_recommended=next_recommended,
        digging_deeper_title=digging_deeper_title,
        digging_deeper_uri=digging_deeper_uri,
        digging_deeper_items=digging_deeper_items,
        pdf_path=pdf_path,
        today_stamp=today_stamp
    )

    success, message = send_pdf_email(
        pdf_path=pdf_path,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        to_addresses=to_addresses,
        from_address=from_address,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username or from_address,
        smtp_password=smtp_password,
        use_tls=use_tls
    )

    if success:

        state.update(
            {
                "last_sent_day": today_stamp,
                "last_sent_pdf": pdf_path.name,
                "last_sent_at": datetime.now().isoformat(),
                "last_subject": subject,
                "last_recipients": to_addresses
            }
        )

        save_email_state(state)

        print(
            f"PDF email sent to {', '.join(to_addresses)}"
        )
    else:

        print(
            f"PDF email skipped: {message}"
        )


def send_daily_pdf_test_email():

    if not parse_bool_env("PDF_EMAIL_ENABLED", False):

        print(
            "PDF test email will still use SMTP settings, even though PDF_EMAIL_ENABLED is off."
        )

    to_raw = os.getenv("PDF_EMAIL_TO", "").strip()
    from_address = os.getenv("PDF_EMAIL_FROM", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_port_raw = os.getenv("SMTP_PORT", "587").strip()
    use_tls = parse_bool_env("SMTP_USE_TLS", True)

    if not (to_raw and from_address and smtp_host):

        print(
            "Test email skipped: missing PDF_EMAIL_TO, PDF_EMAIL_FROM, or SMTP_HOST."
        )
        return False

    to_addresses = [
        address.strip()
        for address in to_raw.split(",")
        if address.strip()
    ]

    if not to_addresses:

        print("Test email skipped: no valid recipients found.")
        return False

    try:

        smtp_port = int(smtp_port_raw)

    except ValueError:

        smtp_port = 587

    subject_prefix = os.getenv(
        "PDF_EMAIL_SUBJECT_PREFIX",
        "Signal Garden Daily Brief"
    ).strip()

    subject = f"{subject_prefix} - Test Email"
    body_text = (
        "This is a Signal Garden test email.\n\n"
        "If you received this message, SMTP is configured correctly."
    )
    body_html = (
        "<div style='font-family:Arial,sans-serif;'>"
        "<h2>Signal Garden test email</h2>"
        "<p>If you received this message, SMTP is configured correctly.</p>"
        "</div>"
    )

    success, message = send_text_email(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        to_addresses=to_addresses,
        from_address=from_address,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username or from_address,
        smtp_password=smtp_password,
        use_tls=use_tls
    )

    if success:

        print(f"Test email sent to {', '.join(to_addresses)}")
        return True

    print(f"Test email skipped: {message}")
    return False


if any(
    arg in {
        "--test-email",
        "--send-test-email"
    }
    for arg in sys.argv[1:]
):

    send_daily_pdf_test_email()
    raise SystemExit(0)


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

    query_variants = [query]
    query_key = query.lower().strip()
    is_mobile_query = query_key in MOBILE_QUERY_HINTS
    is_ocr_query = query_key in OCR_QUERY_HINTS

    if is_mobile_query:

        query_variants.extend(MOBILE_QUERY_HINTS[query_key])

        for domain in MOBILE_SEARCH_DOMAINS.get(query_key, []):

            query_variants.append(
                f"site:{domain} {query}"
            )

            for hint in MOBILE_QUERY_HINTS[query_key]:

                query_variants.append(
                    f"site:{domain} {hint}"
                )
    elif is_ocr_query:

        query_variants.extend(
            OCR_QUERY_HINTS.get(query_key, [])
        )

        for domain in OCR_SEARCH_DOMAINS.get(query_key, []):

            query_variants.append(
                f"site:{domain} {query}"
            )

            for hint in OCR_QUERY_HINTS.get(query_key, []):

                query_variants.append(
                    f"site:{domain} {hint}"
                )
    else:

        query_variants.extend(
            [
                f"{query} official documentation",
                f"{query} developer guide"
            ]
        )

        if any(
            keyword in query_key
            for keyword in [
                "ai",
                "agent",
                "mcp"
            ]
        ):

            query_variants.append(
                f"{query} AI LLM agents"
            )

    try:

        with DDGS() as ddgs:

            seen_urls = set()
            allowed_domains = (
                MOBILE_SEARCH_DOMAINS.get(query_key, [])
                if is_mobile_query
                else OCR_SEARCH_DOMAINS.get(query_key, [])
                if is_ocr_query
                else PREFERRED_SOURCES
            )

            for search_query in query_variants:

                raw = list(

                    ddgs.text(
                        search_query,
                        max_results=12
                    )
                )

                for r in raw:

                    href = r["href"]
                    url = href.lower()

                    if href in seen_urls:

                        continue

                    if any(
                        domain in url
                        for domain in allowed_domains
                    ):

                        seen_urls.add(href)
                        results.append(
                            {
                                "title": r["title"],
                                "url": href
                            }
                        )

            if (is_mobile_query or is_ocr_query) and not results:

                fallback_keywords = (
                    MOBILE_RESULT_KEYWORDS.get(query_key, [])
                    if is_mobile_query
                    else OCR_RESULT_KEYWORDS.get(query_key, [])
                )

                for search_query in query_variants:

                    raw = list(

                        ddgs.text(
                            search_query,
                            max_results=12
                        )
                    )

                    for r in raw:

                        href = r["href"]
                        url = href.lower()
                        haystack = (
                            f"{r['title']} {href}"
                        ).lower()

                        if href in seen_urls:

                            continue

                        if not fallback_keywords:

                            continue

                        if any(
                            keyword in haystack
                            for keyword in fallback_keywords
                        ):

                            seen_urls.add(href)
                            results.append(
                                {
                                    "title": r["title"],
                                    "url": href
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


def collect_recent_source_notes(hours=24, topic=None):

    sources_dir = VAULT_PATH / "Sources"

    if not sources_dir.exists():

        return []

    cutoff = datetime.now() - timedelta(hours=hours)

    records = []
    topic_scope = resolve_recent_source_scope(topic)

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

            if topic_scope and normalize_topic_label(
                record.get("topic")
            ) not in topic_scope:

                continue

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


SOURCE_DOMAIN_WEIGHTS = {

    "arxiv.org": 3.0,
    "github.com": 2.5,
    "openai.com": 2.5,
    "anthropic.com": 2.5,
    "microsoft.com": 2.0,
    "deepmind.google": 2.5,
    "huggingface.co": 2.0,
    "langchain.com": 2.0,
    "mistral.ai": 2.0,
    "ollama.com": 2.0,
    "simonwillison.net": 2.0,
    "towardsdatascience.com": 1.5,
    "medium.com": 1.0,
    "replicate.com": 1.5
}


def source_quality_profile(record):

    score = 0.0
    signals = []

    domain = (record.get("domain", "") or "").lower()

    for pattern, weight in SOURCE_DOMAIN_WEIGHTS.items():

        if pattern in domain:

            score += weight
            signals.append(f"trusted:{pattern}")
            break

    published = parse_iso_datetime(record.get("published", ""))
    retrieved_at = parse_iso_datetime(record.get("retrieved_at", ""))
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

            score += 2.0
            signals.append("fresh:6h")
        elif age_hours <= 24:

            score += 1.5
            signals.append("fresh:24h")
        elif age_hours <= 72:

            score += 1.0
            signals.append("fresh:72h")

    content_excerpt = record.get("content_excerpt", "") or ""
    if len(content_excerpt) >= 1200:

        score += 0.75
        signals.append("depth:long")
    elif len(content_excerpt) >= 500:

        score += 0.5
        signals.append("depth:medium")

    if record.get("description"):

        score += 0.25
        signals.append("has:description")

    if record.get("published"):

        score += 0.25
        signals.append("has:published")

    if len(record.get("note_title", "") or record.get("title", "")) > 60:

        score += 0.25
        signals.append("title:descriptive")

    if score >= 4.5:

        label = "High"
    elif score >= 3.0:

        label = "Strong"
    elif score >= 1.5:

        label = "Standard"
    else:

        label = "Light"

    return {
        "score": round(score, 2),
        "label": label,
        "signals": signals
    }


def signal_window_delta(sightings, recent_window=7, comparison_window=7):

    if not sightings:

        return {
            "recent": 0,
            "previous": 0,
            "delta": 0
        }

    today = date.today()
    recent = 0
    previous = 0

    for seen_at in sightings:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        days_old = max(
            (today - seen_day).days,
            0
        )

        if days_old <= recent_window:

            recent += 1
        elif days_old <= recent_window + comparison_window:

            previous += 1

    return {
        "recent": recent,
        "previous": previous,
        "delta": recent - previous
    }


def concept_trend_delta(record, recent_window=7, comparison_window=7):

    return signal_window_delta(
        record.get("sightings", []),
        recent_window=recent_window,
        comparison_window=comparison_window
    )


def detect_sustained_trend_alerts(
    source_catalog,
    recent_window=1,
    comparison_window=1,
    min_recent=5,
    min_delta=3,
    min_source_count=3
):

    alerts = []

    for concept, record in CONCEPT_STATE.items():

        trend = concept_trend_delta(
            record,
            recent_window=recent_window,
            comparison_window=comparison_window
        )

        recent = trend["recent"]
        previous = trend["previous"]
        delta = trend["delta"]

        if recent < min_recent:

            continue

        if delta < min_delta:

            continue

        if recent <= previous:

            continue

        matching_sources = [
            source for source in source_catalog
            if concept in source.get("archive_concepts", [])
        ]

        if not matching_sources:

            continue

        if len(matching_sources) < min_source_count:

            continue

        alerts.append(
            {
                "concept": concept,
                "recent": recent,
                "previous": previous,
                "delta": delta,
                "momentum": concept_momentum(record),
                "last_seen": record.get("last_seen"),
                "source_count": len(matching_sources),
                "sources": matching_sources[:5],
                "reason": (
                    f"{recent} sightings in the last 24 hours vs "
                    f"{previous} in the prior 24 hours "
                    f"(delta +{delta})."
                )
            }
        )

    alerts.sort(
        key=lambda item: (
            item["delta"],
            item["recent"],
            item["momentum"]
        ),
        reverse=True
    )

    return alerts


def render_trend_alert_markdown(
    alert_title,
    alerts,
    active=True
):

    lines = []

    lines.append(
        f"# {alert_title}"
    )
    lines.append("")
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append("")

    if not alerts:

        lines.append("## Status")
        lines.append("")
        lines.append(
            "- No sustained trend alert is active right now."
        )
        lines.append("")
        lines.append(
            "This note is refreshed every 30 minutes so the dashboard always has a current status."
        )
        return "\n".join(lines)

    lines.append("## Triggered Concepts")
    lines.append("")

    for alert in alerts[:5]:

        concept = alert["concept"]
        lines.append(
            f"- [[{concept}]]: {alert['reason']}"
        )
        lines.append(
            f"  - Support: {alert['source_count']} source notes in the last 24 hours."
        )

        if alert.get("last_seen"):

            lines.append(
                f"  - Last seen: {alert['last_seen']}"
            )

        if alert.get("sources"):

            lines.append("  - Supporting sources:")

            for source in alert["sources"]:

                lines.append(
                    f"    - {format_source_reference(source)}"
                )

    lines.append("")

    if active:

        lines.append(
            "## Why This Matters"
        )
        lines.append("")
        lines.append(
            "- The alert only fires when the concept appears repeatedly in the last 24 hours and is stronger than the prior 24-hour window."
        )
        lines.append(
            "- This is meant to catch sustained movement between 30-minute research runs, not a single spike."
        )

    return "\n".join(lines)


def build_current_trend_alert_summary(alerts):

    if not alerts:

        return "No sustained trend alert is active."

    top = alerts[0]

    return (
        f"{top['concept']} is trending with "
        f"{top['recent']} sightings in the last 24 hours "
        f"vs {top['previous']} before that."
    )


def source_cluster_key(record, matched_concepts):

    if matched_concepts:

        return " + ".join(
            matched_concepts[:2]
        )

    domain = record.get("domain", "").strip()

    if domain:

        return domain

    return "General"


def build_source_clusters(source_catalog, brief, ranked_sources=None):

    if ranked_sources is None:

        ranked_sources, _ = rank_sources_for_followup(
            source_catalog,
            brief
        )

    clusters = {}

    for item in ranked_sources:

        record = item["record"]
        matched_concepts = item.get("matched_concepts", [])
        key = source_cluster_key(
            record,
            matched_concepts
        )

        cluster = clusters.setdefault(
            key,
            {
                "key": key,
                "items": [],
                "score": 0.0,
                "concepts": set(),
                "domains": set()
            }
        )

        cluster["items"].append(item)
        cluster["score"] += float(item.get("score", 0.0))
        cluster["concepts"].update(matched_concepts)

        if record.get("domain"):

            cluster["domains"].add(record.get("domain"))

    cluster_list = []

    for cluster in clusters.values():

        concepts = sorted(
            [
                concept for concept in cluster["concepts"]
                if concept
            ]
        )
        domain = sorted(
            [
                value for value in cluster["domains"]
                if value
            ]
        )

        cluster_list.append(
            {
                "key": cluster["key"],
                "items": sorted(
                    cluster["items"],
                    key=lambda item: (
                        item["score"],
                        item["record"].get("retrieved_at", "")
                    ),
                    reverse=True
                ),
                "score": cluster["score"],
                "concepts": concepts,
                "domains": domain
            }
        )

    cluster_list.sort(
        key=lambda item: (
            item["score"],
            len(item["items"])
        ),
        reverse=True
    )

    return cluster_list


def render_source_clusters_markdown(cluster_list, max_clusters=4):

    lines = [
        "## Source Clusters",
        ""
    ]

    if not cluster_list:

        lines.append(
            "- No clusters found in the last 24 hours."
        )
        lines.append("")
        return "\n".join(lines)

    for cluster in cluster_list[:max_clusters]:

        cluster_title = cluster["key"]
        concept_suffix = ""

        if cluster["concepts"]:

            concept_suffix = (
                f" [concepts: {', '.join(cluster['concepts'])}]"
            )

        lines.append(
            f"### {cluster_title}{concept_suffix}"
        )
        lines.append("")

        for item in cluster["items"][:3]:

            record = item["record"]
            note_link = f"[[{record['note_title']}]]"
            article_link = f"[full article]({record.get('url', '')})"
            quality = item.get("quality", {})
            reason = item.get("reason", "")

            line = (
                f"- {note_link} · {article_link}"
            )

            if quality.get("label"):

                line += f" · quality: {quality['label']}"

            if reason:

                line += f" — {reason}"

            lines.append(line)

        lines.append("")

    return "\n".join(lines)


def render_source_clusters_html(cluster_list, max_clusters=4):

    if not cluster_list:

        return """
        <div class="empty-state">No clusters found in the last 24 hours.</div>
        """

    cards = []

    for cluster in cluster_list[:max_clusters]:

        concepts = ""
        if cluster["concepts"]:

            concepts = html_escape(
                ", ".join(cluster["concepts"])
            )

        cluster_items = []

        for item in cluster["items"][:3]:

            record = item["record"]
            note_title = html_escape(record.get("note_title", record.get("title", "Source")))
            note_uri = html_escape(record.get("note_uri", ""))
            url = html_escape(record.get("url", ""))
            quality = item.get("quality", {})
            reason = html_escape(item.get("reason", ""))

            line = (
                f"<div class='cluster-item'><a href=\"{note_uri}\">{note_title}</a> "
                f"(<a href=\"{url}\">full article</a>)"
            )

            if quality.get("label"):

                line += (
                    f" · quality: {html_escape(quality['label'])}"
                )

            if reason:

                line += f" — {reason}"

            line += "</div>"
            cluster_items.append(line)

        cards.append(
            f"""
            <div class="cluster-card">
              <div class="cluster-title">{html_escape(cluster['key'])}</div>
              {f'<div class="cluster-concepts">Concepts: {concepts}</div>' if concepts else ''}
              <div class="cluster-items">
                {''.join(cluster_items)}
              </div>
            </div>
            """
        )

    return "\n".join(cards)


GITHUB_TRENDING_WEEKLY_URL = "https://github.com/trending?since=weekly"
WEEKLY_TRENDING_CACHE_PATH = VAULT_PATH / "Logs" / "weekly_trending_repositories.json"


def strip_html_fragment(text):

    cleaned = re.sub(r"<[^>]+>", " ", str(text))
    cleaned = html_unescape(cleaned)

    return re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()


def load_weekly_trending_repository_cache():

    if not WEEKLY_TRENDING_CACHE_PATH.exists():

        return {}

    try:

        with open(
            WEEKLY_TRENDING_CACHE_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_weekly_trending_repository_cache(payload):

    try:

        WEEKLY_TRENDING_CACHE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            WEEKLY_TRENDING_CACHE_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                payload,
                f,
                indent=2
            )

    except Exception:

        pass


def fetch_weekly_trending_repositories(limit=8, refresh_hours=12):

    cache = load_weekly_trending_repository_cache()
    cached_at = parse_iso_datetime(
        cache.get("fetched_at", "")
    )

    if cached_at and datetime.now() - cached_at < timedelta(hours=refresh_hours):

        repositories = cache.get("repositories", [])

        if repositories:

            return repositories[:limit]

    try:

        response = requests.get(
            GITHUB_TRENDING_WEEKLY_URL,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Signal Garden)"
            }
        )
        response.raise_for_status()

    except Exception:

        return cache.get("repositories", [])[:limit]

    repo_cards = []

    for block in re.findall(
        r'<article class="Box-row">(.*?)</article>',
        response.text,
        re.S
    ):

        title_match = re.search(
            r'<h2[^>]*>.*?href="/([^"]+)"',
            block,
            re.S
        )

        if not title_match:

            continue

        slug = title_match.group(1).strip("/")

        if "/" not in slug:

            continue

        owner, repo = slug.split("/", 1)

        description_match = re.search(
            r'<p[^>]*>(.*?)</p>',
            block,
            re.S
        )

        language_match = re.search(
            r'itemprop="programmingLanguage">([^<]+)</span>',
            block,
            re.S
        )

        stars_match = re.search(
            r'([\d,]+)\s+stars this week',
            block,
            re.S
        )

        repo_cards.append(
            {
                "owner": owner,
                "repo": repo,
                "slug": slug,
                "title": f"{owner} / {repo}",
                "url": f"https://github.com/{slug}",
                "description": strip_html_fragment(
                    description_match.group(1)
                ) if description_match else "",
                "language": (
                    language_match.group(1).strip()
                    if language_match
                    else ""
                ),
                "weekly_stars": (
                    int(stars_match.group(1).replace(",", ""))
                    if stars_match
                    else 0
                )
            }
        )

    repo_cards.sort(
        key=lambda item: (
            item["weekly_stars"],
            item["title"]
        ),
        reverse=True
    )

    payload = {
        "fetched_at": datetime.now().isoformat(),
        "repositories": repo_cards
    }

    save_weekly_trending_repository_cache(payload)

    return repo_cards[:limit]


def detect_source_concepts(record):

    text_blob = " ".join(
        [
            record.get("title", ""),
            record.get("full_title", ""),
            record.get("note_title", ""),
            record.get("description", ""),
            record.get("content_excerpt", "")
        ]
    ).lower()

    return extract_matching_concepts(
        text_blob,
        sorted(REVERSE_CANONICAL_CONCEPTS.keys())
    )


def build_source_archive_catalog(source_records):

    archive = []

    for record in source_records:

        concepts = detect_source_concepts(record)
        quality = source_quality_profile(record)
        cluster = source_cluster_key(record, concepts)
        anchor = parse_iso_datetime(
            record.get("published", "")
        ) or parse_iso_datetime(
            record.get("retrieved_at", "")
        )

        archive.append(
            {
                **record,
                "archive_concepts": concepts,
                "quality": quality,
                "cluster": cluster,
                "source_day": (
                    anchor.date().isoformat()
                    if anchor else record.get("retrieved_at", "")[:10]
                )
            }
        )

    archive.sort(
        key=lambda item: (
            item.get("source_day", ""),
            item.get("retrieved_at", "")
        ),
        reverse=True
    )

    return archive


def archive_display_title(record):

    short_title = record.get("note_title") or record.get("title") or "Source"
    full_title = record.get("full_title") or record.get("title") or short_title

    return short_title, full_title


def render_source_archive_markdown(
    archive_title,
    archive_records,
    window_days=30
):

    lines = []

    lines.append(
        f"# {archive_title}"
    )
    lines.append("")
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append(
        f"Window: last {window_days} days"
    )
    lines.append("")

    total_sources = len(archive_records)
    unique_domains = sorted(
        {
            record.get("domain", "")
            for record in archive_records
            if record.get("domain", "")
        }
    )
    unique_concepts = sorted(
        {
            concept
            for record in archive_records
            for concept in record.get("archive_concepts", [])
        }
    )

    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Sources archived: {total_sources}")
    lines.append(f"- Domains represented: {len(unique_domains)}")
    lines.append(f"- Concepts matched: {len(unique_concepts)}")
    lines.append("")

    if unique_concepts:

        lines.append("### Quick Concept Filters")
        lines.append("")

        for concept in unique_concepts[:12]:

            concept_sources = [
                record for record in archive_records
                if concept in record.get("archive_concepts", [])
            ]

            lines.append(
                f"- [[{concept}]] ({len(concept_sources)} sources)"
            )

        lines.append("")

    if unique_domains:

        lines.append("### Quick Domain Filters")
        lines.append("")

        for domain in unique_domains[:12]:

            domain_sources = [
                record for record in archive_records
                if record.get("domain", "") == domain
            ]

            lines.append(
                f"- {domain} ({len(domain_sources)} sources)"
            )

        lines.append("")

    lines.append("## By Date")
    lines.append("")

    date_groups = {}

    for record in archive_records:

        date_groups.setdefault(
            record.get("source_day", "Unknown"),
            []
        ).append(record)

    for source_day in sorted(
        date_groups.keys(),
        reverse=True
    ):

        lines.append(f"### {source_day}")
        lines.append("")

        for record in date_groups[source_day]:

            short_title, full_title = archive_display_title(record)
            note_link = f"[[{short_title}]]"
            article_link = f"[full article]({record.get('url', '')})"
            concepts = record.get("archive_concepts", [])
            quality = record.get("quality", {})
            cluster = record.get("cluster", "")

            line = (
                f"- {note_link} · Full title: {full_title} · {article_link} · {record.get('domain', '')}"
            )

            if quality.get("label"):

                line += f" · quality: {quality['label']}"

            if cluster:

                line += f" · cluster: {cluster}"

            if concepts:

                line += f" · concepts: {', '.join(concepts)}"

            lines.append(line)

        lines.append("")

    if unique_concepts:

        lines.append("## By Concept")
        lines.append("")

        for concept in unique_concepts[:15]:

            lines.append(f"### {concept}")
            lines.append("")

            concept_records = [
                record for record in archive_records
                if concept in record.get("archive_concepts", [])
            ]

            if not concept_records:

                lines.append("- No matching sources.")
                lines.append("")
                continue

            for record in concept_records[:12]:

                short_title, full_title = archive_display_title(record)
                note_link = f"[[{short_title}]]"
                article_link = f"[full article]({record.get('url', '')})"
                lines.append(
                    f"- {note_link} · Full title: {full_title} · {article_link} · {record.get('domain', '')} · {record.get('source_day', '')}"
                )

            lines.append("")

    if unique_domains:

        lines.append("## By Domain")
        lines.append("")

        for domain in unique_domains[:15]:

            lines.append(f"### {domain}")
            lines.append("")

            domain_records = [
                record for record in archive_records
                if record.get("domain", "") == domain
            ]

            if not domain_records:

                lines.append("- No matching sources.")
                lines.append("")
                continue

            for record in domain_records[:12]:

                short_title, full_title = archive_display_title(record)
                note_link = f"[[{short_title}]]"
                article_link = f"[full article]({record.get('url', '')})"
                concepts = record.get("archive_concepts", [])
                concept_text = (
                    f" · concepts: {', '.join(concepts)}"
                    if concepts else ""
                )

                lines.append(
                    f"- {note_link} · Full title: {full_title} · {article_link} · {record.get('source_day', '')}{concept_text}"
                )

            lines.append("")

    lines.append("## Source Index")
    lines.append("")

    for record in archive_records:

        short_title, full_title = archive_display_title(record)
        note_link = f"[[{short_title}]]"
        article_link = f"[full article]({record.get('url', '')})"
        lines.append(
            f"- {record.get('source_day', '')} · {record.get('domain', '')} · {note_link} · Full title: {full_title} · {article_link}"
        )

    return "\n".join(lines)


def score_source_for_digging_deeper(
    record,
    highlight_lookup,
    quality_profile=None,
    topic_coverage_lookup=None
):

    score = 0

    if quality_profile is None:

        quality_profile = source_quality_profile(record)

    score += quality_profile.get("score", 0.0)

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

    if topic_coverage_lookup:

        topic_key = normalize_topic_label(
            record.get("topic", "")
        )

        topic_count = topic_coverage_lookup.get(topic_key)

        if topic_count is not None:

            if topic_count <= 1:

                score += 4
            elif topic_count == 2:

                score += 3
            elif topic_count == 3:

                score += 2
            elif topic_count == 4:

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

    return score, reason, matched_concepts, quality_profile


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

    topic_coverage_lookup = {
        normalize_topic_label(item["topic"]): item["count"]
        for item in brief.get("topic_coverage", [])
        if item.get("topic")
    }

    ranked_sources = []

    for record in source_catalog:

        score, reason, matched_concepts, quality_profile = score_source_for_digging_deeper(
            record,
            highlight_lookup,
            topic_coverage_lookup
        )

        ranked_sources.append(
            {
                "record": record,
                "score": score,
                "reason": reason,
                "matched_concepts": matched_concepts,
                "tier": label_source_tier(score),
                "quality": quality_profile,
                "cluster": source_cluster_key(
                    record,
                    matched_concepts
                )
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


def select_next_recommended_reading(
    ranked_sources,
    limit=3,
    topic_coverage=None
):

    if not ranked_sources:

        return []

    selected = []
    selected_ids = set()
    emerging_topics = {
        normalize_topic_label(item["topic"])
        for item in build_new_area_coverage(topic_coverage or [])
        if item.get("topic")
    }

    if emerging_topics:

        emerging_item = next(
            (
                item for item in ranked_sources
                if normalize_topic_label(
                    item["record"].get("topic", "")
                ) in emerging_topics
                and item["record"]["id"] not in selected_ids
            ),
            None
        )

        if emerging_item:

            emerging_item = dict(emerging_item)
            emerging_item["focus_label"] = "New Area"
            selected.append(emerging_item)
            selected_ids.add(emerging_item["record"]["id"])

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
        quality = item.get("quality", {})
        cluster = item.get("cluster", "")
        tier_label = item.get("focus_label", item["tier"])

        line = (
            f"- **{tier_label}**: {note_link} · {article_link}"
        )

        if reason:

            line += f" — {reason}"

        if matched_concepts:

            line += (
                f" [concepts: {', '.join(matched_concepts)}]"
            )

        if cluster:

            line += f" [cluster: {cluster}]"

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
        quality = item.get("quality", {})
        cluster = item.get("cluster", "")
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
              {f'<div class="item-meta">Quality: {html_escape(quality.get("label", ""))}</div>' if quality.get("label") else ''}
              {f'<div class="item-meta">Cluster: {html_escape(cluster)}</div>' if cluster else ''}
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
    topic_coverage,
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

    platform_balance = build_mobile_platform_balance(
        source_catalog
    )

    developments = brief.get(
        "key_developments",
        []
    )

    themes = brief.get(
        "emerging_themes",
        []
    )

    topic_coverage = topic_coverage or build_topic_coverage(
        source_catalog
    )

    brief_for_ranking = dict(brief)
    brief_for_ranking["topic_coverage"] = topic_coverage

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        brief_for_ranking
    )

    next_recommended = select_next_recommended_reading(
        ranked_sources,
        topic_coverage=topic_coverage
    )

    next_recommended_html = render_next_recommended_reading_html(
        next_recommended
    )

    source_clusters = build_source_clusters(
        source_catalog,
        brief_for_ranking,
        ranked_sources
    )

    source_clusters_html = render_source_clusters_html(
        source_clusters
    )

    highlights = brief.get(
        "source_highlights",
        []
    )

    summary_html = "".join(
        f"<li>{html_escape(point)}</li>"
        for point in summary_points
    ) or "<li>No summary points were generated.</li>"

    platform_balance = build_mobile_platform_balance(
        source_catalog
    )

    platform_balance_html = ""

    if platform_balance:

        cards = []

        for label in [
            "Android",
            "iOS",
            "Mobile umbrella",
            "Shared mobile"
        ]:

            count = platform_balance.get(label)

            if not count:

                continue

            cards.append(
                f"""
                <div class="item-card item-card-accent">
                  <div class="item-text">{html_escape(label)}</div>
                  <div class="item-meta">{count} source notes</div>
                </div>
                """
            )

        platform_balance_html = "\n".join(cards)

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

    active_areas_html = ""

    if topic_coverage:

        cards = []

        for item in topic_coverage:

            domain_count = len(
                [
                    domain
                    for domain in item.get("domains", set())
                    if domain
                ]
            )

            cards.append(
                f"""
                <div class="item-card item-card-accent">
                  <div class="item-text">{html_escape(item['topic'])}</div>
                  <div class="item-meta">{item['count']} source notes{f' across {domain_count} domains' if domain_count else ''}</div>
                </div>
                """
            )

        active_areas_html = "\n".join(cards)
    else:
        active_areas_html = """
        <div class="empty-state">No active areas were found in the last 24 hours.</div>
        """

    new_areas_html = ""

    emerging_areas = build_new_area_coverage(
        topic_coverage
    )

    if emerging_areas:

        cards = []

        for item in emerging_areas:

            domain_count = len(
                [
                    domain
                    for domain in item.get("domains", set())
                    if domain
                ]
            )

            cards.append(
                f"""
                <div class="item-card">
                  <div class="item-text">{html_escape(item['topic'])}</div>
                  <div class="item-meta">{item['count']} source notes{f' across {domain_count} domains' if domain_count else ''}</div>
                </div>
                """
            )

        new_areas_html = "\n".join(cards)
    else:
        new_areas_html = """
        <div class="empty-state">No new areas were identified in the last 24 hours.</div>
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
    .report-headline {{
      margin-top: 8px;
      font-size: 30px;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: -0.02em;
      line-height: 1.08;
    }}
    .report-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 12px 22px 0;
    }}
    .report-nav a {{
      display: inline-flex;
      align-items: center;
      padding: 7px 11px;
      border-radius: 999px;
      background: rgba(55, 91, 74, 0.08);
      color: var(--accent);
      font-size: 12px;
      text-decoration: none;
      border: 1px solid rgba(55, 91, 74, 0.14);
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
    .section-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 0 0 12px;
    }}
    .section h2 {{
      margin: 0;
      font-size: 20px;
    }}
    .section-back {{
      display: inline-flex;
      align-items: center;
      justify-content: flex-end;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(55, 91, 74, 0.08);
      border: 1px solid rgba(55, 91, 74, 0.14);
      color: var(--accent);
      font-size: 11px;
      text-decoration: none;
      white-space: nowrap;
      flex: 0 0 auto;
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
    .cluster-card {{
      background: rgba(244, 239, 230, 0.72);
      border: 1px solid rgba(55, 91, 74, 0.12);
      border-radius: 16px;
      padding: 14px;
    }}
    .cluster-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--accent);
    }}
    .cluster-concepts {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .cluster-items {{
      margin-top: 10px;
      display: grid;
      gap: 8px;
    }}
    .cluster-item {{
      font-size: 13px;
      line-height: 1.4;
      color: var(--ink);
    }}
    .cluster-item a {{
      color: var(--accent);
      text-decoration: none;
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
    <div class="shell" id="top">
      <div class="header-art">
        <img src="{html_escape(header_image_uri)}" alt="Signal Garden header artwork" />
        <div class="header-date">{html_escape(published_date_text)}</div>
      </div>
      <div class="report-strip">
        <div class="eyebrow">Signal Garden Daily Brief</div>
        <div class="report-headline">{headline}</div>
        <div class="subhead">Generated {html_escape(datetime.now().isoformat())} · Topic: {html_escape(format_topic_display(topic))}</div>
      </div>
      <div class="report-nav" id="top-nav">
        <a href="#summary">Executive Summary</a>
        <a href="#next-reading">Next Recommended Reading</a>
        <a href="#developments">Key Developments</a>
        <a href="#themes">Emerging Themes</a>
        <a href="#clusters">Source Clusters</a>
        <a href="#sources">Source Appendix</a>
        <a href="#deeper">Digging Deeper</a>
      </div>
      <div class="meta-row">
        <div class="stat"><span class="stat-label">Sources</span><span class="stat-value">{stats['sources']}</span></div>
        <div class="stat"><span class="stat-label">Developments</span><span class="stat-value">{stats['developments']}</span></div>
        <div class="stat"><span class="stat-label">Themes</span><span class="stat-value">{stats['themes']}</span></div>
        <div class="stat"><span class="stat-label">Concepts</span><span class="stat-value">{stats['concepts']}</span></div>
      </div>
      <div class="content">
        <div class="section" id="summary">
          <div class="section-header">
            <h2>Executive Summary</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <ul>
            {summary_html}
          </ul>
        </div>
        <div class="section" id="active-areas">
          <div class="section-header">
            <h2>Active Areas</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {active_areas_html}
          </div>
        </div>
        <div class="section" id="new-areas">
          <div class="section-header">
            <h2>New Areas</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {new_areas_html}
          </div>
        </div>
        {f'<div class="section" id="platform"><div class="section-header"><h2>Platform Balance</h2><a class="section-back" href="#top-nav">Back to navigation</a></div><div class="item-grid">{platform_balance_html}</div></div>' if platform_balance_html else ''}
        <div class="section" id="next-reading">
          <div class="section-header">
            <h2>Next Recommended Reading</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {next_recommended_html}
          </div>
        </div>
        <div class="section" id="developments">
          <div class="section-header">
            <h2>Key Developments</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {developments_html}
          </div>
        </div>
        <div class="section" id="themes">
          <div class="section-header">
            <h2>Emerging Themes</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {themes_html}
          </div>
        </div>
        <div class="section" id="clusters">
          <div class="section-header">
            <h2>Source Clusters</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="item-grid">
            {source_clusters_html}
          </div>
        </div>
        <div class="section" id="sources">
          <div class="section-header">
            <h2>Source Appendix</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
          <div class="source-grid">
            {source_cards_html}
          </div>
        </div>
        <div class="section" id="deeper">
          <div class="section-header">
            <h2>Digging Deeper</h2>
            <a class="section-back" href="#top-nav">Back to navigation</a>
          </div>
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
    concepts,
    topic_coverage=None
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

    coverage_text = "\n".join(
        format_topic_coverage_lines(
            topic_coverage or []
        )
    )

    new_area_text = "\n".join(
        format_new_area_lines(
            topic_coverage or []
        )
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

This is a multi-area daily overview, not a single-topic report. If the provided sources span multiple topics, summarize the active areas together and call out the newest or fastest-moving areas explicitly.
Prefer newly emerging or low-count areas when you choose what to emphasize. Recurring areas can stay in the report, but they should not crowd out newer topics if both are present.

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

ACTIVE AREAS:
{coverage_text if coverage_text else "None"}

NEW AREAS:
{new_area_text if new_area_text else "None"}

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
                "Signal Garden reviewed the last 24 hours of source notes and updated semantic memory across the active areas."
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
    source_catalog,
    topic_coverage=None
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
        f"Topic: [[{format_topic_display(topic)}]]"
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

    summary_points = brief.get(
        "summary_points",
        []
    )

    platform_balance = build_mobile_platform_balance(
        source_catalog
    )

    topic_coverage = topic_coverage or build_topic_coverage(
        source_catalog
    )

    brief_for_ranking = dict(brief)
    brief_for_ranking["topic_coverage"] = topic_coverage

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        brief_for_ranking
    )

    next_recommended = select_next_recommended_reading(
        ranked_sources,
        topic_coverage=topic_coverage
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

    lines.append("### Active Areas")
    lines.append("")
    lines.extend(
        format_topic_coverage_lines(
            topic_coverage
        )
    )
    lines.append("")

    lines.append("### New Areas")
    lines.append("")
    lines.extend(
        format_new_area_lines(
            topic_coverage
        )
    )
    lines.append("")

    if platform_balance:

        lines.append("### Platform Balance")
        lines.append("")

        for label in [
            "Android",
            "iOS",
            "Mobile umbrella",
            "Shared mobile"
        ]:

            count = platform_balance.get(label)

            if not count:

                continue

            lines.append(f"- {label}: {count} source notes")

        lines.append("")

    lines.extend(
        render_next_recommended_reading_markdown(
            next_recommended
        ).splitlines()
    )

    source_clusters = build_source_clusters(
        source_catalog,
        brief_for_ranking,
        ranked_sources
    )

    lines.extend(
        render_source_clusters_markdown(
            source_clusters
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

    topic_coverage = build_topic_coverage(
        source_catalog
    )

    brief_for_ranking = dict(brief)
    brief_for_ranking["topic_coverage"] = topic_coverage

    ranked_sources, highlight_lookup = rank_sources_for_followup(
        source_catalog,
        brief_for_ranking
    )

    lines = []

    lines.append(
        f"# {deeper_note_title}"
    )
    lines.append("")
    lines.append(
        f"Topic: [[{format_topic_display(topic)}]]"
    )
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append("")

    next_recommended = select_next_recommended_reading(
        ranked_sources,
        topic_coverage=topic_coverage
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
            quality = item.get("quality", {})
            cluster = item.get("cluster", "")
            note_link = f"[[{record['note_title']}]]"
            article_link = f"[full article]({record.get('url', '')})"

            line = (
                f"- {note_link} · {article_link}"
            )

            if quality.get("label"):

                line += (
                    f" · quality: {quality['label']}"
                )

            if cluster:

                line += f" · cluster: {cluster}"

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


def generate_weekly_rollup(
    source_catalog,
    concepts
):

    if not source_catalog:

        return {
            "headline": "Weekly rollup",
            "summary_points": [
                "No source notes were found in the last 7 days."
            ],
            "trend_points": [],
            "source_highlights": []
        }

    ranked_sources, _ = rank_sources_for_followup(
        source_catalog,
        {
            "source_highlights": [],
            "topic_coverage": build_topic_coverage(source_catalog)
        }
    )

    clusters = build_source_clusters(
        source_catalog,
        {
            "source_highlights": [],
            "topic_coverage": build_topic_coverage(source_catalog)
        },
        ranked_sources
    )

    trending_repositories = fetch_weekly_trending_repositories()

    trend_rows = sorted(
        CONCEPT_STATE.items(),
        key=lambda item: (
            concept_trend_delta(item[1])["delta"],
            concept_momentum(item[1])
        ),
        reverse=True
    )

    top_momentum = sorted(
        CONCEPT_STATE.items(),
        key=lambda item: (
            concept_momentum(item[1]),
            item[1].get("seen_count", 0)
        ),
        reverse=True
    )

    summary_points = [
        f"Reviewed {len(source_catalog)} source notes from the last 7 days.",
    ]

    if top_momentum:

        summary_points.append(
            "Top momentum concepts: "
            + ", ".join(
                concept for concept, _ in top_momentum[:3]
            )
            + "."
        )

    if trend_rows:

        rising = [
            concept for concept, record in trend_rows
            if concept_trend_delta(record)["delta"] > 0
        ][:3]

        if rising:

            summary_points.append(
                "Fastest rising concepts: "
                + ", ".join(rising)
                + "."
            )

    if clusters:

        summary_points.append(
            f"Most active source cluster: {clusters[0]['key']} "
            f"with {len(clusters[0]['items'])} notes."
        )

    if trending_repositories:

        top_repo = trending_repositories[0]
        summary_points.append(
            "Weekly trending repository watch: "
            f"{top_repo['title']} with {top_repo['weekly_stars']} stars this week."
        )

    trend_points = []

    for concept, record in trend_rows[:5]:

        trend = concept_trend_delta(record)
        trend_points.append(
            {
                "text": (
                    f"{concept}: {trend['recent']} sightings in the last 7 days "
                    f"vs {trend['previous']} in the prior week (delta {trend['delta']})."
                ),
                "concept": concept
            }
        )

    source_highlights = []

    for item in ranked_sources[:8]:

        source_highlights.append(
            {
                "source_id": item["record"]["id"],
                "reason": (
                    f"Weekly priority in {item['tier']} tier "
                    f"({item.get('quality', {}).get('label', 'Standard')} quality)."
                )
            }
        )

    return {
        "headline": "Weekly rollup",
        "summary_points": summary_points,
        "trend_points": trend_points,
        "source_highlights": source_highlights,
        "clusters": clusters,
        "trending_repositories": trending_repositories
    }


def render_weekly_rollup_markdown(
    week_title,
    rollup,
    source_catalog
):

    lines = []

    lines.append(
        f"# {week_title}"
    )
    lines.append("")
    lines.append(
        f"Generated: {datetime.now().isoformat()}"
    )
    lines.append("")
    lines.append(
        f"## {rollup.get('headline', 'Weekly rollup')}"
    )
    lines.append("")

    lines.append("### Weekly Summary")
    lines.append("")

    for point in rollup.get("summary_points", []) or []:

        lines.append(f"- {point}")

    lines.append("")

    trend_points = rollup.get("trend_points", [])

    if trend_points:

        lines.append("### Trend Velocity")
        lines.append("")

        for item in trend_points:

            lines.append(f"- {item['text']}")

        lines.append("")

    trending_repositories = rollup.get("trending_repositories", [])

    if trending_repositories:

        lines.append("### Weekly Trending Repositories")
        lines.append("")

        for repo in trending_repositories[:8]:

            repo_link = f"[{repo['title']}]({repo['url']})"
            meta_bits = []

            if repo.get("language"):

                meta_bits.append(repo["language"])

            if repo.get("weekly_stars"):

                meta_bits.append(
                    f"{repo['weekly_stars']} stars this week"
                )

            meta = f" ({' · '.join(meta_bits)})" if meta_bits else ""
            description = repo.get("description", "").strip()
            description_text = f" — {description}" if description else ""

            lines.append(
                f"- {repo_link}{meta}{description_text}"
            )

        lines.append("")

    clusters = rollup.get("clusters", [])

    if clusters:

        lines.append(
            render_source_clusters_markdown(
                clusters,
                max_clusters=5
            ).rstrip()
        )
        lines.append("")

    next_reading = select_next_recommended_reading(
        rank_sources_for_followup(
            source_catalog,
            {
                "source_highlights": rollup.get("source_highlights", []),
                "topic_coverage": build_topic_coverage(source_catalog)
            }
        )[0],
        topic_coverage=build_topic_coverage(source_catalog)
    )

    lines.append(
        render_next_recommended_reading_markdown(
            next_reading
        ).rstrip()
    )
    lines.append("")

    lines.append("### Source Index")
    lines.append("")

    for record in source_catalog:

        lines.append(
            f"- {record['id']}: {format_source_reference(record)}"
        )

    return "\n".join(lines)

# =========================================================
# SMART TOPIC SELECTION
# =========================================================

def choose_research_topic():

    prioritized_queue = prioritize_research_queue(
        RESEARCH_QUEUE
    )

    if prioritized_queue != RESEARCH_QUEUE:

        RESEARCH_QUEUE[:] = prioritized_queue

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


def prioritize_research_queue(queue):
    priority_labels = {
        normalize_topic_label(topic)
        for topic in PRIORITY_TOPICS
    }

    priority_labels.update(
        normalize_topic_label(topic)
        for topic in OCR_SCOPE_TOPICS
    )

    seen = set()
    prioritized = []

    for topic in queue:

        topic_key = normalize_topic_label(topic)

        if topic_key in seen:

            continue

        seen.add(topic_key)

        priority = 0 if topic_key in priority_labels else 1

        prioritized.append(
            {
                "topic": topic,
                "priority": priority
            }
        )

    prioritized.sort(
        key=lambda item: (
            item["priority"],
            item["topic"].lower()
        )
    )

    return [
        item["topic"]
        for item in prioritized
    ]

# =========================================================
# DASHBOARD
# =========================================================

def generate_dashboard(
    latest_archive_title=None,
    latest_alert_title=None,
    latest_alert_summary=None
):

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
    # ACTIVE ALERTS
    # =====================================

    dashboard += (
        "\n## Active Alerts\n\n"
    )

    if latest_alert_title:

        dashboard += (
            f"- [[{latest_alert_title}]]\n"
        )

        if latest_alert_summary:

            dashboard += (
                f"- {latest_alert_summary}\n"
            )

    else:

        dashboard += (
            "- No active alert note yet\n"
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

            trend = concept_trend_delta(record)
            trend_label = (
                f"+{trend['delta']}" if trend["delta"] > 0 else str(trend["delta"])
            )

            dashboard += (
                f"- [[{concept}]] "
                f"(score {concept_momentum(record):.2f}, "
                f"seen {record.get('seen_count', 0)}, "
                f"velocity {concept_velocity(record)}, "
                f"trend {trend_label})\n"
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

            trend = concept_trend_delta(record)

            dashboard += (
                f"- [[{concept}]] "
                f"(last 7d {concept_velocity(record)}, "
                f"delta {trend['delta']}, "
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
    # RECENT SOURCE CLUSTERS
    # =====================================

    dashboard += (
        "\n## Recent Source Clusters\n\n"
    )

    recent_source_notes = collect_recent_source_notes(
        hours=168
    )

    recent_source_catalog = build_source_catalog(
        recent_source_notes
    )

    recent_source_clusters = build_source_clusters(
        recent_source_catalog,
        {
            "source_highlights": []
        }
    )

    if recent_source_clusters:

        for cluster in recent_source_clusters[:5]:

            concept_suffix = ""

            if cluster["concepts"]:

                concept_suffix = (
                    f" [concepts: {', '.join(cluster['concepts'])}]"
                )

            dashboard += (
                f"- {cluster['key']} "
                f"({len(cluster['items'])} sources)"
                f"{concept_suffix}\n"
            )

    else:

        dashboard += (
            "- No source clusters found yet\n"
        )

    # =====================================
    # SOURCE ARCHIVE
    # =====================================

    dashboard += (
        "\n## Source Archive\n\n"
    )

    if latest_archive_title:

        dashboard += (
            f"- [[{latest_archive_title}]]\n"
        )

    else:

        dashboard += (
            "- No archive generated yet\n"
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

    full_title = result["title"][:240]
    source_title = normalize_note_title(
        full_title,
        max_length=72
    )

    source_records.append(
        {
            "title": source_title,
            "full_title": full_title,
            "url": result["url"],
            "domain": domain,
            "retrieved_at": datetime.now().isoformat(),
            "topic": TOPIC,
            "content": article,
            "note_title": source_title
        }
    )

    vault.save_note(

        "Sources",

        source_title,

        article,

        tags=["source"],

        metadata={
            "url": result["url"],
            "domain": domain,
            "retrieved_at": datetime.now().isoformat(),
            "topic": TOPIC,
            "source_type": "web",
            "title": source_title,
            "full_title": full_title
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

daily_scope_label = "Daily Overview"

if not recent_source_notes:

    recent_source_notes = collect_recent_source_notes(
        hours=24,
        topic=TOPIC
    )
    daily_scope_label = TOPIC

source_catalog = build_source_catalog(
    recent_source_notes
)

recent_source_digest = build_recent_source_digest(
    source_catalog
)

topic_coverage = build_topic_coverage(
    source_catalog
)

digging_deeper_title = f"Digging Deeper - {today_stamp}"

daily_brief = generate_daily_brief(
    daily_scope_label,
    source_catalog,
    recent_source_digest,
    concepts,
    topic_coverage
)

daily_brief_content = render_daily_brief(
    daily_scope_label,
    daily_brief,
    source_catalog,
    topic_coverage
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
        "topic": daily_scope_label,
        "generated_at": datetime.now().isoformat(),
        "source_count": len(source_catalog)
    }
)

digging_deeper_content = render_digging_deeper_markdown(
    daily_scope_label,
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
        "topic": daily_scope_label,
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
    daily_scope_label,
    daily_brief,
    source_catalog,
    concepts,
    topic_coverage,
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

    maybe_email_daily_pdf(
        pdf_path,
        daily_scope_label,
        daily_brief,
        source_catalog,
        digging_deeper_title,
        (
            vault.path("Daily", digging_deeper_title)
            .resolve()
            .as_uri()
        ),
        today_stamp
    )
else:

    print(
        f"Daily PDF export skipped or failed for: {pdf_path}"
    )

# =========================================================
# WEEKLY ROLLUP
# =========================================================

weekly_source_notes = collect_recent_source_notes(
    hours=168
)

weekly_source_catalog = build_source_catalog(
    weekly_source_notes
)

weekly_rollup = generate_weekly_rollup(
    weekly_source_catalog,
    concepts
)

weekly_rollup_title = f"Weekly Rollup - {today_stamp}"

weekly_rollup_content = render_weekly_rollup_markdown(
    weekly_rollup_title,
    weekly_rollup,
    weekly_source_catalog
)

vault.save_note(

    "Weekly",

    weekly_rollup_title,

    weekly_rollup_content,

    tags=[
        "weekly",
        "rollup"
    ],
    overwrite=True,

    metadata={
        "topic": TOPIC,
        "generated_at": datetime.now().isoformat(),
        "source_count": len(weekly_source_catalog)
    }
)

# =========================================================
# SOURCE ARCHIVE
# =========================================================

archive_source_notes = collect_recent_source_notes(
    hours=24 * 30
)

archive_source_catalog = build_source_catalog(
    archive_source_notes
)

archive_source_catalog = build_source_archive_catalog(
    archive_source_catalog
)

source_archive_title = f"Source Archive - {today_stamp}"

source_archive_content = render_source_archive_markdown(
    source_archive_title,
    archive_source_catalog,
    window_days=30
)

vault.save_note(

    "Archive",

    source_archive_title,

    source_archive_content,

    tags=[
        "archive",
        "sources"
    ],
    overwrite=True,

    metadata={
        "generated_at": datetime.now().isoformat(),
        "source_count": len(archive_source_catalog),
        "window_days": 30
    }
)

LATEST_SOURCE_ARCHIVE_TITLE = source_archive_title

# =========================================================
# INTERIM TREND ALERTS
# =========================================================

trend_alerts = detect_sustained_trend_alerts(
    archive_source_catalog
)

trend_alert_title = f"Current Trend Alert"
trend_alert_summary = build_current_trend_alert_summary(
    trend_alerts
)
trend_alert_content = render_trend_alert_markdown(
    trend_alert_title,
    trend_alerts
)

vault.save_note(

    "Alerts",

    trend_alert_title,

    trend_alert_content,

    tags=[
        "alert",
        "trend"
    ],
    overwrite=True,

    metadata={
        "generated_at": datetime.now().isoformat(),
        "active_alerts": len(trend_alerts),
        "alert_summary": trend_alert_summary
    }
)

if trend_alerts:

    history_stamp = datetime.now().strftime("%Y-%m-%d %H%M")
    history_title = f"Trend Alert - {history_stamp}"
    history_content = render_trend_alert_markdown(
        history_title,
        trend_alerts
    )

    vault.save_note(

        "Alerts",

        history_title,

        history_content,

        tags=[
            "alert",
            "trend"
        ],
        overwrite=True,

        metadata={
            "generated_at": datetime.now().isoformat(),
            "active_alerts": len(trend_alerts),
            "alert_summary": trend_alert_summary
        }
    )

# =========================================================
# GENERATE DASHBOARD
# =========================================================

generate_dashboard(
    source_archive_title,
    trend_alert_title,
    trend_alert_summary
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
# COMPLETE
# =========================================================

print("\nResearch completed successfully.")
print("\nObsidian vault updated.")

print("\nResearch Queue:")
print(RESEARCH_QUEUE)

print("\nConcept Frequencies:")
print(CONCEPT_FREQ)
