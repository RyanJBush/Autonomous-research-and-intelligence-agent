# Europa — Demo Runbook

End-to-end walkthrough for evaluating this project: a 2-minute no-setup path, a full local-stack path, and an operator checklist with fallbacks. Targets: hiring managers, technical recruiters, and engineering interview panels.

> Every output shown below — confidence scores, evidence-coverage metrics, contradiction flags — is a heuristic and **requires human verification**. Europa is not a fact-checker; it is a tool for making verification cheaper.

---

## Path A — 2-minute text-only demo (no setup)

The lowest-friction path. No Docker, no API keys, no database, no network.

```bash
git clone https://github.com/RyanJBush/Autonomous-research-and-intelligence-agent.git
cd Autonomous-research-and-intelligence-agent
python scripts/demo_pipeline.py
```

What you should see (against `data/sample/sample_sources.json` — mock data, not live retrieval):

1. The original query.
2. A multi-step plan from `PlannerAgent` — each sub-question with an objective.
3. A source credibility table (domain, type, score) from the mock sources.
4. Numbered citation excerpts from `CitationSystem`.
5. A short extractive summary preview from `SummarizationAgent`.

Total runtime: under five seconds. Exit code `0` on success.

---

## Path B — Full local stack (Docker Compose)

```bash
docker compose up --build
# Backend Swagger UI: http://localhost:8000/docs
# Frontend SPA:       http://localhost:5173
```

Health checks gate startup:

- `postgres` must be healthy before `backend` starts.
- `backend` must respond on `/health` before `frontend` starts.

Stop with `docker compose down` (add `-v` to wipe the Postgres volume).

---

## Path C — Manual local development

Backend:
```bash
cd backend
pip install -e .[dev]
cp .env.example .env       # set ASTRA_JWT_SECRET to anything non-default
uvicorn app.main:app --reload
```

Frontend (in a separate shell):
```bash
cd frontend
cp .env.example .env       # VITE_API_BASE defaults to http://localhost:8000
npm ci
npm run dev
```

---

## Pre-flight: preconditions

- Python 3.11+
- Node 22+
- Docker + Docker Compose (only for Path B)

---

## Live UI walkthrough (8–12 minutes)

### Narrative arc

1. **Problem framing** — research-style questions need multiple sources, traceable citations, and an honest confidence signal — not a single LLM monologue.
2. **Run a query** — show configurable controls and submit.
3. **Trust and evidence** — findings, confidence rationale, contradictions, source metadata.
4. **Operational credibility** — execution timeline, metrics, report export.
5. **Engineering quality** — 120 tests, CI, reproducible local setup.

### Suggested prompt

> Compare major cloud providers on 2026 enterprise AI governance offerings.

### Live steps

1. **Login** — open `http://localhost:5173`. Local-dev mode auto-creates the user on first login.
2. **Dashboard** — show prior sessions and history.
3. **Research Query page** — choose the suggested prompt, optionally set recency / allow-deny domains, submit.
4. **Research Results page** — highlight:
   - Confidence badges and the **rationale breakdown** (base credibility + corroboration + recency − contradiction).
   - The evidence table and its filtering.
   - Contradiction severity tags.
   - Execution timeline with per-stage latency markers (`planning`, `searching`, `extracting`, `validating`, `synthesizing`).
5. **Source Viewer** — open from a citation; inspect author / published / retrieved metadata.
6. **Export** — download Markdown and JSON renders of the same structured report.
7. **Swagger UI** — visit `http://localhost:8000/docs` to show the API surface.

### Talking points (technical depth)

- Pipeline stages: planning → searching → extracting → validating → synthesizing.
- Trust signals:
  - evidence coverage thresholds
  - unsupported-claim tracking
  - contradiction severity
  - provenance metadata (`schema_version`, `pipeline_version`, `generated_at`)
- Governance:
  - PII redaction (emails, phone numbers, SSNs)
  - per-workspace audit logs
  - daily research quota enforced at the API layer
- Search reality check: default `SearchTool` calls Wikipedia OpenSearch + DuckDuckGo Instant Answer. **Not** Brave / Tavily / SerpAPI.

---

## Verification checklist

1. `GET /health` returns `{"status":"ok"}`.
2. UI loads at `http://localhost:5173`.
3. Login succeeds (any email/password in local mode).
4. A submitted query produces a results page with: findings, evidence table, contradictions panel, timeline events.
5. Source viewer shows source metadata and content.
6. Markdown and JSON export downloads succeed.

---

## Quality gates before demo

```bash
make smoke
```

Runs:

- backend lint (`ruff check`)
- backend tests (`pytest -q`)
- frontend lint (`eslint`)
- frontend format check (`prettier --check`)
- frontend build (`vite build`)

Individual gates: `make lint`, `make test`.

---

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Backend import errors | Editable install was skipped | `cd backend && pip install -e .[dev]` |
| Login fails | Stale token in browser storage | Clear `astra_token` from local storage and re-login |
| Empty results from a query | No outbound network for `SearchTool` | Use the pre-canned session in Dashboard, or run Path A demo |
| Frontend can't reach API | `VITE_API_BASE` mismatch | Confirm it points to `http://localhost:8000` |
| `429` from `/api/research` | Daily quota tripped | Wait, or raise `daily_research_quota` in config |
| Docker compose hangs on first run | Postgres healthcheck still warming up | Wait ~10s; backend retries until healthy |

---

## Demo stability tips

- Use one of the three demo prompts hard-coded in the UI (`DEMO_QUERIES` in `frontend/src/App.jsx`) to reduce prep time.
- Keep one pre-run completed session in Dashboard as a fallback if a live retrieval is noisy.
- Pre-export one Markdown and one JSON report ahead of time as backup artifacts.
- If wifi is unreliable, default to Path A — it never touches the network.

---

## Honest framing

This is a **student portfolio project**. The right framing on a call is "here is how I think about agent design, evidence-based reporting, and full-stack engineering — runnable end-to-end, transparent in its limitations." It is not a product, it is not deployed, and its outputs must be verified.
