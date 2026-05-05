import logging
from urllib.parse import quote_plus

import requests

logger = logging.getLogger(__name__)

_DDG_TIMEOUT = 8
_WIKI_TIMEOUT = 10
_MAX_RESULTS = 5


class SearchTool:
    """Search tool that queries Wikipedia and DuckDuckGo Instant Answer API."""

    def search(self, query: str) -> list[str]:
        urls: list[str] = []
        urls.extend(self._duckduckgo_search(query))
        urls.extend(self._wikipedia_search(query))
        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                deduped.append(url)
        return deduped[:_MAX_RESULTS]

    def _wikipedia_search(self, query: str) -> list[str]:
        """Search Wikipedia OpenSearch API and return article URLs."""
        try:
            url = (
                "https://en.wikipedia.org/w/api.php"
                f"?action=opensearch&format=json&limit={_MAX_RESULTS}"
                f"&search={quote_plus(query)}"
            )
            response = requests.get(url, timeout=_WIKI_TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            return payload[3] if isinstance(payload, list) and len(payload) > 3 else []
        except Exception:
            logger.debug("Wikipedia search failed for: %s", query)
            return []

    def _duckduckgo_search(self, query: str) -> list[str]:
        """Query DuckDuckGo Instant Answer API for related topic URLs."""
        try:
            url = (
                "https://api.duckduckgo.com/"
                f"?q={quote_plus(query)}&format=json&no_html=1&no_redirect=1&t=astraai"
            )
            response = requests.get(url, timeout=_DDG_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            urls: list[str] = []
            # AbstractURL is the primary Wikipedia/official page
            abstract_url = data.get("AbstractURL", "")
            if abstract_url and abstract_url.startswith("http"):
                urls.append(abstract_url)
            # RelatedTopics sometimes contain useful first-party links
            for topic in data.get("RelatedTopics", []):
                first_url = topic.get("FirstURL", "") if isinstance(topic, dict) else ""
                if first_url and first_url.startswith("http") and first_url not in urls:
                    urls.append(first_url)
                    if len(urls) >= _MAX_RESULTS:
                        break
            return urls
        except Exception:
            logger.debug("DuckDuckGo search failed for: %s", query)
            return []
