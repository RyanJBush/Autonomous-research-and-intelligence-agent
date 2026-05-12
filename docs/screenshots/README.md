# Europa Screenshots

This folder contains UI screenshots for **portfolio/design review** of Europa.

## Current screenshot set
- [x] `01-query-input.png` — query input state
- [x] `02-task-decomposition.png` — planning/decomposition view
- [x] `03-source-cards.png` — retrieved source cards
- [x] `04-final-cited-report.png` — synthesized draft report
- [x] `05-api-docs.png` — backend API docs (FastAPI)
- [x] `06-execution-timeline.png` — trace/event timeline

## Retrieval context disclosure
These images show local demo behavior. Depending on runtime mode, retrieval is either:
- **Static sample data** (deterministic), or
- **Live lightweight API search** (Wikipedia OpenSearch + DuckDuckGo Instant Answer).

Screenshots are meant to show UX and pipeline flow, not guaranteed factual quality.

## TODO when refreshing screenshots
- [ ] Capture one run labeled “Static sample-data mode”
- [ ] Capture one run labeled “Live API retrieval mode”
- [ ] Confirm disclaimer visibility in report/output screens

## How to recapture
Use `scripts/_capture_screenshots.py` after starting the local stack described in `docs/demo-runbook.md`.
