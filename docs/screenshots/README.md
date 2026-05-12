# Screenshots — Europa

This folder contains screenshots for presenting **Europa — Autonomous Research and Intelligence Agent**.

## Integrity requirements
When sharing screenshots, always disclose the retrieval mode used:
- **Sample-data/stubbed** capture (deterministic)
- **Live lightweight retrieval** capture (Wikipedia/DDG Instant Answer)

Never imply screenshots are proof of factual correctness. They show UI/reporting behavior only.

## Current files
- `01-query-input.png`
- `02-task-decomposition.png`
- `03-source-cards.png`
- `04-final-cited-report.png`
- `05-api-docs.png`
- `06-execution-timeline.png`

## Capture workflow (recommended)
```bash
# Terminal 1
python backend/_europa_run.py

# Terminal 2
cd frontend && npm ci && npm run dev -- --port 5773

# Terminal 3
python scripts/_capture_screenshots.py
```

This capture path is deterministic and uses sample-backed behavior for reproducibility.

## Caption template (use in README/portfolio)
“Screenshots captured from Europa’s local demo workflow. Depending on runtime, retrieval may use deterministic sample data or lightweight live APIs; outputs are heuristic and require human verification.”
