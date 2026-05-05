from urllib.parse import quote_plus

import requests


class SearchTool:
    def search(self, query: str) -> list[str]:
        """Search Wikipedia using both opensearch and full-text search for broader coverage."""
        results: list[str] = []

        # OpenSearch — fast suggestion-based lookup
        try:
            opensearch_url = (
                f"https://en.wikipedia.org/w/api.php"
                f"?action=opensearch&format=json&search={quote_plus(query)}&limit=3"
            )
            payload = requests.get(opensearch_url, timeout=10).json()
            links = payload[3] if isinstance(payload, list) and len(payload) > 3 else []
            results.extend(links)
        except Exception:
            pass

        # Full-text search — finds more relevant articles the suggestion index may miss
        try:
            fulltext_url = (
                f"https://en.wikipedia.org/w/api.php"
                f"?action=query&list=search&srsearch={quote_plus(query)}"
                f"&format=json&srlimit=4"
            )
            data = requests.get(fulltext_url, timeout=10).json()
            search_items = data.get("query", {}).get("search", [])
            for item in search_items:
                title = item.get("title", "")
                if title:
                    results.append(f"https://en.wikipedia.org/wiki/{quote_plus(title)}")
        except Exception:
            pass

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for link in results:
            if link not in seen:
                seen.add(link)
                unique.append(link)
        return unique[:6]
