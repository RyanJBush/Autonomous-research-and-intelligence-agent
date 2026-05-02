from app.services.planner import PlannerAgent


def test_plan_empty_query_returns_empty_list() -> None:
    assert PlannerAgent().plan("") == []


def test_plan_whitespace_only_query_returns_empty_list() -> None:
    assert PlannerAgent().plan("   ") == []


def test_plan_single_part_query_returns_only_the_full_query() -> None:
    steps = PlannerAgent().plan("quantum computing")
    assert steps == ["quantum computing"]


def test_plan_breadth_limits_number_of_sub_questions() -> None:
    planner = PlannerAgent()
    # Query with 5 separable parts; breadth=2 means at most 2 sub-questions appended
    steps = planner.plan("AI safety, model alignment, governance, regulation, oversight", breadth=2)
    assert steps[0] == "AI safety, model alignment, governance, regulation, oversight"
    # full query + at most breadth items → at most 3 total
    assert len(steps) <= 3


def test_plan_deduplicates_when_sub_question_matches_full_query() -> None:
    # A one-part query where the single sub-question equals the full query should not repeat it
    steps = PlannerAgent().plan("climate")
    assert steps.count("climate") == 1


def test_generate_search_queries_without_recency_returns_four_base_variations() -> None:
    queries = PlannerAgent().generate_search_queries("climate policy")
    assert "climate policy" in queries
    assert "climate policy evidence" in queries
    assert "climate policy official report" in queries
    assert "climate policy latest updates" in queries
    assert not any("days" in q for q in queries)


def test_generate_search_queries_with_recency_appends_days_variation() -> None:
    queries = PlannerAgent().generate_search_queries("climate policy", recency_days=30)
    assert "climate policy last 30 days" in queries
    assert len(queries) == 5


def test_generate_search_queries_returns_no_duplicates() -> None:
    queries = PlannerAgent().generate_search_queries("test")
    assert len(queries) == len(set(queries))


def test_generate_follow_up_queries_limits_to_first_three_claims() -> None:
    follow_ups = PlannerAgent().generate_follow_up_queries("topic", ["A", "B", "C", "D", "E"])
    assert "A supporting evidence" in follow_ups
    assert "B supporting evidence" in follow_ups
    assert "C supporting evidence" in follow_ups
    assert "D supporting evidence" not in follow_ups
    assert "E supporting evidence" not in follow_ups


def test_generate_follow_up_queries_with_empty_claims_returns_base_queries() -> None:
    follow_ups = PlannerAgent().generate_follow_up_queries("AI policy", [])
    assert "AI policy contradictory evidence" in follow_ups
    assert "AI policy primary sources" in follow_ups


def test_build_plan_returns_structured_steps() -> None:
    plan = PlannerAgent().build_plan("AI policy and safety", breadth=2)
    assert plan["query"] == "AI policy and safety"
    assert len(plan["steps"]) >= 1
    first_step = plan["steps"][0]
    assert first_step["step_id"] == 1
    assert first_step["sub_question"]
    assert "expected_sources" in first_step
    assert "outputs" in first_step


def test_build_plan_includes_regulatory_sources_for_policy_queries() -> None:
    plan = PlannerAgent().build_plan("AI regulation", breadth=1)
    expected_sources = plan["steps"][0]["expected_sources"]
    assert "government or regulator publications" in expected_sources
