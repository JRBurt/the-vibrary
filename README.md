# the-vibrary

A pgvector-backed RAG index over markdown, exposed to agents as an MCP server.
Point an MCP client (Claude Code, Claude Desktop, etc.) at this project and it
can search your markdown corpus (glossaries, skill files, notes) by meaning,
scoped to a named collection.

## How it fits together

1. `src/ingest.py` walks `VIBRARY_DATA_DIR/<collection>/**/*.md`, splits each
   file into overlapping chunks, embeds them locally, and upserts them into a
   single `chunks` table in Postgres (pgvector extension).
2. `src/mcp_server.py` exposes that table to any MCP client via two tools:
   `search(query, collection=None, top_k=5)` and `list_collections()`.
3. The agent decides when to call `search`; it never touches the database or
   the embedding model directly, only the tool interface.

Your real markdown corpus lives outside this repo entirely (see `.env`), so
nothing private ever enters git history. This repo ships with a small
synthetic demo corpus under `data/demo/` so it works out of the box.

## Setup

```bash
cp .env.example .env
# edit .env: set VIBRARY_DATA_DIR to your real corpus, or leave as ./data/demo to try the sample

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d        # starts Postgres with pgvector on localhost:5433

python -m src.ingest        # chunks + embeds + indexes everything under VIBRARY_DATA_DIR
python -m src.mcp_server    # starts the MCP server over stdio
```

Then point your MCP client's config at `python -m src.mcp_server` (run from
this project's root, with the venv active) to start querying.

## Data layout

```
<VIBRARY_DATA_DIR>/
  glossary/*.md
  skills/*.md
  notes/*.md            # whatever collections you want; each top-level folder is a collection
```

Re-running `python -m src.ingest` after editing a file re-embeds just that
file and replaces its chunks, so the index doesn't go stale.
