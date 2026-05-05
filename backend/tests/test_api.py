import json
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["ASTRA_DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db
from app.main import app
from app.models import AuditLog, Citation, Memory, ResearchSession, ResearchTraceEvent, Source, Summary, User
from app.services.research_service import ResearchService


class FakeResearchService(ResearchService):
    def run(self, db: Session, user_id: int, query: str, **kwargs):
        research = ResearchSession(user_id=user_id, query=query, status="complete")
        if "parent_session_id" in kwargs:
            research.parent_session_id = kwargs["parent_session_id"]
        if "version" in kwargs:
            research.version = kwargs["version"]
        db.add(research)
        db.flush()

        source = Source(
            research_id=research.id,
            title="Example Source",
            url="https://example.com",
            content="A" * 200,
        )
        db.add(source)
        db.flush()

        summary = Summary(research_id=research.id, content="Summary content")
        citation = Citation(
            research_id=research.id,
            source_id=source.id,
            marker="[1]",
            excerpt="A" * 120,
        )
        memory = Memory(research_id=research.id, chunk="A" * 200, source_url=source.url, score=1.0)
        summary.structured_report = json.dumps(
            {
                "executive_summary": "Summary content",
                "findings": [
                    {
                        "claim_id": "F-1",
                        "claim": "Example Source",
                        "confidence": 0.8,
                        "confidence_level": "medium",
                        "source_links": ["https://example.com"],
                        "support": [
                            {"source_id": source.id, "marker": "[1]", "excerpt": "A" * 100}
                        ],
                    }
                ],
                "evidence_coverage": {"supported_claims": 1, "total_claims": 1, "score": 1.0},
                "open_questions": ["Which additional primary sources could increase confidence?"],
                "disclaimer": None,
                "compliance": {"pii_redactions": 0},
                "contradictions": [],
                "conclusion": "Consistent",
            }
        )
        trace = ResearchTraceEvent(
            research_id=research.id,
            stage="complete",
            state="completed",
            detail="Research complete",
            error_category=None,
            latency_ms=10.0,
        )
        db.add_all([summary, citation, memory, trace])
        db.commit()
        db.refresh(research)
        db.refresh(summary)
        db.refresh(citation)
        return research, summary, [citation]


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
app.state.research_service = FakeResearchService()

client = TestClient(app)


def login_headers() -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "strong-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def admin_headers() -> dict[str, str]:
    headers = login_headers()
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "user@example.com").first()
        assert user is not None
        user.role = "admin"
        db.add(user)
        db.commit()
    finally:
        db.close()
    return headers


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_login_rejects_invalid_password() -> None:
    first = client.post(
        "/api/auth/login",
        json={"email": "wrongpass@example.com", "password": "correct-pass"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/auth/login",
        json={"email": "wrongpass@example.com", "password": "incorrect-pass"},
    )
    assert second.status_code == 401
    assert second.json()["detail"] == "Invalid credentials"


def test_create_research_enforces_daily_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = login_headers()
    monkeypatch.setattr("app.main.settings.daily_research_quota", 0)

    response = client.post(
        "/api/research",
        json={"query": "quota check"},
        headers=headers,
    )
    assert response.status_code == 429
    assert response.json()["detail"] == "Daily research quota exceeded"


def test_get_research_not_found_returns_404() -> None:
    headers = login_headers()
    response = client.get("/api/research/999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Research not found"


def test_metrics_and_compliance_return_defaults_when_summary_missing() -> None:
    headers = login_headers()
    create_response = client.post(
        "/api/research",
        json={"query": "summary removal"},
        headers=headers,
    )
    research_id = create_response.json()["research_id"]

    db = TestingSessionLocal()
    try:
        summary = db.query(Summary).filter(Summary.research_id == research_id).first()
        assert summary is not None
        db.delete(summary)
        db.commit()
    finally:
        db.close()

    metrics_response = client.get(f"/api/research/{research_id}/metrics", headers=headers)
    assert metrics_response.status_code == 200
    assert metrics_response.json()["evidence_coverage_score"] == 0.0
    assert metrics_response.json()["stage_latency_ms"] == {}

    compliance_response = client.get(f"/api/research/{research_id}/compliance", headers=headers)
    assert compliance_response.status_code == 200
    assert compliance_response.json()["pii_redactions"] == 0
    assert compliance_response.json()["review_required"] is False


def test_export_report_errors_for_missing_and_unsupported_formats() -> None:
    headers = login_headers()
    create_response = client.post(
        "/api/research",
        json={"query": "export checks"},
        headers=headers,
    )
    research_id = create_response.json()["research_id"]

    bad_format_response = client.get(
        f"/api/research/{research_id}/export?format=xml",
        headers=headers,
    )
    assert bad_format_response.status_code == 400
    assert bad_format_response.json()["detail"] == "Unsupported export format"

    db = TestingSessionLocal()
    try:
        summary = db.query(Summary).filter(Summary.research_id == research_id).first()
        assert summary is not None
        db.delete(summary)
        db.commit()
    finally:
        db.close()

    missing_response = client.get(
        f"/api/research/{research_id}/export?format=markdown",
        headers=headers,
    )
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Report not found"


def test_workspace_endpoint_returns_404_when_workspace_missing() -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "missing-workspace@example.com", "password": "strong-password"},
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "missing-workspace@example.com").first()
        assert user is not None
        user.workspace_id = None
        db.add(user)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/workspaces/current", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"

def test_research_endpoints() -> None:
    headers = login_headers()

    create_response = client.post(
        "/api/research",
        json={"query": "AI in healthcare"},
        headers=headers,
    )
    assert create_response.status_code == 200
    research_id = create_response.json()["research_id"]

    list_response = client.get("/api/research", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    detail_response = client.get(f"/api/research/{research_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["summary"]
    assert detail_response.json()["report"]["findings"]
    assert "requires_review" in detail_response.json()

    sources_response = client.get(f"/api/sources/{research_id}", headers=headers)
    assert sources_response.status_code == 200
    assert len(sources_response.json()) == 1

    memory_response = client.get(f"/api/memory/{research_id}", headers=headers)
    assert memory_response.status_code == 200
    assert len(memory_response.json()) == 1

    trace_response = client.get(f"/api/research/{research_id}/trace", headers=headers)
    assert trace_response.status_code == 200
    assert len(trace_response.json()) >= 1

    metrics_response = client.get(f"/api/research/{research_id}/metrics", headers=headers)
    assert metrics_response.status_code == 200
    assert metrics_response.json()["source_count"] == 1
    assert "stage_latency_ms" in metrics_response.json()
    assert "total_latency_ms" in metrics_response.json()
    assert "fact_support_ratio" in metrics_response.json()

    export_markdown_response = client.get(
        f"/api/research/{research_id}/export?format=markdown",
        headers=headers,
    )
    assert export_markdown_response.status_code == 200
    assert "## Findings" in export_markdown_response.text

    export_json_response = client.get(
        f"/api/research/{research_id}/export?format=json",
        headers=headers,
    )
    assert export_json_response.status_code == 200
    assert "findings" in export_json_response.json()

    replay_response = client.get(f"/api/research/{research_id}/replay", headers=headers)
    assert replay_response.status_code == 200
    assert replay_response.json()["research_id"] == research_id
    assert replay_response.json()["timeline"]
    assert "complete" in replay_response.json()["stage_counts"]

    agent_metrics_response = client.get(
        f"/api/research/{research_id}/agent-metrics",
        headers=headers,
    )
    assert agent_metrics_response.status_code == 200
    assert isinstance(agent_metrics_response.json(), list)

    compliance_response = client.get(
        f"/api/research/{research_id}/compliance",
        headers=headers,
    )
    assert compliance_response.status_code == 200
    assert "pii_redactions" in compliance_response.json()

    workspace_response = client.get("/api/workspaces/current", headers=headers)
    assert workspace_response.status_code == 200
    assert workspace_response.json()["name"].endswith("-workspace")

    pause_response = client.post(f"/api/research/{research_id}/pause", headers=headers)
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "paused"
    assert pause_response.json()["is_paused"] is True

    resume_response = client.post(f"/api/research/{research_id}/resume", headers=headers)
    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "planning"
    assert resume_response.json()["is_paused"] is False

    retry_response = client.post(f"/api/research/{research_id}/retry", headers=headers)
    assert retry_response.status_code == 200
    assert retry_response.json()["research_id"] != research_id

    admin = admin_headers()
    audit_response = client.get("/api/audit-logs", headers=admin)
    assert audit_response.status_code == 200
    assert any(item["action"] == "research.create" for item in audit_response.json())



def test_login_reuses_existing_workspace() -> None:
    first = client.post(
        "/api/auth/login",
        json={"email": "shared-workspace@example.com", "password": "pw-one"},
    )
    second = client.post(
        "/api/auth/login",
        json={"email": "shared-workspace@another.com", "password": "pw-two"},
    )
    assert first.status_code == 200
    assert second.status_code == 200

    db = TestingSessionLocal()
    try:
        users = (
            db.query(User)
            .filter(User.email.in_(["shared-workspace@example.com", "shared-workspace@another.com"]))
            .all()
        )
        assert len(users) == 2
        assert users[0].workspace_id is not None
        assert users[0].workspace_id == users[1].workspace_id
    finally:
        db.close()


def test_create_research_skips_audit_when_user_has_no_workspace() -> None:
    login = client.post(
        "/api/auth/login",
        json={"email": "no-workspace-audit@example.com", "password": "pass"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "no-workspace-audit@example.com").first()
        assert user is not None
        user.workspace_id = None
        db.add(user)
        db.commit()
    finally:
        db.close()

    create_response = client.post(
        "/api/research",
        json={"query": "no audit entry expected"},
        headers=headers,
    )
    assert create_response.status_code == 200

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "no-workspace-audit@example.com").first()
        assert user is not None
        # no workspace means audit logging is skipped entirely
        assert db.query(AuditLog).filter(AuditLog.user_id == user.id).count() == 0
        assert db.query(Source).filter(Source.research_id == create_response.json()["research_id"]).count() == 1
        assert db.query(ResearchTraceEvent).filter(ResearchTraceEvent.research_id == create_response.json()["research_id"]).count() >= 1
    finally:
        db.close()


def test_export_markdown_sets_media_type() -> None:
    headers = login_headers()
    create_response = client.post(
        "/api/research",
        json={"query": "markdown export media type"},
        headers=headers,
    )
    research_id = create_response.json()["research_id"]

    response = client.get(f"/api/research/{research_id}/export?format=markdown", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")


def test_unauthenticated_requests_return_401() -> None:
    assert client.get("/api/research").status_code == 401
    assert client.post("/api/research", json={"query": "q"}).status_code == 401
    assert client.get("/api/workspaces/current").status_code == 401
    assert client.get("/api/audit-logs").status_code == 401


def test_cannot_access_another_users_research_returns_404() -> None:
    # Create research as user A
    headers_a = login_headers()
    create_resp = client.post(
        "/api/research",
        json={"query": "user A query"},
        headers=headers_a,
    )
    assert create_resp.status_code == 200
    research_id = create_resp.json()["research_id"]

    # User B logs in with a different email
    resp_b = client.post(
        "/api/auth/login",
        json={"email": "other-user@example.com", "password": "pass"},
    )
    headers_b = {"Authorization": f"Bearer {resp_b.json()['access_token']}"}

    assert client.get(f"/api/research/{research_id}", headers=headers_b).status_code == 404
    assert client.get(f"/api/sources/{research_id}", headers=headers_b).status_code == 404
    assert client.get(f"/api/memory/{research_id}", headers=headers_b).status_code == 404
    assert client.get(f"/api/research/{research_id}/trace", headers=headers_b).status_code == 404
    assert (
        client.get(f"/api/research/{research_id}/metrics", headers=headers_b).status_code == 404
    )


def test_pause_resume_retry_nonexistent_research_returns_404() -> None:
    headers = login_headers()
    assert client.post("/api/research/999999/pause", headers=headers).status_code == 404
    assert client.post("/api/research/999999/resume", headers=headers).status_code == 404
    assert client.post("/api/research/999999/retry", headers=headers).status_code == 404


def test_audit_logs_returns_403_for_non_admin() -> None:
    # Use a fresh email never touched by admin_headers() to guarantee researcher role
    resp = client.post(
        "/api/auth/login",
        json={"email": "non-admin-audit@example.com", "password": "pass"},
    )
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    assert client.get("/api/audit-logs", headers=headers).status_code == 403


def test_plan_preview_returns_structured_plan() -> None:
    headers = login_headers()
    response = client.get(
        "/api/plan-preview",
        params={"query": "AI safety research", "breadth": 2},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "steps" in data
    assert isinstance(data["steps"], list)
    assert len(data["steps"]) >= 1
    assert "sub_question" in data["steps"][0]
    assert "expected_sources" in data["steps"][0]


def test_plan_preview_empty_query_returns_empty_steps() -> None:
    headers = login_headers()
    response = client.get(
        "/api/plan-preview",
        params={"query": "   "},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["steps"] == []


def test_plan_preview_requires_auth() -> None:
    response = client.get("/api/plan-preview", params={"query": "test"})
    assert response.status_code == 401


def test_demo_seed_creates_research_result() -> None:
    headers = login_headers()
    response = client.post("/api/demo/seed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "research_id" in data
    assert "summary" in data
    assert "report" in data
    assert "findings" in data["report"]
    assert len(data["report"]["findings"]) > 0
    assert "confidence_score" in data["report"]
    assert data["report"]["confidence_score"] > 0.0


def test_demo_seed_requires_auth() -> None:
    response = client.post("/api/demo/seed")
    assert response.status_code == 401

