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

\- visual active-area and new-area maps in the daily PDF

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

Validate Signal Garden state:

```bash
python validate_signal_garden.py
```

Dry-run lightweight state repairs:

```bash
python repair_signal_garden.py
```

Apply lightweight state repairs:

```bash
python repair_signal_garden.py --apply
```

Poll the latest Open Notebook podcast job and download completed audio:

```bash
python monitor_open_notebook_podcast.py
```

Upload the latest daily PDF and podcast MP3 to a configured Google Drive destination:

```bash
python upload_drive_artifacts.py --latest
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
- a compact health dashboard in `MOCs/Signal Garden Health`

Each daily brief links back to the source notes and original article URLs so you can open the full article when you want the underlying evidence.
The daily brief now works as a multi-area daily overview, so it can surface new topics alongside recurring themes from the last 24 hours instead of locking onto just one queue item.
If the last-24-hour window is empty, the daily brief now falls back to the last 72 hours for the active topic, then to a broader 72-hour recent overview, so the report does not go blank after quiet periods.
The daily PDF renders Active Areas and New Areas as visual garden maps with live labels and counts. By default it uses a generated CSS map; set `AREA_MAP_IMAGE_PATH` or save a clean text-free backdrop at `C:\HermesBridge\area-map-clean.png` or `C:\HermesBridge\header-map-clean.png` to use custom artwork under the dynamic labels.
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
- `Audio/Audio Script - YYYY-MM-DD` turns that issue into a precise single-voice script for listening or text-to-speech.
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
OPEN_NOTEBOOK_EPISODE_PROFILE=signal_forecast
OPEN_NOTEBOOK_SPEAKER_PROFILE=single_forecaster
OPEN_NOTEBOOK_PODCAST_POLL_SECONDS=20
```

Set `OPEN_NOTEBOOK_GENERATE_PODCAST=true` only when Open Notebook has working LLM and TTS credentials configured, because that will submit an actual podcast generation job.
The default podcast prompt is a single-presenter audio bulletin: calm, precise, sparse, and closer to a shipping forecast than a radio discussion.
The daily PDF includes a Podcast section with the Open Notebook job link, the handoff note, the source bundle, and a direct audio download link when the Open Notebook job has already returned an episode ID.

Google Drive upload is also opt-in. Use one of these routes:

```bash
GOOGLE_DRIVE_UPLOAD_ENABLED=true
GOOGLE_DRIVE_LOCAL_FOLDER=C:\Path\To\Google Drive\Shared\Signal Garden
```

or configure `rclone` for Google Drive and point it at the shared folder:

```bash
GOOGLE_DRIVE_UPLOAD_ENABLED=true
GOOGLE_DRIVE_RCLONE_REMOTE=gdrive-shared:Signal Garden
```

The shared Drive folder ID currently used manually is `1BtGAcXwValeRe6HafqsSBRR6D1x_h0lp`.

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

The top 10 improvements now have first-pass implementations:

1. `validate_signal_garden.py` validates semantic memory, source metadata, queue state, and Open Notebook bundle structure.
2. Relationship alerts are included in interim trend alert detection.
3. `monitor_open_notebook_podcast.py` polls Open Notebook and downloads completed podcast audio.
4. Source-quality scoring now rewards preferred, trusted, primary, fresh, and fuller sources while down-weighting generic explainers.
5. `config_admin.py` now includes priority topics, boosts, and a guided area-family creator.
6. `repair_signal_garden.py` dry-runs and applies lightweight queue/relationship state repairs.
7. Weekly rollups include a trend comparison table for this week, prior week, and trailing 21 days.
8. Queue prioritization can learn from manual clips through `Memory/queue_feedback.json`.
9. Completed Open Notebook audio can be downloaded into `Reports/` and linked from the PDF/handoff path.
10. `MOCs/Signal Garden Health` summarizes run status, fallbacks, Open Notebook status, and podcast state.

