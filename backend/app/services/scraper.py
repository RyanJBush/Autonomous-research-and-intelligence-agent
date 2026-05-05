from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


class Scraper:
    def extract(self, url: str) -> dict:
        """Extract page content plus metadata.

        Returns a dict with keys: title, content, source_author, published_at, retrieved_at.
        """
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.string.strip() if soup.title and soup.title.string else url)[:500]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        content = " ".join(p for p in paragraphs if p)
        retrieved_at = datetime.now(timezone.utc)

        # Extract author from common meta tags
        source_author = self._extract_author(soup)

        # Extract published date from common meta tags
        published_at = self._extract_published_at(soup)

        return {
            "title": title,
            "content": content[:5000],
            "source_author": source_author,
            "published_at": published_at,
            "retrieved_at": retrieved_at,
        }

    def _extract_author(self, soup: BeautifulSoup) -> str | None:
        author_metas = [
            {"name": "author"},
            {"property": "article:author"},
            {"name": "dc.creator"},
            {"name": "byl"},
        ]
        for attrs in author_metas:
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                value = str(tag["content"]).strip()
                if value:
                    return value[:255]
        # Fallback: look for byline or author span
        for selector in ("span.author", "a[rel='author']", "span.byline", ".author-name"):
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:255]
        return None

    def _extract_published_at(self, soup: BeautifulSoup) -> datetime | None:
        date_metas = [
            {"property": "article:published_time"},
            {"name": "date"},
            {"name": "pubdate"},
            {"name": "dc.date"},
            {"itemprop": "datePublished"},
        ]
        for attrs in date_metas:
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                try:
                    return datetime.fromisoformat(str(tag["content"]).rstrip("Z"))
                except ValueError:
                    continue
        # Fallback: time element with datetime attribute
        time_tag = soup.find("time", attrs={"datetime": True})
        if time_tag:
            try:
                return datetime.fromisoformat(str(time_tag["datetime"]).rstrip("Z"))
            except ValueError:
                pass
        return None
