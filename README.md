# Europa — Autonomous Research and Intelligence Agent

A portfolio demo of an AI-assisted research workflow that turns a query into a cited draft report.

## Recruiter-facing summary
I’m a **University of Maryland student studying Information Science and Electrical Engineering with a Business minor.** Europa is one of my portfolio projects focused on practical AI orchestration, backend API design, and transparent research reporting. It is built to demonstrate engineering decisions and communication quality in a realistic but demo-scale environment.

## What this project demonstrates
- Agent-style pipeline orchestration from user query to structured output
- Evidence-linked report generation with source tracking and validation signals
- FastAPI backend design with session lifecycle, traces, and export paths
- Honest AI product framing that separates demo behavior from real-world reliability

## Tech stack
- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React, Vite
- **Agent services:** planner, retrieval, summarization, validation, reporting modules
- **Demo tooling:** deterministic sample pipeline scripts and screenshot capture scripts

## Architecture overview
See `docs/architecture.md` for component boundaries, data flow, and service responsibilities.

## How to run locally
```bash
git clone https://github.com/RyanJBush/Autonomous-research-and-intelligence-agent.git
cd Autonomous-research-and-intelligence-agent
python scripts/demo_pipeline.py
```

## Demo workflow
1. Run `python scripts/demo_pipeline.py` for the deterministic portfolio demo flow.
2. Optionally run backend + frontend locally for UI walkthroughs.
3. Review generated report output and trace artifacts to inspect reasoning and citations.

## Screenshots / demo
See `docs/screenshots/README.md` and the captured images in `docs/screenshots/`:
- `01-query-input.png`
- `02-task-decomposition.png`
- `03-source-cards.png`
- `04-final-cited-report.png`
- `05-api-docs.png`
- `06-execution-timeline.png`

## Retrieval/search clarity
Retrieval is available in multiple modes:
- **Sample dataset-based demo:** `scripts/demo_pipeline.py` uses `data/sample/sample_sources.json` with no network calls.
- **Sample-backed local UI capture:** `backend/_europa_run.py` uses deterministic patched tools for repeatable screenshots.
- **Live web search via lightweight APIs:** default backend search can call **Wikipedia OpenSearch** and **DuckDuckGo Instant Answer**.

**Retrieval is sample dataset-based by default for portfolio demos, with optional live web search via Wikipedia OpenSearch and DuckDuckGo Instant Answer.**

## Limitations and future work
- Retrieval and synthesis results should be independently verified — this is a portfolio demo, not a fact-checking service.
- AI-generated research summaries may contain errors or hallucinations; human verification is required for any real-world use.
- Current live retrieval connectors are lightweight and may miss depth, recency, or source diversity compared with dedicated commercial search APIs.
- Future work: add richer retrieval adapters, stronger citation ranking controls, and deeper evaluation harnesses.

## Resume bullets
See `docs/resume-bullets.md`.

## License
MIT (see `LICENSE`).
