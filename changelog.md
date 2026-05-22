# Changelog

## 2026-05-22

- Added recency-weighted concept state so Signal Garden can track both freshness and recurrence.
- Added concept relationship tracking based on co-occurrence during research synthesis cycles.
- Updated the dashboard to surface active concepts, fastest-rising concepts, and relationship edges.
- Added a daily brief note with source attribution and direct links back to full articles.
- Added a styled daily PDF export in `Reports/` alongside the markdown brief.
- Updated project documentation to describe the new semantic memory files and operating model.
- Added source quality scoring, source clustering, and recency-aware digging-deeper triage.
- Added a clickable PDF table of contents plus a branded header image with embedded publish date.
- Added a weekly rollup note in `Weekly/` based on the last 7 days of source notes.
- Added a searchable source archive note in `Archive/` and a local `config_admin.py` panel for editing `areas.json`.
- Tightened the config admin validation for `moc_categories` and made the dashboard archive link explicit.
- Normalized auto-generated source note titles so overly long article titles are shortened before becoming Obsidian node labels.
- Added a dry-run-first source title migration utility and surfaced the full article title alongside the short archive label.
- Added an `Alerts/` area and an interim trend alert note that fires when a concept sustains momentum between 30-minute runs.
- Added optional SMTP email delivery for the daily PDF with once-per-day deduplication to avoid scheduler spam.
- Added inline `Next Recommended Reading` links to the daily PDF email body and exposed the mail settings in `.env`.
- Added `Digging Deeper` links to the daily PDF email body, a `--test-email` mode, and stricter interim alert thresholds.
