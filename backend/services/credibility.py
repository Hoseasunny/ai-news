from urllib.parse import urlparse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import SourceCredibility

class CredibilityScorer:
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}

    def get_score(self, url: str) -> float:
        domain = self._extract_domain(url)
        if domain in self._cache:
            return self._cache[domain]

        result = self.db.execute(
            select(SourceCredibility).where(SourceCredibility.domain == domain)
        ).scalar_one_or_none()
        score = result.score if result else 0.5
        self._cache[domain] = score
        return score

    def calculate_weighted_score(self, articles: list) -> float:
        if not articles:
            return 0.0
        total_weight = 0.0
        weighted_sum = 0.0
        for a in articles:
            sim = float(a.get('similarity_score', 0.0))
            cred = float(a.get('credibility_score', 0.0))
            if sim <= 0:
                continue
            total_weight += sim
            weighted_sum += cred * sim
        if total_weight == 0:
            return 0.0
        return weighted_sum / total_weight

    def _extract_domain(self, url: str) -> str:
        try:
            host = urlparse(url).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            return host or "unknown"
        except Exception:
            return "unknown"