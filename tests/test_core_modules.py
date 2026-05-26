from datetime import datetime
from pathlib import Path
import unittest

from config_admin_web import extract_urls, normalize_clip, normalize_personal_source
from signal_garden_core.source_notes import (
    build_recent_source_digest,
    extract_source_note_record,
    normalize_datetime_for_diff,
    parse_iso_datetime,
)
from signal_garden_core.source_quality import (
    is_commercial_mobile_retail_source,
    source_rejection_reason,
)
from signal_garden_core.semantic import (
    concept_trend_delta,
    normalize_concept_record,
    normalize_relationship_record,
)
from signal_garden_core.personal_sources import (
    load_personal_sources,
    parse_feed_items,
)
from signal_garden_core.text import normalize_note_title, normalize_topic_label


PROJECT_PATH = Path(__file__).resolve().parents[1]
FIXTURE_PATH = PROJECT_PATH / "tests" / "fixtures"


class CoreModuleTests(unittest.TestCase):
    def test_text_helpers_preserve_research_agent_rules(self):
        self.assertEqual(normalize_topic_label("  AI   Agents "), "ai agents")
        self.assertEqual(normalize_note_title("A/B:C*D?"), "ABCD")

    def test_source_note_record_extracts_fixture_metadata(self):
        record = extract_source_note_record(
            FIXTURE_PATH / "sample_vault" / "Sources" / "Sample Source.md"
        )

        self.assertEqual(record["title"], "Sample Source")
        self.assertEqual(record["url"], "https://example.com/research")
        self.assertEqual(record["domain"], "example.com")
        self.assertIn("Sample Source", build_recent_source_digest([record]))

    def test_datetime_helpers_parse_api_and_local_values(self):
        parsed = parse_iso_datetime("2026-05-25T09:00:00Z")

        self.assertIsNotNone(parsed)
        self.assertIsNone(normalize_datetime_for_diff(None))
        self.assertIsInstance(
            normalize_datetime_for_diff(datetime(2026, 5, 25, 9, 0, 0)),
            datetime,
        )

    def test_mobile_retail_sources_are_rejected(self):
        record = {
            "domain": "tescomobile.com",
            "title": "Mobile Phones, Phone Contracts & SIM Only Deals",
            "description": "Commercial phone and SIM package sales page.",
        }

        self.assertTrue(is_commercial_mobile_retail_source(record))
        self.assertEqual(source_rejection_reason(record), "commercial-mobile-retail")

    def test_semantic_helpers_normalize_legacy_state(self):
        concept = normalize_concept_record(3)
        relationship = normalize_relationship_record({"weight": "2", "sightings": ["2026-05-25"]})

        self.assertEqual(concept["seen_count"], 3)
        self.assertEqual(relationship["weight"], 2)
        self.assertIn("delta", concept_trend_delta({"sightings": ["2026-05-25"]}))

    def test_personal_sources_parse_rss_feed_items(self):
        rss = """<?xml version="1.0"?>
        <rss version="2.0">
          <channel>
            <title>Example Feed</title>
            <item>
              <title>Useful post</title>
              <link>https://example.com/useful-post</link>
              <pubDate>Tue, 26 May 2026 08:00:00 GMT</pubDate>
              <description>A useful personal source.</description>
            </item>
          </channel>
        </rss>"""

        items = parse_feed_items(rss, {"title": "Example Feed"}, limit=2)

        self.assertEqual(items[0]["title"], "Useful post")
        self.assertEqual(items[0]["url"], "https://example.com/useful-post")

    def test_personal_sources_load_from_config(self):
        config = {
            "personal_sources": {
                "rss_feeds": [
                    {
                        "title": "Example Feed",
                        "url": "https://example.com/feed.xml",
                        "topic": "AI Agents"
                    }
                ],
                "blog_urls": [
                    "https://example.com/blog"
                ]
            }
        }

        sources = load_personal_sources(
            config,
            FIXTURE_PATH / "missing_inbox"
        )

        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["type"], "rss")

    def test_admin_helpers_extract_dropped_urls(self):
        text = "Read https://example.com/post and https://example.com/feed.xml."

        self.assertEqual(
            extract_urls(text),
            [
                "https://example.com/post",
                "https://example.com/feed.xml"
            ]
        )
        self.assertEqual(
            normalize_clip({"url": "https://example.com/a"})[0]["url"],
            "https://example.com/a"
        )
        self.assertEqual(
            normalize_personal_source(
                {
                    "type": "rss",
                    "feed_url": "https://example.com/feed.xml"
                }
            )[0]["feed_url"],
            "https://example.com/feed.xml"
        )


if __name__ == "__main__":
    unittest.main()
