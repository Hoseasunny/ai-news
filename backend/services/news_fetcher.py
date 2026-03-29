import httpx
import asyncio
from typing import List, Dict
from urllib.parse import urlparse, urlunparse
from app.config import settings
import spacy

class NewsFetcher:
    def __init__(self):
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.gnews_url = "https://gnews.io/api/v4/search"
        self._nlp = None

    async def fetch_articles(self, query: str, max_results: int = None) -> List[Dict]:
        if max_results is None:
            max_results = settings.MAX_ARTICLES_FETCH

        keywords = self._extract_keywords(query)
        page_size = max(1, max_results // 2)

        tasks = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            if settings.NEWSAPI_KEY:
                params = {
                    "q": keywords,
                    "pageSize": page_size,
                    "language": "en",
                    "sortBy": "relevancy",
                    "apiKey": settings.NEWSAPI_KEY,
                }
                tasks.append(self._fetch_newsapi(client, params))
            if settings.GNEWS_KEY:
                params = {
                    "q": keywords,
                    "max": page_size,
                    "lang": "en",
                    "token": settings.GNEWS_KEY,
                }
                tasks.append(self._fetch_gnews(client, params))

            if not tasks:
                return []

            results = await asyncio.gather(*tasks)

        merged = []
        for batch in results:
            merged.extend(batch)

        deduped = []
        seen = set()
        for item in merged:
            norm = self._normalize_url(item.get("url", ""))
            if not norm or norm in seen:
                continue
            seen.add(norm)
            item["url"] = norm
            deduped.append(item)

        return deduped

    async def _fetch_newsapi(self, client: httpx.AsyncClient, params: Dict) -> List[Dict]:
        try:
            resp = await client.get(self.newsapi_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            return [
                {
                    "title": a.get("title") or "",
                    "description": a.get("description") or "",
                    "url": a.get("url") or "",
                    "source": (a.get("source") or {}).get("name") or "",
                    "publishedAt": a.get("publishedAt"),
                }
                for a in articles
                if a.get("title") and a.get("url")
            ]
        except Exception:
            return []

    async def _fetch_gnews(self, client: httpx.AsyncClient, params: Dict) -> List[Dict]:
        try:
            resp = await client.get(self.gnews_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            return [
                {
                    "title": a.get("title") or "",
                    "description": a.get("description") or "",
                    "url": a.get("url") or "",
                    "source": (a.get("source") or {}).get("name") or "",
                    "publishedAt": a.get("publishedAt"),
                }
                for a in articles
                if a.get("title") and a.get("url")
            ]
        except Exception:
            return []

    def _extract_keywords(self, text: str) -> str:
        if not self._nlp:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:
                self._nlp = None
        if not self._nlp:
            tokens = [t for t in text.split() if len(t) > 2]
            return " ".join(tokens[:5])

        doc = self._nlp(text)
        keywords = [t.lemma_ for t in doc if t.pos_ in {"NOUN", "PROPN"} and not t.is_stop]
        if not keywords:
            keywords = [t.lemma_ for t in doc if not t.is_stop and t.is_alpha]
        return " ".join(keywords[:5])

    def _normalize_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            clean = parsed._replace(query="", fragment="")
            normalized = urlunparse(clean).rstrip("/")
            return normalized.lower()
        except Exception:
            return url
