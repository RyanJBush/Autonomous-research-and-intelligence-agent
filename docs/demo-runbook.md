# Europa — Demo Runbook

This runbook presents Europa as a **research-agent prototype** for portfolio/interview review.

> **Mandatory framing in demos:** outputs are drafts for human review, not guaranteed truth.

## Demo path A (recommended): deterministic sample-data run
```bash
python scripts/demo_pipeline.py
```
- Uses `data/sample/sample_sources.json`.
- No live network retrieval.
- Best for predictable, repeatable demonstration.

## Demo path B: full local stack
```bash
docker compose up --build
```
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

In this mode, retrieval behavior depends on configured backend runtime (sample-backed patch vs live lightweight search tool).

## Live narration checklist
1. Query decomposition (planner output)
2. Source retrieval context (state if sample/live/stubbed)
3. Evidence + contradictions panels
4. Confidence rationale as heuristic, not guarantee
5. Export + trace/replay endpoints for auditability

## Talking points for honesty + strength
- Strong: orchestration, traceability, schema design, backend/API engineering, docs quality.
- Honest limits: retrieval breadth, heuristic scoring, synchronous execution, required human validation.

## Pre-demo checks
```bash
make lint
make test
```

## Fallback guidance
If live retrieval is noisy/empty, switch to sample-data mode and explicitly say: “This run is deterministic sample data to demonstrate workflow mechanics and report structure.”
