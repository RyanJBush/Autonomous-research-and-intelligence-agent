"""Pre-built demo research session seeder.

Creates a realistic, fully-populated research result without network access so
the app is immediately demo-ready after first startup.
"""

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    Citation,
    Memory,
    ResearchSession,
    ResearchTraceEvent,
    Source,
    Summary,
)

# ---------------------------------------------------------------------------
# Pre-built content
# ---------------------------------------------------------------------------

_DEMO_QUERY = "Compare major cloud providers on 2026 enterprise AI governance offerings."

_DEMO_SOURCES = [
    {
        "title": "AWS AI Governance Framework 2026 – Enterprise Guide",
        "url": "https://aws.amazon.com/ai/governance/enterprise",
        "content": (
            "Amazon Web Services has published an updated AI governance framework for enterprise "
            "customers covering model risk management, data lineage, and continuous compliance "
            "monitoring.  The framework introduces mandatory model cards for all production "
            "deployments and integrates with AWS Audit Manager for real-time policy enforcement. "
            "Organisations that adopt the framework report a significant reduction in compliance "
            "incidents and improved audit outcomes.  The official documentation is available "
            "through the AWS Management Console and is updated quarterly."
        ),
        "source_type": "official_docs",
        "credibility_score": 0.97,
    },
    {
        "title": "Google Cloud Vertex AI – Responsible AI and Governance 2026",
        "url": "https://cloud.google.com/vertex-ai/docs/responsible-ai-governance",
        "content": (
            "Google Cloud's Vertex AI platform now includes built-in governance controls such as "
            "explainability dashboards, fairness constraints, and an AI Safety API that flags "
            "high-risk predictions before they reach production.  Enterprise customers can enforce "
            "workspace-level policies and receive automated alerts when model performance drifts "
            "beyond thresholds.  The service integrates with Chronicle SIEM for audit logging "
            "and meets ISO 42001 requirements for AI management systems."
        ),
        "source_type": "official_docs",
        "credibility_score": 0.96,
    },
    {
        "title": "Microsoft Azure AI Foundry – Governance and Compliance Overview",
        "url": "https://learn.microsoft.com/azure/ai-foundry/governance",
        "content": (
            "Microsoft Azure AI Foundry provides an end-to-end governance layer for AI workloads "
            "including content filtering, prompt-injection protection, and a Responsible AI "
            "dashboard.  The platform supports cross-region residency controls and offers "
            "compliance attestations for GDPR, HIPAA, and the EU AI Act.  Customers benefit from "
            "native integration with Microsoft Purview for data lineage tracking across all AI "
            "model inputs and outputs."
        ),
        "source_type": "official_docs",
        "credibility_score": 0.96,
    },
    {
        "title": "Gartner: Enterprise AI Governance Market Guide 2026",
        "url": "https://www.gartner.com/en/documents/ai-governance-market-guide-2026",
        "content": (
            "Gartner's 2026 market guide highlights that enterprise AI governance adoption has "
            "increased by 62 percent year-over-year, driven largely by regulatory pressure from "
            "the EU AI Act and emerging US federal AI policy.  Cloud providers differentiate on "
            "automation depth, auditability, and the breadth of pre-built compliance packs.  "
            "AWS and Google Cloud lead on developer tooling while Azure leads on enterprise "
            "identity integration and compliance coverage for regulated industries."
        ),
        "source_type": "news",
        "credibility_score": 0.88,
    },
    {
        "title": "IEEE Spectrum: AI Safety Controls in Cloud Platforms – 2026 Review",
        "url": "https://spectrum.ieee.org/cloud-ai-safety-controls-2026",
        "content": (
            "A comparative evaluation of AI safety controls across the three major cloud platforms "
            "found that all three now implement mandatory model evaluation gates before production "
            "deployment.  The study notes that consistency of enforcement varies, with Microsoft "
            "Azure demonstrating the most comprehensive automated red-teaming capabilities and "
            "AWS offering the broadest ecosystem of third-party governance integrations.  "
            "Google Cloud's real-time safety API is rated as the most developer-friendly but "
            "offers fewer enterprise-grade audit hooks compared to AWS and Azure."
        ),
        "source_type": "academic",
        "credibility_score": 0.91,
    },
]

_DEMO_PLAN = {
    "query": _DEMO_QUERY,
    "steps": [
        {
            "step_id": 1,
            "sub_question": (
                "What AI governance features does AWS offer for enterprise clients in 2026?"
            ),
            "objective": "Find verifiable evidence for AWS AI governance offerings",
            "expected_sources": ["official documentation", "primary reporting", "expert analysis"],
            "outputs": ["short evidence memo", "top claims to validate", "candidate citations"],
        },
        {
            "step_id": 2,
            "sub_question": (
                "How does Google Cloud Vertex AI address AI governance for enterprises?"
            ),
            "objective": "Find verifiable evidence for Google Cloud AI governance offerings",
            "expected_sources": ["official documentation", "primary reporting"],
            "outputs": ["short evidence memo", "top claims to validate", "candidate citations"],
        },
        {
            "step_id": 3,
            "sub_question": "What Azure AI governance capabilities does Microsoft provide in 2026?",
            "objective": "Find verifiable evidence for Azure AI governance offerings",
            "expected_sources": ["official documentation", "government or regulator publications"],
            "outputs": ["short evidence memo", "top claims to validate", "candidate citations"],
        },
        {
            "step_id": 4,
            "sub_question": "How do analyst reports rank cloud AI governance maturity?",
            "objective": "Find analyst and third-party assessments of cloud AI governance",
            "expected_sources": ["expert analysis", "peer-reviewed papers"],
            "outputs": ["short evidence memo", "comparative claims", "candidate citations"],
        },
    ],
}

_DEMO_TRACE = [
    (
        "planning",
        "completed",
        "Plan generated: 4 sub-questions across 3 providers + analyst view",
        120.0,
    ),
    ("searching", "completed", "Collected 12 candidate sources from web discovery", 2340.0),
    (
        "extracting",
        "completed",
        "Extracted 5 source payloads (search_failures=1, extraction_failures=2)",
        4810.0,
    ),
    ("validating", "completed", "Validated 5 sources with 0 contradictions", 88.0),
    ("synthesizing", "completed", "Synthesized report with 5 findings", 310.0),
    ("complete", "completed", "Research complete", 0.0),
]


class DemoSeeder:
    """Creates a realistic pre-built research session for instant demo use."""

    def seed(self, db: Session, user_id: int, workspace_id: int | None = None) -> ResearchSession:
        """Insert demo data into the database and return the new ResearchSession."""
        research = ResearchSession(
            user_id=user_id,
            query=_DEMO_QUERY,
            status="complete",
            version=1,
            workspace_id=workspace_id,
        )
        db.add(research)
        db.flush()

        source_rows: list[Source] = []
        for payload in _DEMO_SOURCES:
            row = Source(
                research_id=research.id,
                title=payload["title"],
                url=payload["url"],
                content=payload["content"],
                source_type=payload["source_type"],
                credibility_score=payload["credibility_score"],
                retrieved_at=datetime.now(timezone.utc),
            )
            db.add(row)
            source_rows.append(row)
        db.flush()

        citation_rows: list[Citation] = []
        for idx, source in enumerate(source_rows, start=1):
            citation = Citation(
                research_id=research.id,
                source_id=source.id,
                marker=f"[{idx}]",
                excerpt=source.content[:220],
            )
            db.add(citation)
            citation_rows.append(citation)
        db.flush()

        # Build findings from sources
        findings = []
        for idx, (source, citation) in enumerate(
            zip(source_rows, citation_rows, strict=False), start=1
        ):
            findings.append(
                {
                    "claim_id": f"F-{idx}",
                    "claim": source.title,
                    "confidence": source.credibility_score,
                    "confidence_level": (
                        "high" if source.credibility_score >= 0.85
                        else "medium" if source.credibility_score >= 0.65
                        else "low"
                    ),
                    "confidence_rationale": (
                        f"Source is {source.source_type}. Supported by 1 citation excerpt."
                    ),
                    "support": [
                        {
                            "source_id": source.id,
                            "marker": citation.marker,
                            "excerpt": citation.excerpt,
                            "url": source.url,
                        }
                    ],
                    "source_links": [source.url],
                }
            )

        overall_confidence = round(
            sum(f["confidence"] for f in findings) / len(findings), 3
        ) if findings else 0.0
        report = {
            "schema_version": "1.0",
            "provenance": {
                "pipeline_version": "1.0.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "executive_summary": (
                "Automated research summary for: " + _DEMO_QUERY
            ),
            "research_plan": _DEMO_PLAN,
            "step_outputs": [
                {
                    "stage": "extract",
                    "source_url": src.url,
                    "source_title": src.title,
                    "credibility_score": src.credibility_score,
                    "output": src.content[:500],
                }
                for src in source_rows
            ],
            "findings": findings,
            "evidence_table": [
                {
                    "source_id": src.id,
                    "title": src.title,
                    "source_type": src.source_type,
                    "credibility_score": src.credibility_score,
                    "url": src.url,
                }
                for src in source_rows
            ],
            "source_comparison": [
                {"source_type": "official_docs", "count": 3, "average_credibility": 0.963},
                {"source_type": "news", "count": 1, "average_credibility": 0.88},
                {"source_type": "academic", "count": 1, "average_credibility": 0.91},
            ],
            "contradictions": [],
            "evidence_coverage": {
                "supported_claims": len(findings),
                "total_claims": len(findings),
                "score": 1.0,
                "unsupported_claims": [],
            },
            "open_questions": [
                "Which additional primary sources could increase confidence?",
                "How do pricing and SLA differences affect governance tool adoption?",
            ],
            "disclaimer": None,
            "review_required": False,
            "compliance": {"pii_redactions": 0},
            "conclusion": "Evidence is directionally consistent across current sources.",
            "confidence_score": overall_confidence,
            "confidence_level": "high",
        }

        summary_lines = [report["executive_summary"], ""]
        summary_lines.append("Findings:")
        for finding in findings:
            markers = ", ".join(s["marker"] for s in finding["support"]) or "none"
            summary_lines.append(
                f"- {finding['claim']} (confidence={finding['confidence']}, "
                f"level={finding['confidence_level']}, support={markers})"
            )
        summary_lines.extend(["", f"Conclusion: {report['conclusion']}"])
        summary_text = "\n".join(summary_lines)

        summary = Summary(
            research_id=research.id,
            content=summary_text,
            structured_report=json.dumps(report),
            requires_review=False,
        )
        db.add(summary)

        for src in source_rows:
            db.add(
                Memory(
                    research_id=research.id,
                    chunk=src.content[:500],
                    source_url=src.url,
                    score=src.credibility_score,
                )
            )

        for stage, state, detail, latency_ms in _DEMO_TRACE:
            db.add(
                ResearchTraceEvent(
                    research_id=research.id,
                    stage=stage,
                    state=state,
                    detail=detail,
                    error_category=None,
                    latency_ms=latency_ms,
                )
            )

        db.commit()
        db.refresh(research)
        return research
