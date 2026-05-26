from datetime import datetime
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
