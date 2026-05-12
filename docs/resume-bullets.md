# Resume Bullets — Europa

- Built a research-assistant demo using FastAPI + React that executes a clear agent pipeline: query framing, retrieval, synthesis, and source-linked draft output.
- Implemented dual retrieval paths: deterministic static dataset mode for reproducible demos and optional live web API mode (Wikipedia OpenSearch + DuckDuckGo Instant Answer) for networked retrieval behavior.
- Designed traceable backend data flow with SQLAlchemy/PostgreSQL models for sessions, sources, summaries, citations, and execution events to support transparent run review.
- Added prompting and orchestration patterns that decompose broad questions into narrower sub-tasks before synthesis, improving source coverage and explainability.
- Documented limitations explicitly (hallucination risk, retrieval gaps, heuristic validation) and positioned the system as a student portfolio demo requiring human verification.
