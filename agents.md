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
- writes a weekly rollup from the last 7 days of sources
- writes a searchable source archive for recent sources
- writes an interim alert note when a concept sustains a surge between scheduled runs
- supports a `--test-email` mode for validating SMTP delivery without running a full research cycle
- now treats mobile development as a first-class semantic domain, including Android, iOS, React Native, PWA, AR, speech, GPX, and image-based location work
- keeps the daily brief centered on the last 24 hours of sources so new areas can appear alongside recurring themes
- uses mobile-specific site-targeted search hints plus a richer mobile-doc domain list so mobile topics are more likely to produce actual source notes
- renders a mobile platform balance section so Android and iOS stay visible together instead of one taking over the brief
- keeps oversized source titles short so Obsidian graph nodes stay readable

The core scripts are:

- `research_agent.py`: end-to-end autonomous research loop
- `obsidian_connector.py`: minimal Obsidian note helper and integration test script

## Project Goals

Signal Garden is trying to become a persistent cognitive substrate, not just a content generator.

The most important near-term goals are:

1. Make concept tracking temporal, not just cumulative.
2. Make concept relationships explicit, not just visually implied by Obsidian links.
3. Keep the research queue adaptive so the system can focus on emerging areas.
4. Expand the research queue into mobile development topics where Signal Garden can compare native, web, and cross-platform approaches.

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

### 1. No recency weighting

`concept_frequency.json` only counts upward forever.

That means old concepts can dominate forever even if they have stopped appearing recently.

Preferred direction:

- store `score`
- store `last_seen`
- optionally store a short history of recent sightings
- compute a recency-weighted ranking for the dashboard and queue

### 2. No explicit relationship model

Signal Garden can write wiki links, but it does not yet understand:

- co-occurrence
- dependency
- relationship strength
- concept clusters

Preferred direction:

- track concept pairs from each synthesis cycle
- increment pair weights when concepts appear together
- use this to surface emerging knowledge graph structure

### 3. Dashboard is descriptive, not interpretive

The dashboard shows counts and queue state, but it should also answer:

- what is newly emerging
- what is accelerating
- what is fading
- what concepts are becoming central
- what sources are clustering together

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

## Working Rules For Future Agents

- Prefer small, additive changes over rewrites.
- Preserve the Obsidian vault structure and note-writing behavior.
- Keep canonical concepts stable unless there is a clear taxonomy reason to change them.
- Treat `areas.json` as the source of truth for folders, topics, preferred sources, and MOC categories.
- Treat `concept_state.json` and `concept_relationships.json` as the semantic source of truth for momentum and edges.
- Update the dashboard when any core semantic model changes.
- Avoid introducing heavy dependencies unless they clearly improve the memory system.

## Immediate Next Steps

1. Improve source quality heuristics so trusted domains and fuller articles rise faster.
2. Expand the weekly rollup with trend comparisons against the previous week.
3. Add a lightweight validation script for the new semantic data files.
4. Evolve the config admin panel into a more guided editor for `areas.json`.
5. Add a migration pass for pre-existing source notes when title length or naming rules change.
6. Expand alerts to cover concept relationships, not just single-concept surges.
7. Keep interim alerts conservative so only clearly sustained movement gets surfaced.

## How To Think About Future Changes

When deciding what to build next, prioritize features that help Signal Garden answer:

- what matters now
- what is increasing
- what is connected
- what should be researched next

That is the operating center of the project.
