# Signal-Garden
ignal Garden is a local-first autonomous research and semantic memory system built around:

- Obsidian

- GPT synthesis

- semantic concept extraction

- autonomous research queues

- living concept pages

- knowledge dashboards

- recency-weighted concept momentum

- concept relationship tracking

## Features

- Autonomous AI research

- Defuddle article ingestion

- Semantic memory

- Persistent concept tracking

- Obsidian wikilinking

- Dashboard generation

- Research queue orchestration

- Trend-aware semantic state

## Architecture

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

## Setup


pip install -r requirements.txt
Create:


.env
Add:


OPENAI\_API\_KEY=...
Run:


python research\_agent.py
Semantic Memory
Signal Garden stores its semantic state in the Obsidian vault under Memory/:

concept_state.json for recency-aware concept records
concept_relationships.json for concept co-occurrence edges
concept_frequency.json as a legacy compatibility cache
The dashboard now emphasizes:

active concepts
fastest-rising concepts
active relationships
queue state
daily source-backed brief
Each daily brief links back to the source notes and original article URLs so you can open the full article when you want the underlying evidence.
