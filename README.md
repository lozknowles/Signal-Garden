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

\- Daily and weekly source-backed reports

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

Signal Garden also exports a styled daily PDF into `Reports/` alongside the markdown brief, and a weekly rollup into `Weekly/`.

It also writes a searchable source archive into `Archive/`.
The archive shows each short Obsidian node label alongside the original full article title.
When a concept keeps accelerating across the last 24 hours, Signal Garden also writes a live alert into `Alerts/`.

The PDF report now includes:

- a branded header image
- an embedded publication date
- a clickable table of contents
- source clusters and priority reading links

