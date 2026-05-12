# Screenshots

This directory holds UI screenshots used by the project README and recruiter walkthrough. Files are intentionally committed as **placeholders** until a maintainer captures them from a running local stack.

> The text-only demo (`python scripts/demo_pipeline.py`) does not require screenshots — it prints the agent's I/O directly to the terminal. Screenshots are for the full UI walkthrough only.

---

## Expected files

| File | What it should show | Capture from |
|---|---|---|
| `01-query-input.png` | Research Query page: prompt textarea, breadth / depth / recency controls, allow/deny domain inputs, submit button | `http://localhost:5173` → "New Research" |
| `02-task-decomposition.png` | Sub-question plan rendered before retrieval begins — one row per planned sub-question with objective | Research Results page, top of the page, during/after planning |
| `03-source-cards.png` | Retrieved sources rendered as cards with credibility score, domain, recency, and excerpt | Research Results page, "Sources" section |
| `04-final-cited-report.png` | Final report: findings, confidence rationale breakdown, contradiction flags, evidence table | Research Results page, "Report" section |
| `05-api-docs.png` | Auto-generated FastAPI Swagger UI | `http://localhost:8000/docs` |

A 6th optional capture: `06-execution-timeline.png` — the per-stage timeline (`planning`, `searching`, `extracting`, `validating`, `synthesizing`) with latency markers.

---

## How to capture

1. Bring the stack up: `docker compose up --build` (see `docs/demo-runbook.md`).
2. Run the suggested prompt: *"Compare major cloud providers on 2026 enterprise AI governance offerings."*
3. Wait for the full pipeline to finish (the synthesizing stage will mark completion).
4. Take the screenshots above. Recommended resolution: 1440×900 or larger; PNG; light theme for legibility.
5. Save them in this directory with the exact filenames listed above so the README references resolve.

---

## Style guidance

- Crop to the relevant panel — full-window screenshots with unused chrome are harder to scan in a README.
- Redact any auto-generated user email or workspace name if you ran with a personal address.
- Do **not** stage edited results to make the output look stronger than it is. The whole point of this project is honest framing.
- Keep file sizes reasonable (≤ ~400 KB each). Use `pngquant` or `oxipng` if needed.

---

## Why these are placeholders

The repository is feature-complete for its stated scope, but screenshots are a maintenance burden — they age every time the UI changes. They are captured fresh before any portfolio submission rather than checked in long-term.

If you are reviewing this repo and the screenshots are missing or stale, the text-only demo (`scripts/demo_pipeline.py`) plus the architecture doc are sufficient to evaluate the work.
