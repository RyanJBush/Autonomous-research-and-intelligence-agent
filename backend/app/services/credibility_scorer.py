from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse


@dataclass
class CredibilityResult:
    credibility_score: float
    credibility_label: str
    source_type: str


class CredibilityScorer:
    DOMAIN_TIERS = {
        "academic": 1.0,
        "gov": 0.95,
        "news": 0.75,
        "blog": 0.45,
        "unknown": 0.3,
    }

    def score(
        self,
        *,
        url: str,
        content: str,
        published_at: datetime | None = None,
    ) -> CredibilityResult:
        source_type = self._domain_tier(url)
        domain_score = self.DOMAIN_TIERS[source_type]
        https_score = 1.0 if url.lower().startswith("https://") else 0.4
        recency_score = self._recency_score(published_at)
        citation_count = max(content.count("["), content.lower().count("according to"))
        citation_score = min(1.0, citation_count / 8)

        score = (
            0.45 * domain_score
            + 0.15 * https_score
            + 0.2 * recency_score
            + 0.2 * citation_score
        )
        score = round(max(0.0, min(1.0, score)), 3)
        return CredibilityResult(
            credibility_score=score,
            credibility_label=self._label(score),
            source_type=source_type,
        )

    def _domain_tier(self, url: str) -> str:
        host = (urlparse(url).hostname or "").lower()
        if host.endswith(".gov") or host.endswith(".mil"):
            return "gov"
        if host.endswith(".edu") or "nature.com" in host or "science.org" in host:
            return "academic"
        news_tokens = ("reuters", "apnews", "bbc", "nytimes", "wsj", "bloomberg")
        if any(token in host for token in news_tokens):
            return "news"
        if host:
            return "blog"
        return "unknown"

    def _recency_score(self, published_at: datetime | None) -> float:
        if published_at is None:
            return 0.5
        now = datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        days_old = max(0, (now - published_at).days)
        if days_old <= 30:
            return 1.0
        if days_old <= 180:
            return 0.8
        if days_old <= 365:
            return 0.65
        if days_old <= 730:
            return 0.45
        return 0.25

    def _label(self, score: float) -> str:
        if score >= 0.75:
            return "High"
        if score >= 0.5:
            return "Medium"
        if score > 0:
            return "Low"
        return "Unknown"
