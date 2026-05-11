# API Reference

FastAPI backend, mounted under `http://localhost:8000`. Interactive docs are available at `/docs` (Swagger) and `/redoc` once the backend is running.

All `/api/*` routes except `/api/auth/login` require a Bearer JWT in the `Authorization` header.

## Auth

### POST `/api/auth/login`
Exchange email + password for an access token.

Request:
```json
{ "email": "user@example.com", "password": "..." }
```

Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

## Research lifecycle

### POST `/api/research`
Kick off a new research session. The agent runs synchronously and returns the final report.

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

Response: `ResearchResult` — research session metadata, summary, citations, and structured report.

### POST `/api/research/{research_id}/pause`
Pause a running session. Returns the updated `ResearchRead`.

### POST `/api/research/{research_id}/resume`
Resume a paused session.

### POST `/api/research/{research_id}/retry`
Retry a failed session with the same parameters.

### POST `/api/research/{research_id}/refine`
Run a follow-up research session that links back to the original via `parent_session_id`. Useful for "go deeper on claim X" workflows.

## Research history and detail

### GET `/api/research`
List the current user's research sessions (most recent first).

### GET `/api/research/{research_id}`
Get full detail for one session: report, citations, sources, and metadata.

### GET `/api/sources/{research_id}`
List the sources retrieved for a session, with credibility scores and metadata.

### GET `/api/memory/{research_id}`
List vector-memory entries written during the session (FAISS-backed in-process store).

## Observability

### GET `/api/research/{research_id}/trace`
Per-stage trace events: `planning`, `searching`, `extracting`, `validating`, `synthesizing`.

### GET `/api/research/{research_id}/metrics`
High-level metrics for the run (latency per stage, source counts, evidence coverage).

### GET `/api/research/{research_id}/agent-metrics`
Per-agent invocation metrics (planner, summarizer, validator, etc.).

### GET `/api/research/{research_id}/compliance`
PII redaction stats and other compliance signals for the run.

### GET `/api/research/{research_id}/replay`
Deterministic replay payload — the trace plus inputs needed to walk through the run after the fact.

## Workspaces and audit

### GET `/api/workspaces/current`
The active workspace for the current user.

### GET `/api/audit-logs`
Workspace-scoped audit log entries.

## Export

### GET `/api/research/{research_id}/export?format=markdown`
Export the report as Markdown or JSON (`format=json`).

## Health

### GET `/health`
Liveness probe. Returns `{"status": "ok"}`.

## Notes and limitations

- The backend runs the agent **synchronously** inside the request. Long queries can hold the connection for tens of seconds; in a real deployment you would move this behind a job queue.
- Source retrieval defaults to a stubbed/sample search tool in local development. Live web search requires wiring an API key into `SearchTool` — see `backend/app/services/search.py`.
- The report includes a confidence score and evidence-coverage metric, but the **outputs are not guaranteed factually correct** and require human verification before any decision-making use.
