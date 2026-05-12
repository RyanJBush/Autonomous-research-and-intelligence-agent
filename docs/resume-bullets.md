# Resume Bullets

ATS-friendly, one-line bullets describing this project (Astra AI / Europa — Autonomous Research & Intelligence Agent). Pick 2–4 that best match the role you are applying for.

## Headline (one-liner)
- Built an autonomous multi-step research agent in Python and FastAPI that decomposes natural-language queries, retrieves and scores sources, and outputs cited evidence-based reports.

## Autonomous agent / agentic systems
- Designed a five-stage agent pipeline (plan → search → extract → validate → synthesize) with per-stage tracing, retries, and per-role tool allowlists.
- Implemented a planner agent that decomposes free-form research questions into typed sub-question plans with expected source classes and per-step outputs.
- Built a tool registry that gates which pipeline stages each user role can invoke, providing a lightweight authorization layer for agent actions.

## NLP / summarization / information retrieval
- Implemented an extractive summarization and citation system that links each report claim back to a numbered source excerpt for traceability.
- Built a source credibility scorer combining domain authority, recency, corroboration bonus, and contradiction penalty into a single confidence score.
- Added a contradiction detector that flags conflicting claims across retrieved sources and surfaces severity in the final report.

## Evidence-based reporting / guardrails
- Authored a structured report schema (versioned, with provenance, evidence coverage, and unsupported-claim tracking) to reduce hallucination risk in agent output.
- Added PII redaction (emails, phone numbers, SSNs) and a per-workspace audit log to make agent runs auditable and compliance-friendly.
- Defined an evidence-coverage metric and unsupported-claim list so reports explicitly disclose where the agent did not find enough support.

## Backend / engineering
- Built a FastAPI backend with JWT auth, SQLAlchemy models, role-based access, research history, replay endpoint, and Markdown/JSON report export.
- Set up Docker Compose and GitHub Actions CI (ruff, pytest, frontend build) with 120+ passing backend tests covering planner, validator, reporting, and API contracts.
- Modeled research sessions, sources, citations, trace events, and agent run metrics in SQLAlchemy, enabling per-stage latency analysis and replay.

## Portfolio framing (recruiter-readable)
- Independently designed and shipped a portfolio-grade autonomous research assistant — agentic pipeline, evidence-cited reports, FastAPI backend, React frontend, Docker, and CI — as a University of Maryland Information Science student project.

## How to use these
- Pair one headline bullet with one or two stack-specific bullets (autonomous agent, NLP, or backend) depending on the job.
- Keep total project bullets to 3–5 per role on a resume; move the rest to a portfolio README or LinkedIn project entry.
- Quantify where you can in your own copy (e.g., "120+ passing tests", "five-stage pipeline") — the numbers in this doc are the ones currently true of the repo.
