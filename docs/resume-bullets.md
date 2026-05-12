# Resume Bullets — Europa

ATS-friendly one-line bullets describing this project (Europa, internal/legacy name Astra AI — Autonomous Research & Intelligence Agent). Pick 3–5 that best match the role you are applying for.

Every bullet below is grounded in the current repo state. Numeric claims (`five-stage pipeline`, `120 backend test functions`) are verified, not aspirational.

---

## Headline (one-liner)

- Built an autonomous multi-step research agent in Python and FastAPI that decomposes natural-language queries, retrieves and scores sources, and produces cited evidence-based reports — as a student portfolio project.

---

## Autonomous agent / agentic systems

- Designed a five-stage agent pipeline (plan → search → extract → validate → synthesize) with per-stage tracing, retries, and per-agent invocation metrics for explainability.
- Implemented a planner agent that decomposes free-form research questions into typed sub-question plans with objectives, expected source classes, and per-step outputs.
- Built a per-role tool registry that gates which pipeline tools each user role can invoke, providing a lightweight authorization layer for agent actions.
- Added a deterministic replay endpoint that reconstructs any prior research run from its trace events and inputs.

---

## NLP / summarization / information retrieval

- Implemented an extractive summarization and citation system that links each report claim back to a numbered source excerpt for traceability.
- Built a source-credibility scorer combining domain authority, recency, corroboration bonus, and contradiction penalty into a transparent confidence rationale (not a single opaque score).
- Added a contradiction detector that flags conflicting claims across retrieved sources and surfaces severity in the final report.
- Integrated a FAISS-backed in-process vector memory store written per session and queryable via the API.

---

## Evidence-based reporting / guardrails

- Authored a versioned structured-report schema (provenance, evidence coverage, claim-to-evidence links, and unsupported-claim tracking) to make agent output auditable and reduce hallucination risk.
- Added PII redaction (emails, phone numbers, SSNs) and a per-workspace audit log to make agent runs auditable and compliance-friendly.
- Defined an evidence-coverage metric and unsupported-claim list so reports explicitly disclose where the agent did not find enough support — instead of hiding it.

---

## Backend / engineering

- Built a FastAPI backend with JWT auth, SQLAlchemy, PostgreSQL, role-based access, research history, replay endpoint, daily quota enforcement, and Markdown/JSON report export.
- Wrote 120 backend test functions covering planner, validator, reporting, services, and API contracts; integrated ruff, mypy (non-blocking), eslint, and prettier in GitHub Actions CI.
- Modeled research sessions, sources, citations, trace events, agent run metrics, workspaces, and audit logs in SQLAlchemy, enabling per-stage latency analysis and replay.
- Shipped a Dockerized local stack (Postgres 16 + FastAPI backend + React frontend) with health-check-gated service startup.

---

## Frontend

- Built a React 19 + Vite + Tailwind research interface (JSX) with query input, sub-task plan view, source credibility cards, evidence table, contradictions panel, execution timeline, and Markdown/JSON export.

---

## Portfolio framing (recruiter-readable)

- Independently designed and shipped a portfolio-grade autonomous research agent — agentic pipeline, evidence-cited reports, FastAPI backend, React UI, Docker, and CI — as a University of Maryland Information Science student project, with explicit limitations documented alongside the code.

---

## How to use these

- Pair the headline bullet with one or two stack-specific bullets (agent, NLP, backend, or frontend) depending on the role.
- Keep total project bullets to 3–5 per role on a resume; move the rest to a portfolio README or LinkedIn project entry.
- Quantify only with numbers that are still true of the repo (`five-stage pipeline`, `120 backend test functions`). Update the count before reusing if the repo changes.

---

## Honest framing for interviews

- This is a **student portfolio project**, not a product. Outputs require human verification — describe it as a tool for making evidence-based research *cheaper* to do, not as a fact-checker.
- The default `SearchTool` calls Wikipedia + DuckDuckGo Instant Answer, not Brave/Tavily/SerpAPI. The packaged demo uses mock data.
- Frontend is JSX, not TypeScript — describe accurately if a JD asks for TS.
