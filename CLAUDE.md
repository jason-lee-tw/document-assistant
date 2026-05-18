# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project

A LangChain RAG document assistant: a FastAPI backend that ingests local and Tavily-crawled documents into pgvector, then answers chat queries via Claude, with Phoenix tracing and Ollama-served embeddings.

# Stack & commands

Python 3.14, uv workspace (member: `apps/backend`), FastAPI, LangChain, Alembic, pgvector, Arize Phoenix, Ollama, Docker Compose.

```bash
just init        # uv sync at repo root — the single .venv lives here
just up-all      # boot Ollama + the compose stack (backend, migration, pgvector, phoenix)
just down-all
just lint        # ruff check
just format      # ruff format
uv run pytest    # runs *_test.py files (co-located with source)
```

# Conventions

1. Tests live beside source as `*_test.py` (e.g. `server_test.py` next to `server.py`) — no top-level `tests/` dir.
2. Use `Logger(__name__)` from `server_config.logger` instead of stdlib `logging` or `print`.
3. Add every env var you read in code to `apps/backend/.env.template`.
4. Place new Alembic revisions under `apps/backend/src/migrations/versions/`; the `db-migration` container runs `alembic upgrade head` on every `up`.
5. Keep `chunk_id` as `{document_name}#{index}` — `filter_pending_documents` and other lookups assume this exact shape.
6. New HTTP routes go in a `*_controller.py` exposing a module-level `router`; `start_app` auto-discovers via glob — nothing else registers them.

# Layout

- `apps/backend/src/modules/<feature>/` — FastAPI controllers + services + DTOs, one folder per feature (`app`, `chat`, `rag`).
- `apps/backend/src/ai_agents/` — LangChain wrappers (`rag/`, `tavily/`, `base_agent.py`).
- `apps/backend/src/server_config/` — FastAPI app factory, Phoenix tracer, custom logger.
- `apps/backend/src/migrations/` — Alembic config and revisions.
- `docker/`, `docker-compose.yml`, `Justfile` — runtime stack, all at repo root.
- `docs/superpowers/` — prior plans/specs; read-only background context.

# Quirks

- Backend container uses `network_mode: host` so it can reach Ollama on `localhost:11434` — don't switch networks without re-pointing `OLLAMA_BASE_URL`.
- `apps/backend` is a uv workspace member but the `.venv` lives at the repo root; always `uv sync` from root, never from `apps/backend`.
- `scripts/` and `docs/` must not be moved or renamed.

# Plan-first before execute

- When given a task, firstly, ALWAYS analyse deeply to understand what the user actually want.
- Once you are clear on the scope and the details of the task, then start planning.
- ALWAYS review your plan before asking for human review the plan. Apply 5-why rules when reviewing the plan.
- NEVER make any assumption. Always clarify or ask question.
- NEVER start execution before human confirm the plan.
