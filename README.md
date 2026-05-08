![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Memory-orange?style=flat)
![CI](https://github.com/RyanJBush/Autonomous-research-and-intelligence-agent/actions/workflows/ci.yml/badge.svg)

# Astra AI

> An autonomous AI research agent that decomposes complex queries into sub-questions, searches and validates sources in parallel, detects contradictions, and synthesizes citation-backed reports — built to explore what it actually takes to make LLM-powered research trustworthy.

---

## 🎯 What I Built & Why

LLMs are good at generating text but bad at knowing when they're wrong. I built Astra AI to tackle the reliability problem in AI research pipelines:

- **Multi-step planner agent** — domain-aware query decomposition (policy, academic, technology, market, health) ensures the right sub-questions are asked, not just the obvious ones
- **Source validation layer** — domain allow/deny filtering, duplicate detection, prompt-injection signal filtering, and PII redaction before any content is persisted or cited
- **Contradiction detection** — when two sources disagree, the pipeline surfaces the conflict with severity levels (high/medium/low) instead of silently picking one
- **FAISS memory persistence** — research sessions retain context across steps so the agent builds on prior findings rather than starting from scratch each query
- **Confidence-scored reports** — every synthesized report includes an overall confidence score and per-claim source links, making the output auditable

---

## 📷 Features

- **Autonomous research pipeline** — plan → search → scrape → validate → synthesize → report in one request
- **Domain-aware planning** — query decomposition tuned for policy, academic, technology, market, and health domains
- **Source credibility scoring** — per-source quality assessment with contradiction detection
- **PII redaction** — before persistence and in compliance reporting
- **FAISS memory** — vector-based session memory with persistence
- **Pause / resume / retry / refine** — full run lifecycle controls
- **Export to Markdown / JSON** — shareable reports with confidence sections and disclaimers
- **React dashboard** — domain-aware plan preview, execution timeline, evidence filters, contradiction panel

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + SQLAlchemy + PostgreSQL |
| Search | DuckDuckGo Instant Answer API + Wikipedia OpenSearch fallback |
| Scraping | requests + BeautifulSoup |
| Memory | FAISS (vector persistence) |
| Frontend | React + Vite + Tailwind CSS |
| Infra | Docker Compose + GitHub Actions CI |

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+

### Docker (Recommended)
```bash
docker-compose up --build
# Frontend:         http://localhost:5173
# Backend API docs: http://localhost:8000/docs
```

### Local Development
```bash
# Backend
cd backend && cp .env.example .env
pip install -e .[dev]
uvicorn app.main:app --reload

# Frontend
cd frontend && cp .env.example .env
npm install && npm run dev
```

> Prefer Python 3.11+ for local development (CI runs on 3.11).

### Quality Checks
```bash
make lint
make test
make smoke
```

---

## 🗂️ Repository Structure

```
backend/    FastAPI API, research pipeline, planner agent, validation layer, FAISS memory, tests
frontend/   React dashboard (query input, plan preview, results, source viewer, execution trace)
docs/       Architecture notes, demo script, runbook
```

---

## 📘 15-Minute Demo Flow

1. Open `http://localhost:5173` and sign in (local demo auth auto-provisions a user)
2. Open **Research Query** and run one of the built-in demo prompts
3. In **Research Results**, review:
   - Findings with confidence rationale
   - Evidence table filters and contradiction panel
   - Execution timeline (state + latency per step)
4. Open **Source Viewer** from citations and inspect source credibility metadata
5. Export Markdown and JSON reports

Full scripted walkthrough: `docs/demo-script.md`
Troubleshooting: `docs/runbook.md`

---

## 📝 Key Learnings

- Multi-step planning with domain awareness produces meaningfully better research decomposition than single-shot queries
- Source validation (dedup, domain filtering, prompt-injection detection) is as important as source retrieval — garbage in, garbage out applies doubly when the output is a cited report
- Contradiction detection is what separates a research tool from a hallucination machine; surfacing disagreements explicitly builds user trust in the output

---

## 📄 License

MIT
