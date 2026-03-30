import httpx
import asyncio
from typing import List, Dict, Iterable
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta
from app.config import settings
import spacy

class NewsFetcher:
    def __init__(self):
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.gnews_url = "https://gnews.io/api/v4/search"
        self.mediastack_url = "http://api.mediastack.com/v1/news"
        self._nlp = None

    async def fetch_articles(self, query: str, max_results: int = None) -> List[Dict]:
        if max_results is None:
            max_results = settings.MAX_ARTICLES_FETCH

        plan = self.build_query_plan(query, max_results)
        queries = plan["queries"]
        page_size = plan["page_size"]
        date_from = plan["date_from"]
        date_to = plan["date_to"]

        tasks = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for q in queries:
                if settings.NEWSAPI_KEY:
                    params = {
                        "q": q,
                        "pageSize": page_size,
                        "language": "en",
                        "sortBy": "relevancy",
                        "apiKey": settings.NEWSAPI_KEY,
                    }
                    if date_from:
                        params["from"] = date_from
                    tasks.append(self._fetch_newsapi(client, params))
                if settings.GNEWS_KEY:
                    params = {
                        "q": q,
                        "max": page_size,
                        "lang": "en",
                        "token": settings.GNEWS_KEY,
                    }
                    if date_from:
                        params["from"] = date_from
                    tasks.append(self._fetch_gnews(client, params))
                if settings.MEDIASTACK_KEY:
                    params = {
                        "access_key": settings.MEDIASTACK_KEY,
                        "keywords": q,
                        "languages": "en",
                        "limit": page_size,
                    }
                    if date_from:
                        params["date"] = f"{date_from},{date_to}"
                    tasks.append(self._fetch_mediastack(client, params))

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

    def build_query_plan(self, query: str, max_results: int = None) -> Dict:
        if max_results is None:
            max_results = settings.MAX_ARTICLES_FETCH

        keywords = self._extract_keywords(query)
        entities = self._extract_entities(query) if settings.USE_ENTITY_QUERIES else []
        expansions = self._expand_queries(query, keywords, entities)
        queries = list(self._dedupe_queries(expansions))[: settings.MAX_QUERY_EXPANSIONS]
        if not queries:
            queries = [keywords or query]

        page_size = max(1, max_results // max(1, len(queries)) // 2)
        date_from = self._extract_date_window(query)
        date_to = datetime.utcnow().strftime("%Y-%m-%d")

        return {
            "queries": queries,
            "page_size": page_size,
            "date_from": date_from,
            "date_to": date_to,
            "max_results": max_results,
        }

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

    async def _fetch_mediastack(self, client: httpx.AsyncClient, params: Dict) -> List[Dict]:
        try:
            resp = await client.get(self.mediastack_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("data", [])
            return [
                {
                    "title": a.get("title") or "",
                    "description": a.get("description") or "",
                    "url": a.get("url") or "",
                    "source": a.get("source") or "",
                    "publishedAt": a.get("published_at"),
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

    def _extract_entities(self, text: str) -> List[str]:
        if not self._nlp:
            return []
        doc = self._nlp(text)
        ents = [ent.text for ent in doc.ents if ent.label_ in {"PERSON", "ORG", "GPE", "LOC"}]
        return ents[:5]

    def _expand_queries(self, text: str, keywords: str, entities: List[str]) -> Iterable[str]:
        base = text.strip()
        expansions = []
        if keywords:
            expansions.append(keywords)
        if entities and settings.USE_ENTITY_QUERIES:
            expansions.append(" ".join(entities))
        if base and settings.USE_FULLTEXT_QUERY:
            expansions.append(base)
        if settings.ENABLE_QUERY_EXPANSION:
            synonyms = self._parse_synonyms(settings.QUERY_SYNONYMS)
            lowered = base.lower()
            for key, syns in synonyms.items():
                if key in lowered:
                    expansions.append(base + " " + " ".join(syns[:2]))
        return expansions

    def _parse_synonyms(self, raw: str) -> Dict[str, List[str]]:
        mapping: Dict[str, List[str]] = {}
        if not raw:
            return mapping
        for group in raw.split(";"):
            if ":" not in group:
                continue
            key, vals = group.split(":", 1)
            synonyms = [v.strip() for v in vals.split("|") if v.strip()]
            if key.strip() and synonyms:
                mapping[key.strip().lower()] = synonyms
        return mapping

    def _dedupe_queries(self, queries: Iterable[str]) -> Iterable[str]:
        seen = set()
        for q in queries:
            clean = " ".join(q.split())
            if not clean:
                continue
            if clean.lower() in seen:
                continue
            seen.add(clean.lower())
            yield clean

    def _extract_date_window(self, text: str) -> str | None:
        if not self._nlp:
            return None
        doc = self._nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                # Use a loose window: last 60 days if any date present
                return (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d")
        return None

    def _normalize_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            clean = parsed._replace(query="", fragment="")
            normalized = urlunparse(clean).rstrip("/")
            return normalized.lower()
        except Exception:
            return url
