import re

_MIN_EXCERPT_LEN = 50
_MAX_EXCERPT_LEN = 240


class CitationSystem:
    def build(self, sources: list[dict[str, str]]) -> list[dict[str, str | int]]:
        citations: list[dict[str, str | int]] = []
        for idx, source in enumerate(sources, start=1):
            citations.append(
                {
                    "marker": f"[{idx}]",
                    "excerpt": self._extract_excerpt(source.get("content", "")),
                    "source_index": idx - 1,
                }
            )
        return citations

    def _extract_excerpt(self, content: str) -> str:
        """Return the first meaningful sentence from the content.

        Falls back to the first ``_MAX_EXCERPT_LEN`` characters if no
        sentence meeting the minimum length threshold is found.
        """
        # Split on sentence-ending punctuation while keeping boundaries
        sentences = re.split(r"(?<=[.!?])\s+", content.strip())
        for sentence in sentences:
            clean = sentence.strip()
            if len(clean) >= _MIN_EXCERPT_LEN:
                return clean[:_MAX_EXCERPT_LEN]
        return content[:_MAX_EXCERPT_LEN]
