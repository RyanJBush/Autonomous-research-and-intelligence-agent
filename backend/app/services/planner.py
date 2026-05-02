import re
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate


class ResearchPlanStep(TypedDict):
    step_id: int
    sub_question: str
    objective: str
    expected_sources: list[str]
    outputs: list[str]


class ResearchPlan(TypedDict):
    query: str
    steps: list[ResearchPlanStep]


class PlannerAgent:
    def __init__(self) -> None:
        self.prompt = ChatPromptTemplate.from_template(
            "Break the query into research sub-questions: {query}"
        )

    def build_plan(self, query: str, breadth: int = 3) -> ResearchPlan:
        _ = self.prompt.invoke({"query": query})
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
        steps: list[ResearchPlanStep] = []
        for index, sub_question in enumerate(selected_questions, start=1):
            steps.append(
                {
                    "step_id": index,
                    "sub_question": sub_question,
                    "objective": f"Find verifiable evidence for: {sub_question}",
                    "expected_sources": self._expected_sources_for(sub_question),
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

    def _expected_sources_for(self, sub_question: str) -> list[str]:
        lowered = sub_question.lower()
        sources = ["official documentation", "primary reporting", "expert analysis"]
        if any(token in lowered for token in ("policy", "law", "regulation")):
            sources.insert(0, "government or regulator publications")
        if any(token in lowered for token in ("research", "study", "paper")):
            sources.insert(0, "peer-reviewed papers")
        return list(dict.fromkeys(sources))

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
