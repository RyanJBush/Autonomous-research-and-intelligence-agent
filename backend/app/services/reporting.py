from datetime import datetime, timezone

from app.models import Citation, Source
from app.services.validator import ValidationLayer

# Report schema version – bump when the report structure changes
_SCHEMA_VERSION = "1.0"
_PIPELINE_VERSION = "1.0.0"


class ReportBuilder:
    def __init__(self) -> None:
        self.validator = ValidationLayer()

    def build(
        self,
        query: str,
        sources: list[Source],
        citations: list[Citation],
        contradictions: list[dict[str, str | int]],
        research_plan: dict | None = None,
        step_outputs: list[dict[str, object]] | None = None,
        compliance: dict[str, int] | None = None,
    ) -> dict:
        generated_at = datetime.now(timezone.utc).isoformat()
        citation_by_source: dict[int, list[Citation]] = {}
        for citation in citations:
            citation_by_source.setdefault(citation.source_id, []).append(citation)

        findings: list[dict] = []
        for idx, source in enumerate(sources, start=1):
            support = [
                {
                    "source_id": source.id,
                    "marker": citation.marker,
                    "excerpt": citation.excerpt,
                    "url": source.url,
                }
                for citation in citation_by_source.get(source.id, [])
            ]
            confidence = round(float(source.credibility_score), 3)
            confidence_level = self._confidence_level(confidence)
            findings.append(
                {
                    "claim_id": f"F-{idx}",
                    "claim": source.title,
                    "confidence": confidence,
                    "confidence_level": confidence_level,
                    "confidence_rationale": self._confidence_rationale(
                        confidence_level, source.source_type, len(support)
                    ),
                    "support": support,
                    "source_links": [item["url"] for item in support],
                }
            )

        evidence_coverage = self.validator.score_evidence_coverage(findings)
        contradiction_items = [
            {
                "claim_a": item["left_claim"],
                "claim_b": item["right_claim"],
                "reason": item["reason"],
                "source_indices": [item["left_index"], item["right_index"]],
                "severity": item.get("severity", "medium"),
            }
            for item in contradictions
        ]
        open_questions = self._build_open_questions(evidence_coverage, contradiction_items)
        conclusion = (
            "Evidence is mixed; contradictory claims require additional validation."
            if contradiction_items
            else "Evidence is directionally consistent across current sources."
        )
        disclaimer = self._disclaimer(evidence_coverage, contradiction_items)
        review_required = bool(
            disclaimer or any(finding["confidence_level"] == "low" for finding in findings)
        )
        overall_confidence_score = self._overall_confidence(findings)
        executive_summary = self._build_executive_summary(
            query, findings, contradiction_items, overall_confidence_score
        )
        return {
            "schema_version": _SCHEMA_VERSION,
            "provenance": {
                "pipeline_version": _PIPELINE_VERSION,
                "generated_at": generated_at,
            },
            "executive_summary": executive_summary,
            "overall_confidence_score": overall_confidence_score,
            "research_plan": research_plan or {"query": query, "steps": []},
            "step_outputs": step_outputs or [],
            "findings": findings,
            "evidence_table": [
                {
                    "source_id": source.id,
                    "title": source.title,
                    "source_type": source.source_type,
                    "credibility_score": source.credibility_score,
                    "url": source.url,
                }
                for source in sources
            ],
            "source_comparison": self._source_comparison(sources),
            "contradictions": contradiction_items,
            "evidence_coverage": evidence_coverage,
            "open_questions": open_questions,
            "disclaimer": disclaimer,
            "review_required": review_required,
            "compliance": compliance or {"pii_redactions": 0},
            "conclusion": conclusion,
        }

    def to_summary_text(self, report: dict) -> str:
        lines = [report["executive_summary"], ""]
        overall = report.get("overall_confidence_score")
        if overall is not None:
            pct = int(round(overall * 100))
            lines.append(f"Overall confidence: {pct}%")
            lines.append("")
        lines.append("Findings:")
        for finding in report["findings"]:
            claim = finding["claim"]
            confidence = finding["confidence"]
            confidence_level = finding["confidence_level"]
            markers = ", ".join(item["marker"] for item in finding["support"]) or "none"
            lines.append(
                f"- {claim} (confidence={confidence}, level={confidence_level}, support={markers})"
            )
        lines.append("")
        if report.get("open_questions"):
            lines.append("Open questions:")
            for item in report["open_questions"]:
                lines.append(f"- {item}")
            lines.append("")
        if report.get("disclaimer"):
            lines.append(f"Disclaimer: {report['disclaimer']}")
            lines.append("")
        lines.append(f"Conclusion: {report['conclusion']}")
        return "\n".join(lines)

    def to_markdown(self, report: dict) -> str:
        lines = ["# Research Report", "", "## Executive Summary", report["executive_summary"], ""]
        overall = report.get("overall_confidence_score")
        if overall is not None:
            pct = int(round(overall * 100))
            lines.extend([f"**Overall confidence score:** {pct}%", ""])
        lines.append("## Findings")
        for finding in report["findings"]:
            links = ", ".join(finding["source_links"]) or "No source links"
            lines.append(
                f"- **{finding['claim_id']}**: {finding['claim']} "
                f"(confidence: {finding['confidence']} / {finding['confidence_level']})  \n"
                f"  Sources: {links}"
            )
        lines.append("")
        lines.append("## Contradictions")
        if report["contradictions"]:
            for contradiction in report["contradictions"]:
                contradiction_summary = (
                    f"{contradiction['claim_a']} vs {contradiction['claim_b']}: "
                    f"{contradiction['reason']}"
                )
                lines.append(f"- {contradiction_summary}")
        else:
            lines.append("- None detected")
        lines.append("")
        lines.append("## Open Questions")
        for question in report.get("open_questions", []) or ["None"]:
            lines.append(f"- {question}")
        lines.append("")
        lines.append("## Conclusion")
        lines.append(report["conclusion"])
        if report.get("disclaimer"):
            lines.extend(["", "## Disclaimer", report["disclaimer"]])
        return "\n".join(lines)

    def metrics(
        self,
        report: dict,
        sources: list[Source],
        citations: list[Citation],
    ) -> dict[str, float | int]:
        source_count = len(sources)
        citation_coverage = 0.0
        if source_count:
            covered_source_ids = {citation.source_id for citation in citations}
            citation_coverage = round(len(covered_source_ids) / source_count, 3)
        avg_credibility = (
            round(sum(source.credibility_score for source in sources) / source_count, 3)
            if source_count
            else 0.0
        )
        contradiction_rate = 0.0
        source_pair_count = source_count * (source_count - 1) / 2
        if source_pair_count > 0:
            contradiction_rate = round(
                min(1.0, len(report["contradictions"]) / source_pair_count),
                3,
            )
        return {
            "source_count": source_count,
            "average_credibility_score": avg_credibility,
            "citation_coverage_score": citation_coverage,
            "evidence_coverage_score": float(report["evidence_coverage"]["score"]),
            "fact_support_ratio": float(report["evidence_coverage"]["score"]),
            "contradiction_rate": contradiction_rate,
        }

    def _confidence_level(self, confidence: float) -> str:
        if confidence >= 0.85:
            return "high"
        if confidence >= 0.65:
            return "medium"
        return "low"

    def _confidence_rationale(
        self, level: str, source_type: str, support_count: int
    ) -> str:
        """Generate a human-readable rationale for the confidence level."""
        type_label = {
            "official_docs": "official documentation",
            "academic": "peer-reviewed / academic source",
            "news": "news outlet",
            "blog": "blog or opinion piece",
            "forum": "community forum",
        }.get(source_type, source_type)
        base = f"Source is {type_label}."
        if support_count == 0:
            base += " No direct citation excerpts captured."
        elif support_count == 1:
            base += " Supported by 1 citation excerpt."
        else:
            base += f" Supported by {support_count} citation excerpts."
        if level == "high":
            base += " Confidence is high."
        elif level == "medium":
            base += " Confidence is moderate; additional verification recommended."
        else:
            base += " Confidence is low; treat findings as provisional."
        return base

    def _source_comparison(self, sources: list[Source]) -> list[dict[str, object]]:
        by_type: dict[str, list[float]] = {}
        for source in sources:
            by_type.setdefault(source.source_type, []).append(float(source.credibility_score))
        return [
            {
                "source_type": source_type,
                "count": len(scores),
                "average_credibility": round(sum(scores) / len(scores), 3),
            }
            for source_type, scores in sorted(by_type.items())
        ]

    def _build_open_questions(
        self,
        evidence_coverage: dict[str, object],
        contradiction_items: list[dict[str, object]],
    ) -> list[str]:
        questions: list[str] = []
        unsupported_claims = evidence_coverage.get("unsupported_claims", [])
        if isinstance(unsupported_claims, list):
            for claim in unsupported_claims[:3]:
                questions.append(f"What primary evidence supports claim: {claim}?")
        for contradiction in contradiction_items[:2]:
            questions.append(
                f"Why do sources disagree on '{contradiction['claim_a']}' "
                f"and '{contradiction['claim_b']}'?"
            )
        if not questions:
            questions.append("Which additional primary sources could increase confidence?")
        return questions

    def _disclaimer(
        self,
        evidence_coverage: dict[str, object],
        contradiction_items: list[dict[str, object]],
    ) -> str | None:
        if contradiction_items:
            return "Conflicting evidence detected; conclusions should be treated as provisional."
        if float(evidence_coverage.get("score", 0.0)) < 0.6:
            return (
                "Limited evidence coverage; more sources are required before relying on findings."
            )
        return None

    def _overall_confidence(self, findings: list[dict]) -> float:
        """Compute the mean credibility score across all findings."""
        if not findings:
            return 0.0
        return round(sum(float(f["confidence"]) for f in findings) / len(findings), 3)

    def _build_executive_summary(
        self,
        query: str,
        findings: list[dict],
        contradictions: list[dict],
        overall_confidence: float,
    ) -> str:
        """Synthesize a human-readable executive summary from findings."""
        if not findings:
            return f"Research on '{query}' found no usable sources."

        source_count = len(findings)
        pct = int(round(overall_confidence * 100))
        lines = [
            f"Research on '{query}' reviewed {source_count} source(s) "
            f"with an overall confidence of {pct}%."
        ]

        # Highlight the top finding by confidence
        sorted_findings = sorted(findings, key=lambda f: float(f["confidence"]), reverse=True)
        top = sorted_findings[0]
        level = top.get("confidence_level", "medium")
        lines.append(
            f"Highest-confidence finding ({level}): {top['claim']}"
        )

        if contradictions:
            lines.append(
                f"Note: {len(contradictions)} contradictory source(s) detected; "
                "conclusions should be treated as provisional."
            )

        return " ".join(lines)
