# Europa — Architecture

Europa (legacy name: Astra AI) is an autonomous research-and-intelligence agent built as a **student portfolio project**. This document describes the pipeline, the trust/report model, and the deliberate honesty constraints on the agent's output.

> **Important:** Every claim below is grounded in the current repo. Anything the agent produces — confidence scores, evidence-coverage metrics, contradiction flags — is a heuristic over retrieved text and **requires human verification** before any decision-making use. Europa is not a fact-checker.

---

## 1. System overview

- **Backend** — FastAPI service with JWT auth, a role field on `User` (admin / researcher / viewer-style gating via `require_role`), SQLAlchemy models, and the research pipeline.
- **Agent pipeline (five stages)** — planner → search → scrape → validate → summarize / citations, with FAISS-backed memory writes at the end. Each stage emits a `ResearchTraceEvent` and, for the LLM-style agents, an `AgentRunMetric`.
- **Frontend** — React 19 + Vite + Tailwind (JSX, **not** TypeScript) with pages for login, dashboard, query, results, source viewer, and settings.
- **Infra** — Dockerized backend and frontend, PostgreSQL 16 via `docker-compose.yml`, GitHub Actions CI (ruff, mypy non-blocking, pytest, frontend lint + build).

---

## 2. Pipeline stages

| Stage | Service | Responsibility |
|---|---|---|
| **Plan** | `services/planner.py` (`PlannerAgent`) | Decomposes a free-form query into typed sub-questions with objectives, expected source classes, and per-step outputs. |
| **Search** | `services/search.py` (`SearchTool`) | Calls Wikipedia OpenSearch + DuckDuckGo Instant Answer API and returns up to five deduplicated URLs. See the note in §5 about what this is and is not. |
| **Extract** | `services/scraper.py` | Fetches content for retrieved URLs. |
| **Validate** | `services/validator.py` | Scores each source's credibility (domain authority, recency, citation signals), detects contradictions across sources, and tracks evidence coverage and unsupported claims. |
| **Synthesize** | `services/summarizer.py` + `services/citations.py` + `services/reporting.py` | Builds an extractive summary, links each finding to a numbered source excerpt, and assembles a versioned structured report. |

Orchestration lives in `services/research_service.py` (`ResearchService.run`).

### Auxiliary services

- `services/tool_registry.py` — a per-role tool allowlist gating which pipeline tools each user role can invoke.
- `services/pii_redactor.py` — regex-based redaction of emails, phone numbers, and US SSNs; redaction counts surface via the compliance endpoint.
- `services/memory_store.py` — FAISS-backed in-process vector store; written to at the end of a run and exposed via `/api/memory/{research_id}`.

---

## 3. Trust and report model

The structured report (built by `services/reporting.py`) is intentionally **transparent rather than authoritative**. Its job is to make it easy for a human reader to see *what is supported, by what, and how confidently* — not to declare facts.

Top-level fields:

- `schema_version` — bump on breaking changes.
- `provenance` — `generated_at`, `pipeline_version`, query metadata.
- `findings` — narrative findings, each one linkable to claims.
- `claims` — atomic statements extracted from the synthesis.
- `claim_evidence_links` — explicit (claim → source excerpt) edges.
- `evidence_coverage` — count of supported vs. unsupported claims and a sufficiency threshold.
- `contradictions` — pairs of conflicting claims with a `severity` field.
- `unsupported_claims` — claims with no evidence link; surfaced rather than hidden.
- `compliance` — PII redaction counts.

### Confidence scoring (componentized)

The final confidence number is **not** a single opaque score. It is decomposed and the breakdown is surfaced in the report:

```
confidence = base_credibility
           + corroboration_bonus
           + recency_bonus
           - contradiction_penalty
```

- `base_credibility` — per-source signal from `validator.py` (domain authority + source-type heuristics).
- `corroboration_bonus` — count of independent sources supporting the same claim.
- `recency_bonus` — bounded bonus for fresh sources.
- `contradiction_penalty` — applied when conflicting claims are detected.

This is a **heuristic**. It is not a calibrated probability and it is not a fact-check. A high confidence number means "multiple credible-looking, recent, non-contradictory sources said this" — it does not mean the claim is true.

---

## 4. Observability

Every research run emits:

- A `ResearchTraceEvent` per pipeline stage (planning, searching, extracting, validating, synthesizing) with timestamps. Exposed via `/api/research/{id}/trace`.
- An `AgentRunMetric` per agent invocation (planner, summarizer, validator, etc.). Exposed via `/api/research/{id}/agent-metrics`.
- A `Source` row per retrieved URL, with credibility score and metadata.
- A `Citation` row per (finding → source excerpt) link.
- A `Summary` row with the structured report JSON.

A deterministic **replay** payload (`/api/research/{id}/replay`) combines the trace events with the inputs so a run can be walked through after the fact.

---

## 5. Search backend — what it actually is

This is the most-overstated part of agentic-system READMEs in general, so it is called out explicitly here:

- The default `SearchTool` (`services/search.py`) makes live HTTP calls to **Wikipedia OpenSearch** and the **DuckDuckGo Instant Answer API**, deduplicates the URLs, and returns up to five.
- It is **not** Brave Search, Tavily, SerpAPI, Google Custom Search, or any other commercial retrieval API. Wiring those in is listed as future work.
- The DuckDuckGo Instant Answer API in particular returns *abstract pages and related topics*, not a general web-search result set; coverage is shallow on long-tail queries.
- The `scripts/demo_pipeline.py` demo bypasses `SearchTool` entirely and runs against the mock sources in `data/sample/sample_sources.json`. The demo never touches the network.

If a recruiter or interviewer asks "is this hitting the open web?" — the honest answer is "it can, against two free APIs, but the depth and quality of those APIs is the cap on the agent's research, and the included demo runs against fixtures."

---

## 6. Frontend

- React 19 + Vite + Tailwind. Single-file SPA in `frontend/src/App.jsx` with React Router routes for Login / Dashboard / Research Query / Research Results / Source Viewer / Settings.
- Surfaces confidence rationale, contradiction severity, and the per-stage execution timeline from `/api/research/{id}/trace`.
- Source viewer exposes author / published / retrieved metadata for explainability.
- **Not** TypeScript (despite earlier copy). Migration to TS is on the future-work list.

---

## 7. Demo-readiness notes

- `python scripts/demo_pipeline.py` is the canonical text-only demo. It runs in under five seconds and requires no setup beyond cloning the repo.
- The full UI demo is in `docs/demo-runbook.md`.
- A pre-run completed session in Dashboard is the recommended fallback if a live network retrieval is noisy.

---

## 8. What this architecture is *not*

- Not production-grade.
- Not a fact-checker — confidence scoring is a heuristic, not a probability of truth.
- Not a real-time system — the agent runs synchronously inside the HTTP request.
- Not a substitute for human review — the report's purpose is to make verification *cheaper*, not to skip it.

See the README's **Limitations** table for the short-form version of these caveats.
