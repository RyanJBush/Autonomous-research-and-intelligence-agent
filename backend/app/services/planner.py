import re
from typing import TypedDict


class ResearchPlanStep(TypedDict):
    step_id: int
    sub_question: str
    objective: str
    expected_sources: list[str]
    outputs: list[str]


class ResearchPlan(TypedDict):
    query: str
    steps: list[ResearchPlanStep]


# Domain keywords used to enrich sub-question generation
_DOMAIN_HINTS: list[tuple[tuple[str, ...], str, list[str]]] = [
    (
        ("policy", "law", "regulation", "compliance", "governance", "legal"),
        "policy",
        ["government or regulator publications", "legislative records", "official guidance"],
    ),
    (
        ("research", "study", "paper", "clinical", "trial", "evidence", "systematic review"),
        "academic",
        ["peer-reviewed papers", "systematic reviews", "meta-analyses"],
    ),
    (
        ("technology", "software", "ai", "ml", "model", "algorithm", "cloud", "api"),
        "technology",
        ["technical documentation", "benchmark reports", "vendor whitepapers"],
    ),
    (
        ("market", "industry", "revenue", "growth", "forecast", "adoption", "trends"),
        "market",
        ["industry analyst reports", "market research firms", "financial filings"],
    ),
    (
        ("health", "medical", "drug", "treatment", "patient", "clinical", "fda"),
        "health",
        ["FDA guidance", "clinical trial registries", "medical journals"],
    ),
]


class PlannerAgent:
    def __init__(self) -> None:
        pass

    def build_plan(self, query: str, breadth: int = 3) -> ResearchPlan:
        normalized_query = re.sub(r"\s+", " ", query).strip()
        if not normalized_query:
            return {"query": "", "steps": []}

        candidate_parts = re.split(r"\band\b|,|;", normalized_query, flags=re.IGNORECASE)
        sub_questions = [part.strip(" .") for part in candidate_parts if part.strip(" .")]
        if not sub_questions:
            sub_questions = [normalized_query]

        deduped_questions = []
        seen: set[str] = set()
        for question in [normalized_query, *sub_questions]:
            lowered = question.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            deduped_questions.append(question)

        selected_questions = deduped_questions[: max(1, breadth + 1)]
        domain = self._detect_domain(normalized_query)
        steps: list[ResearchPlanStep] = []
        for index, sub_question in enumerate(selected_questions, start=1):
            steps.append(
                {
                    "step_id": index,
                    "sub_question": sub_question,
                    "objective": self._build_objective(sub_question, domain),
                    "expected_sources": self._expected_sources_for(sub_question, domain),
                    "outputs": [
                        "short evidence memo",
                        "top claims to validate",
                        "candidate citations",
                    ],
                }
            )
        return {"query": normalized_query, "steps": steps}

    def plan(self, query: str, breadth: int = 3) -> list[str]:
        research_plan = self.build_plan(query, breadth=breadth)
        return [step["sub_question"] for step in research_plan["steps"]]

    def _detect_domain(self, query: str) -> str:
        lowered = query.lower()
        for keywords, domain, _ in _DOMAIN_HINTS:
            if any(kw in lowered for kw in keywords):
                return domain
        return "general"

    def _build_objective(self, sub_question: str, domain: str) -> str:
        domain_prefix = {
            "policy": "Identify authoritative regulatory or legal evidence for",
            "academic": "Locate peer-reviewed or scientific evidence supporting",
            "technology": "Gather technical documentation and benchmark data for",
            "market": "Collect industry and market data to evaluate",
            "health": "Find clinical or regulatory evidence regarding",
        }.get(domain, "Find verifiable evidence for")
        return f"{domain_prefix}: {sub_question}"

    def _expected_sources_for(self, sub_question: str, domain: str = "general") -> list[str]:
        # Start with domain-specific sources
        sources: list[str] = []
        for _keywords, d, domain_sources in _DOMAIN_HINTS:
            if d == domain:
                sources.extend(domain_sources)
                break
        # Always include general high-credibility sources
        defaults = ["official documentation", "primary reporting", "expert analysis"]
        for src in defaults:
            if src not in sources:
                sources.append(src)
        return sources[:4]

    def generate_search_queries(self, step: str, recency_days: int | None = None) -> list[str]:
        variations = [
            step,
            f"{step} evidence",
            f"{step} official report",
            f"{step} latest updates",
        ]
        if recency_days:
            variations.append(f"{step} last {recency_days} days")
        return list(dict.fromkeys(variations))

    def generate_follow_up_queries(
        self,
        query: str,
        unsupported_claims: list[str],
    ) -> list[str]:
        follow_ups = [f"{query} contradictory evidence", f"{query} primary sources"]
        for claim in unsupported_claims[:3]:
            follow_ups.append(f"{claim} supporting evidence")
        return list(dict.fromkeys(follow_ups))
