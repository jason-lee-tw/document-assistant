# RAG Document Assistant

A LangChain-based **Retrieval-Augmented Generation (RAG)** service that ingests
local documents and Tavily-crawled web pages into a `pgvector` store, then
answers chat queries via Anthropic Claude with Ollama-served embeddings and
Arize Phoenix tracing.

---

## 1. Purpose

This repository is a learning / reference project for the AI Engineering
Upskill Program. It demonstrates the end-to-end mechanics of building a
production-style RAG application:

- **Ingest** documents (local files or crawled URLs) into a vector store.
- **Retrieve** the most relevant chunks for a user question.
- **Generate** grounded answers using Claude, comparing four approaches:
  - plain LLM chat (no retrieval),
  - manual RAG (retrieve → prompt → LLM),
  - LCEL pipeline (LangChain Expression Language),
  - tool-calling agent (`create_agent` with a retrieval tool).
- **Observe** every chain/agent call through Arize Phoenix (OpenTelemetry).

It is intentionally small enough to read end-to-end, but uses the full
production toolchain: FastAPI, uv workspace, Alembic migrations, Docker
Compose, Ruff, and Pytest.

---

## 2. Running the Application

### 2.1 Prerequisites

Install these on your host before starting:

| Tool | Purpose |
|---|---|
| [`uv`](https://docs.astral.sh/uv/) | Python 3.14 + dependency management |
| [`just`](https://github.com/casey/just) | Task runner (`Justfile`) |
| [Docker](https://docs.docker.com/get-docker/) (with Compose v2) | Runs backend, `pgvector`, Phoenix, db-migration |
| [Ollama](https://ollama.com/) | Serves the embedding model on `localhost:11434` |

You will also need:

- An **Anthropic API key** (`ANTHROPIC_API_KEY`) for Claude.
- A **Tavily API key** (`TAVILY_API_KEY`) for web crawling.

### 2.2 First-time setup

```bash
# 1. Install Python deps into the repo-root .venv (uv workspace)
just init

# 2. Create your local env file from the template
cp apps/backend/.env.template apps/backend/.env
# then fill in ANTHROPIC_API_KEY and TAVILY_API_KEY
```

> Every env var the code reads is listed in `apps/backend/.env.template` —
> keep that file in sync when adding new ones.

### 2.3 Boot the full stack

```bash
just up-all      # starts Ollama (host) + backend, pgvector, phoenix, db-migration (compose)
just down-all    # stops everything
```

On first boot:

- `ollama-checker` makes sure Ollama is reachable and the embedding model is
  pulled.
- `db-migration` runs `alembic upgrade head` against `pgvector`.
- `backend` starts on the host network at `http://localhost:${PORT}` (default
  `3001`).

Once up:

| Service | URL |
|---|---|
| Backend API | `http://localhost:3001` |
| Swagger UI | `http://localhost:3001/docs` |
| Phoenix tracing | `http://localhost:6006` |
| Postgres (pgvector) | `localhost:5432` |

### 2.4 Trying the API

Once the stack is up, the easiest way to explore every endpoint is the
auto-generated **Swagger UI** at **`http://localhost:3001/docs`** — it lists
every route, schema, and lets you fire requests straight from the browser.

You can also use `curl`:

```bash
# Health check
curl http://localhost:3001/

# Ingest every file under apps/backend/sample-docs (mounted as /sample-docs)
curl -X POST http://localhost:3001/rag/

# Crawl URLs with Tavily and embed the results
curl -X POST http://localhost:3001/rag/crawl \
  -H 'content-type: application/json' \
  -d '{"url_list": ["https://example.com"]}'

# Chat — four flavors, same request shape
curl -X POST http://localhost:3001/chat/with-rag-tool \
  -H 'content-type: application/json' \
  -d '{"message": "What is in the docs?", "history": []}'
```

Available chat endpoints:

- `POST /chat/`           — plain Claude, no retrieval
- `POST /chat/with-rag`   — manual retrieve → prompt → LLM
- `POST /chat/with-lcel`  — same pipeline expressed as an LCEL chain
- `POST /chat/with-rag-tool` — Claude as an agent calling a retrieval tool

### 2.5 Common dev commands

```bash
just lint            # ruff check
just lint-fix        # ruff check --fix
just format          # ruff format
uv run pytest        # tests live next to source as *_test.py
just down-clean      # stop containers AND drop volumes (wipes pgvector + phoenix data)
just clean-python    # remove .venv / __pycache__ / .ruff_cache
```

---

## 3. Folder Structure

```
rag-document-assistant/
├── apps/
│   └── backend/                       # The only workspace member (see pyproject.toml at root)
│       ├── .env.template              # Every env var the app reads — keep in sync
│       ├── pyproject.toml             # Backend deps (FastAPI, LangChain, pgvector, …)
│       ├── sample-docs/               # Drop files here; POST /rag/ ingests this folder
│       └── src/
│           ├── main.py                # Entrypoint — uvicorn factory bootstrapping
│           │
│           ├── server_config/         # App-wide infra
│           │   ├── server.py          # FastAPI factory; auto-discovers *_controller.py routers
│           │   ├── logger.py          # Custom Logger(__name__) — use this, not stdlib logging/print
│           │   └── tracer.py          # Phoenix / OpenTelemetry registration
│           │
│           ├── modules/               # Feature modules — one folder per HTTP feature
│           │   ├── app/               # /  (health check)
│           │   ├── chat/              # /chat/*   (controller + service + dto/)
│           │   └── rag/               # /rag/*    (controller + service + dto/)
│           │
│           ├── ai_agents/             # LangChain glue, kept out of HTTP layer
│           │   ├── base_agent.py      # ChatAnthropic wrapper (model = claude-sonnet-4-6)
│           │   ├── rag/               # embedding.py, retrieving.py, vector_store.py
│           │   ├── tavily/            # Tavily crawler client + response parsing
│           │   └── tools/             # LangChain @tool definitions (e.g. document_search_tool)
│           │
│           ├── constants/             # Cross-module constants (e.g. vector collection names)
│           │
│           └── migrations/            # Alembic
│               ├── env.py
│               └── versions/          # Add new revisions here; runs on every `up`
│
├── docker/
│   ├── Dockerfile.backend             # Backend image
│   ├── Dockerfile.migration           # One-shot migration runner
│   └── ollama-checker.sh              # Verifies Ollama on host before backend starts
│
├── docker-compose.yml                 # backend + pgvector + phoenix + db-migration + ollama-checker
├── Justfile                           # All dev commands (init, up-all, lint, format, …)
├── pyproject.toml                     # uv workspace root (members: apps/backend)
├── ruff.toml                          # Lint/format rules
├── scripts/                           # start-ollama.sh / stop-ollama.sh — DO NOT rename
├── docs/superpowers/                  # Historical plans + specs (read-only background)
└── CLAUDE.md                          # Guidance for Claude Code in this repo
```

### Conventions worth knowing

1. **Tests live beside source** as `*_test.py` (e.g. `server_test.py` next to
   `server.py`). There is no top-level `tests/` directory.
2. **New HTTP routes** go in a `*_controller.py` exposing a module-level
   `router`. `server_config/server.py` globs and registers them automatically —
   no manual wiring.
3. **Logging**: use `Logger(__name__)` from `server_config.logger`. Do not use
   stdlib `logging` or `print`.
4. **Chunk IDs** are `"{document_name}#{index}"`. `filter_pending_documents`
   and other lookups depend on this exact shape.
5. **uv workspace**: the only `.venv` lives at the repo root. Always
   `uv sync` from the root, never from `apps/backend`.
6. **Backend networking**: the `backend` service uses `network_mode: host` so
   it can reach Ollama on `localhost:11434`. If you change the network, also
   re-point `OLLAMA_BASE_URL`.
