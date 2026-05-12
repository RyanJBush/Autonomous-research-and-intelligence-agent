# Europa API Reference

Base URL (local): `http://localhost:8000`

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

> **Reliability note:** API responses include heuristic quality signals, not guaranteed fact-checking. Outputs require human verification.

## Auth
### `POST /api/auth/login`
Returns bearer JWT for API access.

## Research lifecycle
### `POST /api/research`
Creates and executes a research session (synchronous in-request execution).

### `POST /api/research/{id}/pause`
Pause run.

### `POST /api/research/{id}/resume`
Resume run.

### `POST /api/research/{id}/retry`
Re-run with original parameters (versioned lineage).

### `POST /api/research/{id}/refine`
Run a follow-up session linked to the parent research id.

## Research retrieval modes (behavioral context)
When you interpret API output, account for backend mode:
- **Sample/stubbed mode** (used by `backend/_europa_run.py`): deterministic sample-backed results.
- **Default live lightweight mode**: Wikipedia OpenSearch + DuckDuckGo Instant Answer.

This mode distinction materially affects source breadth and freshness.

## Research read APIs
- `GET /api/research`
- `GET /api/research/{id}`
- `GET /api/sources/{research_id}`
- `GET /api/memory/{research_id}`

## Observability
- `GET /api/research/{id}/trace`
- `GET /api/research/{id}/metrics`
- `GET /api/research/{id}/agent-metrics`
- `GET /api/research/{id}/compliance`
- `GET /api/research/{id}/replay`

## Export
### `GET /api/research/{id}/export?format=markdown|json`
Exports structured report in markdown or json.

## Admin/workspace
- `GET /api/workspaces/current`
- `GET /api/audit-logs` (admin)

## Health
- `GET /health`

## Implementation caveats
- Synchronous execution can increase request latency for deep queries.
- Retrieval quality depends on backend mode (sample vs live lightweight APIs).
- Confidence/evidence metrics are decision-support signals, not proof.
