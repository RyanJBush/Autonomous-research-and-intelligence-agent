# Screenshots

This directory holds UI screenshots used by the project README and recruiter walkthrough.

> The text-only demo (`python scripts/demo_pipeline.py`) does not require screenshots — it prints the agent's I/O directly to the terminal. Screenshots are for the full UI walkthrough only.

---

## Files in this directory

| File | What it shows | Captured from |
|---|---|---|
| `01-query-input.png` | Research Query page: prompt textarea, breadth / depth / max-sources controls, recency-days input, allow/deny domain inputs, plan preview, submit button | `http://localhost:5173/research` |
| `02-task-decomposition.png` | Research plan section — per-step sub-question and expected source types — rendered alongside source citations | Research Results page, "Research plan" panel |
| `03-source-cards.png` | Evidence table panel — one card per retrieved source with title, type, and credibility score — next to the contradictions panel | Research Results page, "Evidence table" panel |
| `04-final-cited-report.png` | Executive summary with confidence badge, findings list with per-claim confidence and support markers, refine-and-rerun control, sources/coverage/support-ratio metric cards | Research Results page, top of page |
| `05-api-docs.png` | Auto-generated FastAPI Swagger UI listing all `/api/*` endpoints | `http://localhost:8000/docs` |
| `06-execution-timeline.png` | Per-stage execution trace (`planning`, `searching`, `extracting`, `validating`, `synthesizing`, `complete`) with status and per-event latency | Research Results page, "Execution trace" panel |

> Captured automatically via Playwright against the included sample dataset (`data/sample/sample_sources.json`) so the figures shown are reproducible. See `scripts/_capture_screenshots.py` for the capture flow and `backend/_europa_run.py` for the local-only runner that swaps the live retrieval tools for the sample data (Wikipedia/DuckDuckGo are unreliable without an API key/UA, and the goal here is an honest representation of the UI, not a live retrieval demo).

---

## How to re-capture

Two paths.

**Automated (recommended):**

```bash
# Terminal 1 — patched backend (sample-data tools, CORS open for local vite)
python backend/_europa_run.py

# Terminal 2 — frontend
cd frontend && npm ci && npm run dev -- --port 5773

# Terminal 3 — capture
python scripts/_capture_screenshots.py
```

The capture script logs in as `demo@europa.dev / demo123` (auto-created on first login by the patched backend), runs the suggested prompt, waits for the pipeline to complete, and writes all six PNGs into this directory.

**Manual:**

1. Bring the full stack up: `docker compose up --build` (see `docs/demo-runbook.md`).
2. Run the suggested prompt: *"Compare major cloud providers on 2026 enterprise AI governance offerings."*
3. Wait for the full pipeline to finish (the synthesizing stage will mark completion).
4. Take the screenshots above. Recommended resolution: 1440×900 or larger; PNG; light theme for legibility.
5. Save them in this directory with the filenames listed above so the README references resolve.

---

## Style guidance

- Crop to the relevant panel — full-window screenshots with unused chrome are harder to scan in a README.
- Redact any auto-generated user email or workspace name if you ran with a personal address.
- Do **not** stage edited results to make the output look stronger than it is. The whole point of this project is honest framing.
- Keep file sizes reasonable (≤ ~400 KB each). Use `pngquant` or `oxipng` if needed.

---

## Honesty notes

- Screenshots age every time the UI changes — they are committed for portfolio review but are expected to drift. If you find them stale, the text-only demo (`scripts/demo_pipeline.py`) plus the architecture doc are sufficient to evaluate the work.
- The captures use the **mock** sample sources in `data/sample/sample_sources.json` (domains end in `.test`). Live retrieval against Wikipedia/DuckDuckGo without an API key/UA yields empty results, so we patch in deterministic sample data rather than ship screenshots of a broken-looking empty state. The pipeline itself (planner → search → scraper → validator → summarizer → citations → reporting) runs unchanged.
