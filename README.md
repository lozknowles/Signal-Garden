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
Mobile topics now use site-targeted search hints and broader mobile-doc domain coverage so the report can actually surface Android, iOS, PWA, AR, speech, GPX, and visual location sources instead of drifting back to generic AI content.
Mobile reports now include a platform balance block so Android and iOS stay visible together instead of one quietly taking over the brief.
The `Next Recommended Reading` block now reserves one slot for a `New Area` whenever the last 24 hours surface a genuinely fresh topic.

Signal Garden also exports a styled daily PDF into `Reports/` alongside the markdown brief, and a weekly rollup into `Weekly/`.
If PDF email is enabled, it sends the daily PDF once per day and skips duplicate sends on the 30-minute scheduler.
The interim alert note now only fires when a concept clears a stricter 24-hour movement threshold and has enough source support to look sustained.

It also writes a searchable source archive into `Archive/`.
The archive shows each short Obsidian node label alongside the original full article title.
When a concept keeps accelerating across the last 24 hours, Signal Garden also writes a live alert into `Alerts/`.

The PDF report now includes:

- a branded header image
- an embedded publication date
- a clickable table of contents
- source clusters and priority reading links

