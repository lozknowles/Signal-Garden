# Signal Garden Agents Guide

This repository powers Signal Garden, a local-first autonomous research and semantic memory system built around Obsidian notes, GPT synthesis, concept extraction, research queues, and dashboards.

Use this file as the operating guide for future agents working in this repo.

## What Signal Garden Is Doing Today

Signal Garden currently:

- pulls research topics from a queue or topic list
- searches the web for relevant sources
- defuddles article content when possible
- stores source notes in the Obsidian vault
- synthesizes a research update with GPT
- extracts canonical concepts from the synthesized text
- increments concept frequency counts
- writes concept memory notes and concept area pages
- generates MOCs and a dashboard note
- writes a daily overview brief with source attribution, active areas, new areas, source clusters, and priority reading links
- renders active areas and new areas as visual PDF garden maps with dynamic labels over an optional clean backdrop image
- reserves one `Next Recommended Reading` slot for a new area when the last 24 hours surface one, and labels it explicitly as `New Area`
- falls back to the last 72 hours for the active topic, then a broader 72-hour recent overview, when the strict 24-hour daily window is empty
- writes a weekly rollup from the last 7 days of sources
- writes a calm weekly reading issue with Deep Reads, Practical Reads, New Area, Wildcard, and Follow-up sections
- writes an audio-ready single-voice script and an Open Notebook podcast handoff note
- can sync source URLs into Open Notebook through its local API and optionally submit a single-presenter podcast generation job
- adds a Podcast section to the daily PDF with Open Notebook status, handoff, source bundle, and audio links when available
- writes a searchable source archive for recent sources
- writes an interim alert note when a concept sustains a surge between scheduled runs
- supports a `--test-email` mode for validating SMTP delivery without running a full research cycle
- now treats mobile development as a first-class semantic domain, including Android, iOS, React Native, PWA, AR, speech, GPX, and image-based location work
- now treats open-source OCR as a first-class semantic area, gives it a short configurable priority boost before it cools off, and tracks weekly GitHub trending repositories in the weekly rollup
- keeps the daily brief centered on the last 24 hours of sources so new areas can appear alongside recurring themes
- uses mobile-specific site-targeted search hints plus a richer mobile-doc domain list so mobile topics are more likely to produce actual source notes
- renders a mobile platform balance section so Android and iOS stay visible together instead of one taking over the brief
- keeps oversized source titles short so Obsidian graph nodes stay readable
- has public-readiness documentation for cloning/forking, including `README.md`, `docs/architecture.md`, and an MIT license
- supports configurable vault, config, and report image paths through `.env`

The core scripts are:

- `research_agent.py`: end-to-end autonomous research loop
- `obsidian_connector.py`: minimal Obsidian note helper and integration test script
- `config_admin.py`: local Tkinter maintenance app for editing `areas.json`
- `open-notebook.docker-compose.yml`: local Open Notebook starter stack
- `validate_signal_garden.py`: read-only semantic state and artifact validator
- `repair_signal_garden.py`: dry-run-first lightweight state repair helper
- `monitor_open_notebook_podcast.py`: Open Notebook job poller and podcast audio downloader
- `upload_drive_artifacts.py`: opt-in uploader for latest daily PDF and podcast MP3 via local Drive folder or `rclone`

The daily PDF uses separate visual backdrops for the area sections: `header-map-clean.png` for Active Areas and `header-map-new-areas.png` for New Areas by default. Override them with `ACTIVE_AREAS_MAP_IMAGE_PATH` and `NEW_AREAS_MAP_IMAGE_PATH`. Keep labels out of future artwork where possible; Signal Garden overlays live area names and counts during report generation.

## Project Goals

Signal Garden is trying to become a persistent cognitive substrate, not just a content generator.

The most important near-term goals are:

1. Keep concept tracking temporal and interpretable, not just cumulative.
2. Make concept relationships actionable through alerts, clusters, and graph-aware recommendations.
3. Keep the research queue adaptive so the system can focus on emerging areas.
4. Keep mobile development and document intelligence as first-class semantic domains.
5. Make the reading and podcast layer reliable enough to become a regular review ritual.

## Current Strengths

The current system already has:

- memory
- synthesis
- queueing
- dashboards
- semantic extraction
- ontology stabilization through canonical concept mapping

That is a strong base. The next step is making the system aware of time and relationships.

## Current Rough Edges

Signal Garden is now suitable to publish as a working local-first reference project, but not as a production framework.

The main rough edges are tracked in `TODO.md`. The most important ones are:

- `research_agent.py` is still monolithic and should be split into modules.
- The project is Windows-first because that is where it was built and tested.
- Automated tests and CI are still light.
- Web search can fail or return thin results.
- Open Notebook, Google Drive, email, and PDF export remain optional local-environment integrations.
- A first-run setup wizard would make forks much easier.

## Suggested Data Model Direction

The current frequency map is a good starting point, but it should evolve toward records like:

```json
{
  "AI Agents": {
    "score": 45,
    "last_seen": "2026-05-21",
    "seen_count": 12
  }
}
```

For relationships, a simple edge map would be enough initially:

```json
{
  "AI Agents|MCP": {
    "weight": 9,
    "last_seen": "2026-05-21"
  }
}
```

Signal Garden now also maintains:

- `Memory/concept_state.json` for recency-aware concept records
- `Memory/concept_relationships.json` for concept co-occurrence edges
- `Memory/concept_frequency.json` as a legacy count cache
- `Memory/manual_clip_state.json` for manually supplied read-later URLs
- `Reports/Open Notebook Podcast Bundle - YYYY-MM-DD.json` for podcast source bundles

## Working Rules For Future Agents

- Prefer small, additive changes over rewrites.
- Preserve the Obsidian vault structure and note-writing behavior.
- Keep canonical concepts stable unless there is a clear taxonomy reason to change them.
- Treat `areas.json` as the source of truth for folders, topics, preferred sources, and MOC categories.
- Treat `concept_state.json` and `concept_relationships.json` as the semantic source of truth for momentum and edges.
- Treat Open Notebook integration as opt-in. Do not submit podcast jobs unless `OPEN_NOTEBOOK_GENERATE_PODCAST=true`.
- Keep Signal Garden podcasts in the single-voice bulletin style: precise, sparse, source-grounded, and closer to a shipping forecast than a radio discussion.
- Treat Google Drive upload as opt-in. Do not upload unless `GOOGLE_DRIVE_UPLOAD_ENABLED=true` and either a local Drive folder or `rclone` remote is configured.
- Treat `.env` as local-only and keep secrets out of commits.
- Prefer configurable paths (`SIGNAL_GARDEN_VAULT_PATH`, `SIGNAL_GARDEN_CONFIG_PATH`, image path overrides) over hardcoded local machine paths.
- Keep daily PDFs useful even when a strict 24-hour window is empty; preserve the 72-hour fallback unless replacing it with something better.
- Update the dashboard when any core semantic model changes.
- Avoid introducing heavy dependencies unless they clearly improve the memory system.

## Top 10 Improvements Now Started

1. Semantic validation exists in `validate_signal_garden.py`; future work should deepen repair suggestions and source frontmatter checks.
2. Relationship alerts now run alongside concept alerts; future work should tune thresholds with real usage.
3. Podcast completion monitoring exists in `monitor_open_notebook_podcast.py`; future work should schedule it automatically.
4. Source-quality scoring now considers preferred, trusted, primary, fresh, full-depth, and generic-explainer signals.
5. The config admin now has priority topics, boosts, and a guided area-family creator.
6. Lightweight state repair exists in `repair_signal_garden.py`; future work should expand source-note repair.
7. Weekly rollups now include a trend comparison table.
8. Queue feedback now learns from manual clips through `Memory/queue_feedback.json`.
9. Podcast audio can be downloaded into `Reports/` when Open Notebook exposes an episode ID.
10. `MOCs/Signal Garden Health` summarizes run status, fallbacks, Open Notebook, and podcast state.

## How To Think About Future Changes

When deciding what to build next, prioritize features that help Signal Garden answer:

- what matters now
- what is increasing
- what is connected
- what should be researched next

That is the operating center of the project.
