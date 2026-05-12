# Resume Bullets — Europa (Autonomous Research and Intelligence Agent)

Use 3–5 bullets per application. These are written to be strong for AI agent, backend, research workflow, and technical writing roles while remaining accurate.

## AI agent / research workflow
- Built a research-agent prototype in Python/FastAPI that decomposes open-ended questions into a staged workflow (plan → retrieve → extract → validate → synthesize) and produces citation-linked reports.
- Implemented transparent trust heuristics (credibility, corroboration, recency, contradiction) plus unsupported-claim tracking to make agent output auditable for human reviewers.
- Designed deterministic sample-data demo paths for reliable evaluation of agent behavior independent of external search volatility.

## Backend / platform
- Developed a FastAPI + SQLAlchemy + PostgreSQL backend with JWT auth, role-aware tool access, research-session lifecycle endpoints, trace/metrics APIs, replay payloads, and markdown/json export.
- Modeled research artifacts (sessions, sources, citations, summaries, trace events, agent metrics) to support observability and post-run analysis.

## Technical writing / documentation
- Authored architecture, API, runbook, and screenshot documentation that explicitly separates live retrieval from sample/stubbed modes and states human-verification requirements.
- Wrote limitation-first documentation to avoid overclaiming factual reliability, improving trust and reviewer clarity.

## Honest interview framing
- “Europa is a research-agent prototype for structured evidence gathering and analysis support; it is not a guaranteed fact-checker, and outputs require human verification.”
