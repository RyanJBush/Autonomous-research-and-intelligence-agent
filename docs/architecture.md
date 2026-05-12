# Europa — Architecture (Research-Agent Prototype)

This document describes Europa as an **autonomous research and intelligence agent prototype**.

> **Accuracy boundary:** Europa is not a guaranteed fact-checking system. It produces structured, citation-linked outputs that **require human verification**.

## 1) System purpose
Europa is designed to make research review more structured and auditable by:
- decomposing broad questions into sub-questions,
- collecting candidate evidence,
- scoring/supporting claims with transparent heuristics,
- surfacing unsupported or contradictory claims.

## 2) Core pipeline
1. **Plan** (`planner.py`) — converts the user query into sub-tasks.
2. **Search/Retrieve** (`search.py`) — gets candidate sources.
3. **Extract** (`scraper.py`) — extracts text/content for analysis.
4. **Validate** (`validator.py`) — computes credibility/coverage/contradiction signals.
5. **Synthesize** (`summarizer.py`, `citations.py`, `reporting.py`) — builds the final report with claim→evidence links.

Orchestration lives in `research_service.py`.

## 3) Retrieval/search truth table
Europa has multiple retrieval states depending on runtime mode:

| Mode | Data source | Live network? | Intended use |
|---|---|---:|---|
| Sample demo (`scripts/demo_pipeline.py`) | `data/sample/sample_sources.json` | No | Fast, deterministic walkthrough |
| Screenshot/demo backend (`backend/_europa_run.py`) | deterministic sample-backed pipeline | No | Stable UI capture and portfolio demos |
| Default backend runtime | Wikipedia OpenSearch + DuckDuckGo Instant Answer | Yes | Lightweight live retrieval (limited depth) |

**Important:** “live mode” does not imply comprehensive web coverage or high-confidence truth.

## 4) Trust model
Europa’s output quality signals are **heuristics**, including:
- source credibility components,
- corroboration bonus,
- recency bonus,
- contradiction penalty,
- evidence coverage/unsupported claims.

These signals help prioritize review; they do not certify factual correctness.

## 5) Data and observability
- `ResearchTraceEvent`: per-stage timeline.
- `AgentRunMetric`: per-agent metrics.
- `Source`, `Citation`, `Summary`: persisted run artifacts.
- replay endpoint: reconstructable run context.

## 6) Non-goals / limitations
- Not production-ready.
- Not a legal/medical/financial fact authority.
- Not guaranteed to retrieve best-available or complete sources.
- Not a replacement for domain-expert judgment.

## 7) Human-in-the-loop requirement
All findings, confidence values, and claims should be treated as **draft research outputs** and independently verified by a human reviewer before use.
