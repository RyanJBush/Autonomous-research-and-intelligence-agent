# Europa — Autonomous Research and Intelligence Agent

Europa is a **research-agent prototype** built for portfolio and interview review. It demonstrates agent orchestration, evidence-linked reporting, backend engineering, and technical documentation quality.

> **Honesty contract:** Europa does not guarantee factual correctness. Confidence/evidence signals are heuristic. Every output requires human verification before use.

## What this repo is
- A student-built, end-to-end agent workflow: **plan → search/retrieve → extract → validate → synthesize**.
- A FastAPI + SQLAlchemy + Postgres backend with run tracing, metrics, replay, and export.
- A React UI for query input, source inspection, contradictions, and report review.
- A deterministic demo path with sample data for reliable walkthroughs.

## Retrieval modes (explicit)
Europa supports different retrieval contexts depending on how you run it:

1. **Sample-data mode (recommended demo)**
   - `python scripts/demo_pipeline.py`
   - Uses `data/sample/sample_sources.json` only.
   - No network calls.
2. **Local screenshot/demo mode**
   - `python backend/_europa_run.py`
   - Uses patched local tools with deterministic sample data for UI capture.
3. **Live lightweight retrieval mode**
   - Default backend `SearchTool` can call Wikipedia OpenSearch and DuckDuckGo Instant Answer.
   - Coverage/quality are limited and not equivalent to production search APIs.

## Quickstart
```bash
git clone https://github.com/RyanJBush/Autonomous-research-and-intelligence-agent.git
cd Autonomous-research-and-intelligence-agent
python scripts/demo_pipeline.py
```

## Documentation map
- Architecture: `docs/architecture.md`
- API docs: `docs/api.md`
- Demo runbook: `docs/demo-runbook.md`
- Resume bullets: `docs/resume-bullets.md`
- Screenshot guide: `docs/screenshots/README.md`

## Evaluation framing
Use this repo to evaluate:
- agent pipeline decomposition and orchestration,
- evidence-linked reporting design,
- backend/API quality and testing,
- technical writing clarity and honesty in system claims.

Do **not** evaluate it as a production fact-checking system.
