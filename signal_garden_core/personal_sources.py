from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import xml.etree.ElementTree as ET

import requests


def normalize_personal_source(item, default_kind="url"):

    if isinstance(item, str):

        return {
            "type": default_kind,
            "url": item.strip(),
            "title": "",
            "topic": "",
            "source": "personal_sources"
        }

    if not isinstance(item, dict):

        return None

    source_type = str(
        item.get("type") or item.get("kind") or default_kind
    ).strip().lower()

    return {
        "type": source_type,
        "url": str(item.get("url") or item.get("feed_url") or "").strip(),
        "feed_url": str(item.get("feed_url") or item.get("url") or "").strip(),
        "title": str(item.get("title") or item.get("name") or "").strip(),
        "topic": str(item.get("topic") or "").strip(),
        "reason": str(item.get("reason") or "").strip(),
        "source": str(item.get("source") or "personal_sources").strip(),
        "handle": str(item.get("handle") or item.get("profile") or "").strip()
    }


def personal_sources_from_config(config):

    payload = config.get("personal_sources", [])
    entries = []

    if isinstance(payload, list):

        for item in payload:

            normalized = normalize_personal_source(item)

            if normalized:

                entries.append(normalized)

    if isinstance(payload, dict):

        for key, default_kind in [
            ("rss_feeds", "rss"),
            ("atom_feeds", "rss"),
            ("blog_urls", "url"),
            ("urls", "url"),
            ("x_feeds", "x"),
            ("x_profiles", "x")
        ]:

            for item in payload.get(key, []) or []:

                normalized = normalize_personal_source(
                    item,
                    default_kind=default_kind
                )

                if normalized:

                    entries.append(normalized)

    return entries


def personal_sources_from_inbox(inbox_dir):

    path = Path(inbox_dir) / "personal_sources.json"

    if not path.exists():

        return []

    try:

        payload = json.loads(
            path.read_text(encoding="utf-8")
        )

    except Exception:

        return []

    if isinstance(payload, dict):

        payload = payload.get("sources", payload.get("personal_sources", []))

    entries = []

    if isinstance(payload, list):

        for item in payload:

            normalized = normalize_personal_source(item)

            if normalized:

                normalized["source"] = "Inbox/personal_sources.json"
                entries.append(normalized)

    return entries


def load_personal_sources(config, inbox_dir):

    entries = []
    seen_keys = set()

    for item in (
        personal_sources_from_config(config) +
        personal_sources_from_inbox(inbox_dir)
    ):

        key = (
            item.get("type", ""),
            item.get("url", ""),
            item.get("feed_url", ""),
            item.get("handle", "")
        )

        if key in seen_keys:

            continue

        seen_keys.add(key)
        entries.append(item)

    return entries


def tag_text(element, local_name):

    for child in list(element):

        if child.tag.split("}")[-1] == local_name:

            return "".join(child.itertext()).strip()

    return ""


def atom_link(entry):

    for child in list(entry):

        if child.tag.split("}")[-1] != "link":

            continue

        href = child.attrib.get("href", "").strip()

        if href:

            return href

    return ""


def clean_feed_text(value):

    return re.sub(
        r"\s+",
        " ",
        re.sub(r"<[^>]+>", " ", value or "")
    ).strip()


def parse_feed_items(xml_text, source, limit=5):

    try:

        root = ET.fromstring(xml_text)

    except ET.ParseError:

        return []

    root_name = root.tag.split("}")[-1].lower()
    items = []

    if root_name == "feed":

        feed_title = tag_text(root, "title") or source.get("title", "")

        for entry in root.findall(".//{*}entry"):

            url = atom_link(entry)

            if not url:

                continue

            title = tag_text(entry, "title") or url
            published = (
                tag_text(entry, "published") or
                tag_text(entry, "updated")
            )
            description = (
                tag_text(entry, "summary") or
                tag_text(entry, "content")
            )

            items.append(
                {
                    "title": clean_feed_text(title),
                    "url": url,
                    "published": published,
                    "description": clean_feed_text(description),
                    "feed_title": feed_title
                }
            )

            if len(items) >= limit:

                break

        return items

    channel = root.find("channel")
    feed_title = (
        tag_text(channel, "title")
        if channel is not None else source.get("title", "")
    )

    for item in root.findall(".//item"):

        url = tag_text(item, "link")

        if not url:

            guid = tag_text(item, "guid")
            url = guid if guid.startswith("http") else ""

        if not url:

            continue

        title = tag_text(item, "title") or url
        published = (
            tag_text(item, "pubDate") or
            tag_text(item, "published") or
            tag_text(item, "updated")
        )
        description = (
            tag_text(item, "description") or
            tag_text(item, "summary") or
            tag_text(item, "content")
        )

        items.append(
            {
                "title": clean_feed_text(title),
                "url": url,
                "published": published,
                "description": clean_feed_text(description),
                "feed_title": feed_title
            }
        )

        if len(items) >= limit:

            break

    return items


def source_is_feed(source):

    source_type = source.get("type", "")

    return source_type in {
        "rss",
        "atom",
        "feed",
        "x"
    } and bool(source.get("feed_url") or source.get("url"))


def source_is_direct_url(source):

    return source.get("type", "") in {
        "url",
        "blog",
        "article",
        "x_url",
        "tweet"
    } and bool(source.get("url"))


def fetch_personal_source_candidates(sources, feed_item_limit=5, timeout=30):

    candidates = []
    skipped = []

    for source in sources:

        source_type = source.get("type", "")

        if source_is_feed(source):

            feed_url = source.get("feed_url") or source.get("url")

            try:

                response = requests.get(feed_url, timeout=timeout)
                response.raise_for_status()

            except Exception as exc:

                skipped.append(
                    {
                        "source": source,
                        "reason": str(exc)
                    }
                )
                continue

            for item in parse_feed_items(
                response.text,
                source,
                limit=feed_item_limit
            ):

                item.update(
                    {
                        "source_kind": source_type,
                        "source_label": source.get("title") or item.get("feed_title", ""),
                        "topic": source.get("topic", ""),
                        "reason": source.get("reason", ""),
                        "configured_source": source.get("source", "personal_sources")
                    }
                )
                candidates.append(item)

            continue

        if source_is_direct_url(source):

            url = source.get("url", "")
            candidates.append(
                {
                    "title": source.get("title") or url,
                    "url": url,
                    "published": "",
                    "description": "",
                    "feed_title": "",
                    "source_kind": source_type,
                    "source_label": source.get("title", ""),
                    "topic": source.get("topic", ""),
                    "reason": source.get("reason", ""),
                    "configured_source": source.get("source", "personal_sources")
                }
            )
            continue

        if source_type == "x" and source.get("handle"):

            skipped.append(
                {
                    "source": source,
                    "reason": "X profiles require a configured feed_url, API bridge, or direct tweet URL."
                }
            )

    return candidates, skipped


def candidate_domain(candidate):

    return urlparse(candidate.get("url", "")).netloc.replace("www.", "")


def personal_source_state_key(candidate):

    return candidate.get("url", "").strip()


def personal_source_note_body(content, candidate):

    description = candidate.get("description", "").strip()

    if content:

        return content

    lines = [
        candidate.get("title", "Personal source"),
        "",
        candidate.get("url", "")
    ]

    if description:

        lines.extend(
            [
                "",
                description
            ]
        )

    return "\n".join(lines).strip()
