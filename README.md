\# Signal Garden



Signal Garden is a local-first autonomous research and semantic memory system built around:



\- Obsidian

\- GPT synthesis

\- semantic concept extraction

\- autonomous research queues

\- living concept pages

\- knowledge dashboards

\- recency-weighted concept momentum

\- concept relationship tracking

\- source quality scoring and source clustering



\## Features



\- Autonomous AI research

\- Defuddle article ingestion

\- Semantic memory

\- Persistent concept tracking

\- Obsidian wikilinking

\- Dashboard generation

\- Research queue orchestration

\- Trend-aware semantic state

\- Daily overview and weekly source-backed reports

\- searchable source archive pages

\- calm weekly reading issues

\- audio-ready reading scripts

\- manual clip ingestion from the Obsidian inbox

\- interim trend alerts for sustained surges between scheduled runs

\- a local admin panel for editing `areas.json`
\- a dry-run-first source title migration utility



\## Architecture



Internet

↓

Signal Garden Research Agent

↓

Semantic Extraction

↓

Concept State + Relationships

↓

Living Knowledge Pages

↓

Obsidian Vault



\## Setup



```bash

pip install -r requirements.txt

```



Create:



```bash

.env

```



Add:



```bash

OPENAI\_API\_KEY=...

```



Run:



```bash

python research\_agent.py

```

Open the config admin panel:

```bash

python config_admin.py

```

This opens the local desktop maintenance UI for `areas.json`; it does not run as a browser page.

Preview source title migrations:

```bash

python migrate_source_note_titles.py

```

To email the daily PDF, set these environment variables and turn on `PDF_EMAIL_ENABLED`:

```bash

PDF_EMAIL_ENABLED=true
PDF_EMAIL_TO=you@example.com
PDF_EMAIL_FROM=signal-garden@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=signal-garden@example.com
SMTP_PASSWORD=...
SMTP_USE_TLS=true
PDF_EMAIL_BODY_INCLUDE_NEXT_READING=true
PDF_EMAIL_MAX_NEXT_READING=3

```

The email body includes the top summary points plus the current `Next Recommended Reading` links from the daily brief.
It also includes the `Digging Deeper` follow-up note and its top links for a faster skim.

Run a quick SMTP smoke test without a full research cycle:

```bash

python research_agent.py --test-email

```

## Semantic Memory

Signal Garden stores its semantic state in the Obsidian vault under `Memory/`:

- `concept_state.json` for recency-aware concept records
- `concept_relationships.json` for concept co-occurrence edges
- `concept_frequency.json` as a legacy compatibility cache

The dashboard now emphasizes:

- active concepts
- fastest-rising concepts
- active relationships
- recent source clusters
- queue state
- daily source-backed brief

Each daily brief links back to the source notes and original article URLs so you can open the full article when you want the underlying evidence.
The daily brief now works as a multi-area daily overview, so it can surface new topics alongside recurring themes from the last 24 hours instead of locking onto just one queue item.
If the last-24-hour window is empty, the daily brief now falls back to the last 72 hours for the active topic, then to a broader 72-hour recent overview, so the report does not go blank after quiet periods.
Mobile topics now use site-targeted search hints and broader mobile-doc domain coverage so the report can actually surface Android, iOS, PWA, AR, speech, GPX, and visual location sources instead of drifting back to generic AI content.
Mobile reports now include a platform balance block so Android and iOS stay visible together instead of one quietly taking over the brief.
The `Next Recommended Reading` block now reserves one slot for a `New Area` whenever the last 24 hours surface a genuinely fresh topic.
Signal Garden also tracks open-source OCR topics, gives them a short configurable boost ahead of older backlog items, and adds a weekly GitHub trending repository watchlist to the weekly rollup.

Signal Garden also exports a styled daily PDF into `Reports/` alongside the markdown brief, and a weekly rollup into `Weekly/`.
If PDF email is enabled, it sends the daily PDF once per day and skips duplicate sends on the 30-minute scheduler.
The interim alert note now only fires when a concept clears a stricter 24-hour movement threshold and has enough source support to look sustained.

It also writes a searchable source archive into `Archive/`.
The archive shows each short Obsidian node label alongside the original full article title.
When a concept keeps accelerating across the last 24 hours, Signal Garden also writes a live alert into `Alerts/`.

Signal Garden also writes a calmer weekly reading layer:

- `Reading/Reading Issue - YYYY-MM-DD` groups the strongest sources into Deep Reads, Practical Reads, New Area, Wildcard, and Follow-up sections.
- `Audio/Audio Script - YYYY-MM-DD` turns that issue into a host-style script for listening or text-to-speech.
- `Audio/Open Notebook Podcast Handoff - YYYY-MM-DD` packages the source URLs, local note links, and a custom prompt for generating an Open Notebook podcast.
- `Reports/Open Notebook Podcast Bundle - YYYY-MM-DD.json` gives the same source bundle in machine-readable form for future REST API automation.
- One wildcard source is deliberately included when possible so the reading list does not become too predictable.

Open Notebook can be started with Docker:

```bash
docker compose -f open-notebook.docker-compose.yml up -d
```

Then open `http://localhost:8502`. Signal Garden assumes the app is at `OPEN_NOTEBOOK_BASE_URL=http://localhost:8502` and the API is at `OPEN_NOTEBOOK_API_URL=http://localhost:5055` unless those environment variables are changed.

Open Notebook automation is opt-in:

```bash
OPEN_NOTEBOOK_SYNC_ENABLED=true
OPEN_NOTEBOOK_GENERATE_PODCAST=false
OPEN_NOTEBOOK_NOTEBOOK_NAME=Signal Garden
OPEN_NOTEBOOK_EPISODE_PROFILE=tech_discussion
OPEN_NOTEBOOK_SPEAKER_PROFILE=tech_experts
OPEN_NOTEBOOK_PODCAST_POLL_SECONDS=20
```

Set `OPEN_NOTEBOOK_GENERATE_PODCAST=true` only when Open Notebook has working LLM and TTS credentials configured, because that will submit an actual podcast generation job.
The daily PDF includes a Podcast section with the Open Notebook job link, the handoff note, the source bundle, and a direct audio download link when the Open Notebook job has already returned an episode ID.

To add your own read-later links, place them in either:

- `Inbox/manual_clips.json` as a list of URLs or objects like `{"url": "...", "topic": "...", "reason": "..."}`
- `Inbox/Manual Clips.md` as plain Markdown links

Manual clips are fetched during the next run, saved as source notes, and tracked in `Memory/manual_clip_state.json` so the same URL is not repeatedly ingested.

The PDF report now includes:

- a branded header image
- an embedded publication date
- a clickable table of contents
- source clusters and priority reading links
- a Podcast section with Open Notebook status, handoff, source bundle, and audio links when available

## Future Improvements

The highest-value next improvements are:

1. Add a semantic data validator for `concept_state.json`, `concept_relationships.json`, queue state, source metadata, and Open Notebook handoff metadata.
2. Add relationship alerts so sustained movement in concept pairs can trigger alerts, not just single concepts.
3. Add a podcast completion monitor that polls Open Notebook after the main run and updates the handoff note/PDF companion link when audio finishes.
4. Add richer source-quality scoring for trusted domains, article depth, primary-source status, source freshness, and duplicated syndication.
5. Add a guided `areas.json` editor workflow for topic families, preferred domains, boosts, and MOC categories instead of raw list editing.
6. Add a migration/repair command for old source notes, missing metadata, shortened titles, and orphaned source records.
7. Add weekly trend comparison tables that compare this week, the prior week, and the trailing month.
8. Add queue-learning feedback from reading behavior, manual clips, podcast selections, and skipped/low-quality sources.
9. Add durable podcast artifacts by downloading completed Open Notebook audio into `Reports/` or `Audio/` and linking the local file from Obsidian.
10. Add a compact health dashboard covering last run status, empty-source fallbacks, API failures, email status, Open Notebook status, and scheduler freshness.

