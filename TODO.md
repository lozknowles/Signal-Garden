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
- [ ] Expand `repair_signal_garden.py` to repair source-note frontmatter.
- [ ] Tune relationship alert thresholds after a week of real runs.
- [ ] Add tests around source quality scoring and weekly comparison tables.
- [ ] Configure Google Drive upload through either Drive for Desktop local sync or `rclone`.
