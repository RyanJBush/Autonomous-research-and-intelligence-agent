# API Reference

FastAPI backend, mounted under `http://localhost:8000`. Interactive docs are auto-generated at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc:      `http://localhost:8000/redoc`

All `/api/*` routes except `/api/auth/login` require a Bearer JWT in the `Authorization` header. Roles `admin` and `researcher` can mutate research sessions; `admin` is required for audit-log access.

> ⚠️ **Outputs require human verification.** Every report endpoint returns heuristic confidence and evidence-coverage signals — they are *not* fact-checks. Do not use this API for decision-making without an independent review of the cited sources.

---

## Auth

### `POST /api/auth/login`

Exchange email + password for an access token. In local-dev mode, a previously unseen email auto-creates a user with role `researcher` (do not expose this to the public internet).

Request:
```json
{ "email": "user@example.com", "password": "..." }
```

Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Research lifecycle

### `POST /api/research`

Kick off a new research session. The agent runs **synchronously inside the request** and returns the final report. Long queries hold the connection — see the synchronous-execution caveat in `docs/architecture.md`.

Request:
```json
{
  "query": "Compare major cloud providers on enterprise AI governance offerings",
  "depth": 2,
  "breadth": 3,
  "recency_days": 30,
  "max_sources": 5,
  "allow_domains": [],
  "deny_domains": []
}
```

Response: `ResearchResult` — `research_id`, `summary`, `citations`, and the structured `report` (see `docs/architecture.md` for the schema).

### `POST /api/research/{research_id}/pause`
Pause a running session. Returns the updated `ResearchRead`.

### `POST /api/research/{research_id}/resume`
Resume a paused session.

### `POST /api/research/{research_id}/retry`
Retry a failed (or completed) session with the same parameters. Increments `version` and links via `parent_session_id`.

### `POST /api/research/{research_id}/refine`
Run a follow-up research session that links back to the original via `parent_session_id`. Useful for "go deeper on claim X" workflows.

---

## Research history and detail

### `GET /api/research`
List the current user's research sessions, most recent first.

### `GET /api/research/{research_id}`
Get full detail for one session: report, citations, sources, `requires_review` flag, and any reviewer reason.

### `GET /api/sources/{research_id}`
List the sources retrieved for a session, with credibility scores and metadata.

### `GET /api/memory/{research_id}`
List FAISS-backed vector-memory entries written during the session. The memory store is **in-process** — it does not persist across backend restarts.

---

## Observability

### `GET /api/research/{research_id}/trace`
Per-stage trace events: `planning`, `searching`, `extracting`, `validating`, `synthesizing`.

### `GET /api/research/{research_id}/metrics`
High-level metrics for the run: source count, average credibility, citation coverage, evidence coverage, fact-support ratio, contradiction rate, total and per-stage latency.

### `GET /api/research/{research_id}/agent-metrics`
Per-agent invocation metrics (planner, summarizer, validator, etc.).

### `GET /api/research/{research_id}/compliance`
PII redaction stats and the `review_required` flag for the run.

### `GET /api/research/{research_id}/replay`
Deterministic replay payload — the trace plus inputs needed to walk through the run after the fact.

---

## Workspaces and audit

### `GET /api/workspaces/current`
The active workspace for the current user.

### `GET /api/audit-logs`
Workspace-scoped audit log entries. **Requires `admin` role.** Returns at most the 200 most recent entries.

---

## Export

### `GET /api/research/{research_id}/export?format=markdown`

Export the structured report as Markdown or JSON.

- `?format=markdown` (default) — returns `text/markdown` rendered from the structured report.
- `?format=json` — returns the raw structured report as JSON.

Any other value returns `400 Unsupported export format`.

---

## Health

### `GET /health`
Liveness probe. Returns `{"status": "ok"}`. Used by the Docker Compose healthcheck.

---

## Notes and limitations

- **Synchronous agent execution.** `/api/research` does not return until the agent finishes. Long queries (tens of seconds) hold the HTTP connection. A real deployment would move the pipeline behind a job queue.
- **Search backend.** The default `SearchTool` calls Wikipedia OpenSearch and DuckDuckGo Instant Answer over the network. It is **not** a commercial search API (Brave / Tavily / SerpAPI). The text-only demo in `scripts/demo_pipeline.py` bypasses retrieval entirely and uses mock sources.
- **Summarization.** Default summarization is **extractive** (sentence selection). There is no LLM call wired into the default summarizer.
- **Daily quota.** Each user is rate-limited via `_enforce_daily_quota` (`backend/app/main.py`); exceeding the configured quota returns `429`.
- **Auth.** Demo-grade JWT. Local-dev mode auto-creates a user on first login. Not safe to expose publicly without further hardening.
- **Confidence & evidence-coverage are heuristics, not fact-checks.** Every output requires human verification.
