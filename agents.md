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
- reserves one `Next Recommended Reading` slot for a new area when the last 24 hours surface one, and labels it explicitly as `New Area`
- falls back to the last 72 hours for the active topic, then a broader 72-hour recent overview, when the strict 24-hour daily window is empty
- writes a weekly rollup from the last 7 days of sources
- writes a calm weekly reading issue with Deep Reads, Practical Reads, New Area, Wildcard, and Follow-up sections
- writes an audio-ready script and an Open Notebook podcast handoff note
- can sync source URLs into Open Notebook through its local API and optionally submit a podcast generation job
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

The core scripts are:

- `research_agent.py`: end-to-end autonomous research loop
- `obsidian_connector.py`: minimal Obsidian note helper and integration test script
- `config_admin.py`: local Tkinter maintenance app for editing `areas.json`
- `open-notebook.docker-compose.yml`: local Open Notebook starter stack
- `validate_signal_garden.py`: read-only semantic state and artifact validator
- `repair_signal_garden.py`: dry-run-first lightweight state repair helper
- `monitor_open_notebook_podcast.py`: Open Notebook job poller and podcast audio downloader

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

## Current Gaps

### 1. Validation is still lightweight

The semantic state files now exist, but there is not yet a focused validator for malformed concept records, broken relationship edges, missing source metadata, stale queue state, or Open Notebook handoff metadata.

Preferred direction:

- add a lightweight validation script
- report repair suggestions without mutating by default
- check vault paths, source note frontmatter, semantic JSON files, and podcast bundle fields

### 2. Relationship alerts are not first-class yet

Signal Garden tracks relationship edges, but interim alerts still focus mostly on individual concepts.

Preferred direction:

- alert on sustained movement in concept pairs
- surface emerging relationship clusters
- distinguish durable relationships from one-off co-occurrence

### 3. Podcast completion is not yet durable

Signal Garden can submit Open Notebook podcast jobs and place links in the PDF, but long-running audio jobs may finish after the PDF is generated.

Preferred direction:

- add a small monitor/update command
- download finished audio into the vault
- update the handoff note and dashboard with durable local audio links

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
