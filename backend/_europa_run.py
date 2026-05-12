"""Run backend with SearchTool/Scraper patched to use local sample sources.

Used for local UI walkthroughs / screenshot capture. Wikipedia returns 403 to
unauthenticated requests and DuckDuckGo's instant-answer API returns redirect
shells with no scrapeable content, so live retrieval yields empty results.
Patching against `data/sample/sample_sources.json` gives the existing pipeline
realistic source payloads to plan/extract/validate/synthesize against.

Not wired into the normal startup path. Invoke manually:

    python backend/_europa_run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "backend"))

SAMPLE = json.loads((REPO / "data/sample/sample_sources.json").read_text())
SOURCES = SAMPLE["sources"]
URL_TO_SOURCE = {s["url"]: s for s in SOURCES}

class _SampleSearchTool:
    def search(self, query):  # noqa: ARG002
        return [s["url"] for s in SOURCES]


class _SampleScraper:
    def extract(self, url):
        s = URL_TO_SOURCE.get(url)
        if not s:
            raise ValueError(f"unknown sample url {url}")
        content = s["content"]
        if len(content) < 1200:
            content = content + " " + (
                "This document discusses enterprise AI governance with concrete examples and "
                "practical recommendations for cloud customers evaluating model lifecycle "
                "controls, audit requirements, and operational risk. " * 4
            )
        return s["title"], content


from app.services import research_service as rs_module  # noqa: E402
from app.services import scraper as scraper_module  # noqa: E402
from app.services import search as search_module  # noqa: E402

search_module.SearchTool = _SampleSearchTool
scraper_module.Scraper = _SampleScraper
rs_module.SearchTool = _SampleSearchTool
rs_module.Scraper = _SampleScraper

import uvicorn  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.main import app  # noqa: E402

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8100, log_level="info")
