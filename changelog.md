# Changelog

## 2026-05-25

- Added a weekly `Reading/Reading Issue - YYYY-MM-DD` note that turns recent source rankings into Deep Reads, Practical Reads, New Area, Wildcard, and Follow-up sections.
- Added an `Audio/Audio Script - YYYY-MM-DD` note that converts the reading issue into a text-to-speech-friendly host script.
- Added an `Audio/Open Notebook Podcast Handoff - YYYY-MM-DD` note with source URLs, local source links, a custom podcast prompt, and placeholders for the generated Open Notebook audio link or downloaded file.
- Added `Reports/Open Notebook Podcast Bundle - YYYY-MM-DD.json` for future Open Notebook REST API automation.
- Added opt-in Open Notebook API automation for creating/finding a Signal Garden notebook, syncing source URLs, and submitting podcast jobs when enabled.
- Added a Podcast section to the daily PDF with Open Notebook job/status links, handoff links, source bundle links, and a direct audio download link when an episode ID is available.
- Added `open-notebook.docker-compose.yml` as a local Open Notebook starter template.
- Added manual clip ingestion from `Inbox/manual_clips.json` and `Inbox/Manual Clips.md`, with processed URLs tracked in `Memory/manual_clip_state.json`.
- Added `Reading` and `Audio` to the managed Obsidian folder list and linked the latest issue/script from the dashboard.
- Added a daily source fallback so empty 24-hour reports can use the active topic's last 72 hours, then a broader 72-hour overview.
- Documented the local `config_admin.py` maintenance app and captured the top future-improvement priorities in the README and agent guide.
- Added `validate_signal_garden.py`, `repair_signal_garden.py`, and `monitor_open_notebook_podcast.py`.
- Added relationship alerts, weekly trend comparison tables, queue feedback from manual clips, durable podcast download support, and `MOCs/Signal Garden Health`.
- Expanded source-quality scoring and upgraded the config admin with priority topics, boosts, and a guided area-family creator.

## 2026-05-23

- Reworked the daily brief into a multi-area daily overview so new areas of interest can appear alongside recurring themes from the last 24 hours.
- Passed topic coverage through the daily brief, digging-deeper note, email digest, and weekly rollup ranking paths so emerging areas influence follow-up recommendations.
- Kept the active-areas and new-areas sections prominent in the brief so the report is less dominated by a single long-running topic.
- Reserved one `Next Recommended Reading` slot for a `New Area` and labeled it explicitly in the brief, PDF, email digest, and digging-deeper note.
- Added open-source OCR as a first-class research area, gave it a short configurable queue boost that resets from `areas.json` when the config changes, and added a weekly GitHub trending repositories section to the weekly rollup.

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
- Expanded the research queue with mobile development topics covering native vs web, Android, iOS, AR, speech, GPX, and image-based location workflows.
- Added mobile-specific canonical concepts and a `Mobile Development` MOC category so the semantic layer can recognize those topics in reports and alerts.
- Scoped the daily brief to the active topic so older queued themes no longer drown out the current report.
- Added site-targeted mobile search hints and broader mobile-doc domain coverage so mobile runs can surface real Android, iOS, PWA, AR, speech, GPX, and location articles instead of falling back to generic AI results.
- Normalized topic matching when collecting recent source notes so topic-scoped reporting is more resilient to casing and spacing differences.
- Added a mobile platform balance section so Android and iOS stay visible together instead of one quietly taking over the brief.
