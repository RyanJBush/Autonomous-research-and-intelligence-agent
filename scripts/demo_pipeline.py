"""Run the planner + summarizer + citation pipeline against the sample data.

This is a lightweight demo entry point that does **not** require the FastAPI
server, a database, or any network access. It exercises the agent's pure
in-process components against `data/sample/sample_sources.json` and prints
a compact preview of the kind of output the full pipeline produces.

Run from the repo root:

    python scripts/demo_pipeline.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PATH = REPO_ROOT / "data" / "sample" / "sample_sources.json"

sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.citations import CitationSystem  # noqa: E402
from app.services.planner import PlannerAgent  # noqa: E402
from app.services.summarizer import SummarizationAgent  # noqa: E402


def main() -> int:
    payload = json.loads(SAMPLE_PATH.read_text())
    query: str = payload["query"]
    sources: list[dict] = payload["sources"]

    planner = PlannerAgent()
    summarizer = SummarizationAgent()
    citations = CitationSystem()

    plan = planner.build_plan(query, breadth=3)
    print(f"Query: {query}\n")
    print("Plan:")
    for step in plan["steps"]:
        print(f"  - [{step['step_id']}] {step['sub_question']}")
        print(f"      objective: {step['objective']}")

    print("\nSource credibility:")
    for source in sources:
        print(
            f"  - {source['domain']:30s}  "
            f"type={source['source_type']:14s}  "
            f"score={source['credibility_score']:.2f}"
        )

    built_citations = citations.build(sources)
    print("\nCitations (excerpts):")
    for citation in built_citations:
        print(f"  {citation['marker']} {citation['excerpt'][:100]}...")

    summary = summarizer.summarize(query, sources)
    print("\nSummary preview:")
    print(f"  {summary[:400]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
