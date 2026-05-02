import pytest
from app.models import Citation, Source
from app.services.citations import CitationSystem
from app.services.reporting import ReportBuilder
from app.services.summarizer import SummarizationAgent
from app.services.tool_registry import ToolRegistry


def _make_source(
    idx: int,
    source_type: str = "news",
    credibility_score: float = 0.8,
) -> Source:
    return Source(
        id=idx,
        research_id=1,
        title=f"Claim {idx}",
        url=f"https://example.com/{idx}",
        content="c",
        source_type=source_type,
        credibility_score=credibility_score,
    )


# ---------------------------------------------------------------------------
# ReportBuilder._confidence_level
# ---------------------------------------------------------------------------


def test_confidence_level_high_at_and_above_085() -> None:
    builder = ReportBuilder()
    assert builder._confidence_level(0.85) == "high"
    assert builder._confidence_level(1.0) == "high"


def test_confidence_level_medium_between_065_and_084() -> None:
    builder = ReportBuilder()
    assert builder._confidence_level(0.65) == "medium"
    assert builder._confidence_level(0.84) == "medium"


def test_confidence_level_low_below_065() -> None:
    builder = ReportBuilder()
    assert builder._confidence_level(0.0) == "low"
    assert builder._confidence_level(0.64) == "low"


# ---------------------------------------------------------------------------
# ReportBuilder.to_markdown
# ---------------------------------------------------------------------------


def test_to_markdown_no_contradictions_shows_none_detected() -> None:
    builder = ReportBuilder()
    report = {
        "executive_summary": "Summary for: query",
        "findings": [],
        "contradictions": [],
        "open_questions": ["A question"],
        "disclaimer": None,
        "conclusion": "Consistent",
    }
    md = builder.to_markdown(report)
    assert "## Contradictions" in md
    assert "None detected" in md
    assert "## Disclaimer" not in md


def test_to_markdown_includes_findings_and_source_links() -> None:
    builder = ReportBuilder()
    source = _make_source(1)
    citation = Citation(id=1, research_id=1, source_id=1, marker="[1]", excerpt="excerpt")
    report = builder.build("query", [source], [citation], [])
    md = builder.to_markdown(report)
    assert "Claim 1" in md
    assert "https://example.com/1" in md
    assert "## Findings" in md


def test_to_markdown_open_questions_section_present() -> None:
    builder = ReportBuilder()
    report = {
        "executive_summary": "S",
        "findings": [],
        "contradictions": [],
        "open_questions": ["What is the evidence?"],
        "disclaimer": None,
        "conclusion": "Consistent",
    }
    md = builder.to_markdown(report)
    assert "## Open Questions" in md
    assert "What is the evidence?" in md


# ---------------------------------------------------------------------------
# ReportBuilder.build edge cases
# ---------------------------------------------------------------------------


def test_build_empty_sources_returns_empty_findings_and_zero_coverage() -> None:
    builder = ReportBuilder()
    report = builder.build("empty query", [], [], [])
    assert report["findings"] == []
    assert report["evidence_table"] == []
    assert report["source_comparison"] == []
    assert report["evidence_coverage"]["score"] == 0.0


def test_build_with_explicit_compliance_dict_is_preserved() -> None:
    builder = ReportBuilder()
    source = _make_source(1)
    report = builder.build("query", [source], [], [], compliance={"pii_redactions": 7})
    assert report["compliance"]["pii_redactions"] == 7


def test_build_compliance_defaults_to_zero_when_not_provided() -> None:
    builder = ReportBuilder()
    source = _make_source(1)
    report = builder.build("query", [source], [], [])
    assert report["compliance"]["pii_redactions"] == 0


def test_build_conclusion_mixed_when_contradictions_present() -> None:
    builder = ReportBuilder()
    source = _make_source(1)
    contradictions = [
        {
            "left_claim": "Claim A",
            "right_claim": "Claim B",
            "reason": "Opposing outcome language",
            "left_index": 0,
            "right_index": 1,
        }
    ]
    report = builder.build("query", [source], [], contradictions)
    assert "mixed" in report["conclusion"].lower()


# ---------------------------------------------------------------------------
# ReportBuilder.metrics edge cases
# ---------------------------------------------------------------------------


def test_metrics_no_sources_returns_all_zeros() -> None:
    builder = ReportBuilder()
    report = {"contradictions": [], "evidence_coverage": {"score": 0.0}}
    result = builder.metrics(report, [], [])
    assert result["source_count"] == 0
    assert result["average_credibility_score"] == 0.0
    assert result["citation_coverage_score"] == 0.0
    assert result["contradiction_rate"] == 0.0


def test_metrics_single_source_no_citation_gives_zero_coverage() -> None:
    builder = ReportBuilder()
    source = _make_source(1, credibility_score=0.9)
    report = {"contradictions": [], "evidence_coverage": {"score": 1.0}}
    result = builder.metrics(report, [source], [])
    assert result["source_count"] == 1
    assert result["average_credibility_score"] == 0.9
    assert result["citation_coverage_score"] == 0.0


# ---------------------------------------------------------------------------
# ReportBuilder._source_comparison
# ---------------------------------------------------------------------------


def test_source_comparison_aggregates_by_type() -> None:
    builder = ReportBuilder()
    sources = [
        _make_source(1, source_type="news", credibility_score=0.8),
        _make_source(2, source_type="news", credibility_score=0.6),
        _make_source(3, source_type="academic", credibility_score=0.9),
    ]
    comparison = builder._source_comparison(sources)
    types = {entry["source_type"] for entry in comparison}
    assert "news" in types
    assert "academic" in types
    news_entry = next(e for e in comparison if e["source_type"] == "news")
    assert news_entry["count"] == 2
    assert news_entry["average_credibility"] == round((0.8 + 0.6) / 2, 3)


def test_source_comparison_single_source_per_type() -> None:
    builder = ReportBuilder()
    sources = [_make_source(1, source_type="academic", credibility_score=0.9)]
    comparison = builder._source_comparison(sources)
    assert comparison == [{"source_type": "academic", "count": 1, "average_credibility": 0.9}]


# ---------------------------------------------------------------------------
# CitationSystem
# ---------------------------------------------------------------------------


def test_citation_system_empty_sources_returns_empty_list() -> None:
    assert CitationSystem().build([]) == []


# ---------------------------------------------------------------------------
# SummarizationAgent
# ---------------------------------------------------------------------------


def test_summarizer_empty_sources_returns_only_topic_line() -> None:
    result = SummarizationAgent().summarize("AI safety", [])
    assert result == "Research topic: AI safety"


def test_summarizer_multiple_sources_numbers_each() -> None:
    result = SummarizationAgent().summarize(
        "topic",
        [
            {"title": "First", "content": "A" * 50},
            {"title": "Second", "content": "B" * 50},
        ],
    )
    assert "- [1] First:" in result
    assert "- [2] Second:" in result


def test_summarizer_truncates_content_to_180_chars() -> None:
    result = SummarizationAgent().summarize("t", [{"title": "Doc", "content": "X" * 300}])
    assert "X" * 180 in result
    assert "X" * 181 not in result


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------


def test_tool_registry_researcher_role_has_all_pipeline_tools() -> None:
    registry = ToolRegistry()
    tools = registry.allowed_tools_for_role("researcher")
    assert {"planner", "search", "scraper", "validator", "reporting", "citations"} <= tools


def test_tool_registry_viewer_role_has_no_tools() -> None:
    assert ToolRegistry().allowed_tools_for_role("viewer") == set()


def test_tool_registry_user_role_has_all_pipeline_tools() -> None:
    tools = ToolRegistry().allowed_tools_for_role("user")
    assert "planner" in tools
    assert "search" in tools


def test_ensure_stage_allowed_all_stages_succeed_for_researcher() -> None:
    registry = ToolRegistry()
    for stage in ("planning", "searching", "extracting", "validating", "synthesizing"):
        registry.ensure_stage_allowed("researcher", stage)  # must not raise


def test_ensure_stage_allowed_unknown_stage_does_not_raise_for_viewer() -> None:
    # An unknown stage has an empty required-tools set, so no PermissionError regardless of role.
    try:
        ToolRegistry().ensure_stage_allowed("viewer", "nonexistent_stage")
    except PermissionError:
        pytest.fail("ensure_stage_allowed raised unexpectedly for an unknown stage")


def test_ensure_stage_allowed_viewer_fails_all_known_stages() -> None:
    registry = ToolRegistry()
    for stage in ("planning", "searching", "extracting", "validating", "synthesizing"):
        with pytest.raises(PermissionError):
            registry.ensure_stage_allowed("viewer", stage)
