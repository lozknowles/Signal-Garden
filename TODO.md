# Signal Garden TODO

## Top 10 Future Improvements

- [x] Add a semantic data validator for `concept_state.json`, `concept_relationships.json`, queue state, source metadata, and Open Notebook handoff metadata.
- [x] Add relationship alerts so sustained movement in concept pairs can trigger alerts, not just single concepts.
- [x] Add a podcast completion monitor that polls Open Notebook after the main run and updates the handoff note/PDF companion link when audio finishes.
- [x] Add richer source-quality scoring for trusted domains, article depth, primary-source status, source freshness, and duplicated syndication.
- [x] Add a guided `areas.json` editor workflow for topic families, preferred domains, boosts, and MOC categories instead of raw list editing.
- [x] Add a migration/repair command for old source notes, missing metadata, shortened titles, and orphaned source records.
- [x] Add weekly trend comparison tables that compare this week, the prior week, and the trailing month.
- [x] Add queue-learning feedback from reading behavior, manual clips, podcast selections, and skipped/low-quality sources.
- [x] Add durable podcast artifacts by downloading completed Open Notebook audio into `Reports/` or `Audio/` and linking the local file from Obsidian.
- [x] Add a compact health dashboard covering last run status, empty-source fallbacks, API failures, email status, Open Notebook status, and scheduler freshness.

## Follow-Up Hardening

- [ ] Schedule `monitor_open_notebook_podcast.py` after long-running podcast jobs.
- [x] Expand `repair_signal_garden.py` to repair source-note frontmatter.
- [ ] Tune relationship alert thresholds after a week of real runs.
- [ ] Add tests around source quality scoring and weekly comparison tables.
- [ ] Add optional authenticated X/API connectors for users who want native social ingestion beyond RSS/feed bridges and direct URLs.
- [ ] Vendor or locally build the React admin app so it works fully offline instead of loading React from a CDN.
- [ ] Configure Google Drive upload through either Drive for Desktop local sync or `rclone`.

## Public Readiness Rough Edges

- [x] Split reusable runtime helpers out of `research_agent.py` into `signal_garden_core/` modules for JSON state, Obsidian writing, source notes, source quality, semantic state, optional integrations, PDF export, and text normalization.
- [ ] Continue slimming `research_agent.py` by moving report assembly and synthesis orchestration into focused runtime modules.
- [x] Add CI and smoke tests for core scripts.
- [x] Add a proper CLI with commands such as `run`, `validate`, `repair`, `podcast`, and `upload`.
- [x] Provide a small sample vault fixture for contributors and automated tests.
- [ ] Make path and artifact handling fully cross-platform beyond the current Windows-first defaults.
- [ ] Improve web search resilience when DuckDuckGo/DDGS fails or returns thin results.
- [ ] Add a first-run setup wizard for `.env`, vault path, OpenAI key checks, and `areas.json`.
- [ ] Document Open Notebook profile setup more deeply, including creating the single-voice profile.
- [ ] Improve report theming and image asset overrides for forks.
- [ ] Add a minimal Docker/devcontainer path for contributors.
