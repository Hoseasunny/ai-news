from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
import time
import re

from app.database import get_db
from app.schemas import VerifyRequest, VerifyResponse, SourceOut
from app.models import VerificationQuery, FetchedSource
from services.news_fetcher import NewsFetcher
from services.nlp_processor import NLPProcessor
from services.similarity import SimilarityEngine
from services.credibility import CredibilityScorer
from services.decision_engine import DecisionEngine
from utils.hashing import hash_input
from app.limiter import limiter

router = APIRouter(prefix="/api/v1")

@router.post("/verify", response_model=VerifyResponse)
@limiter.limit("10/minute")
async def verify_news(
    request: Request,
    payload: VerifyRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()

    # 1. Validate input
    text = re.sub(r"<[^>]*?>", "", payload.text).strip()
    if len(text) < 10:
        raise HTTPException(422, "Input too short (min 10 characters)")
    if len(text) > 5000:
        raise HTTPException(422, "Input too long (max 5000 characters)")

    # 2. Cache check
    input_hash = hash_input(text)
    cutoff = datetime.utcnow() - timedelta(hours=24)
    cached_query = db.execute(
        select(VerificationQuery).where(
            VerificationQuery.input_hash == input_hash,
            VerificationQuery.created_at >= cutoff
        )
    ).scalar_one_or_none()

    if cached_query:
        sources = [
            SourceOut(
                title=s.title,
                source=s.source_name,
                url=s.source_url,
                credibility_score=s.credibility_score or 0.0,
                similarity_score=s.similarity_score or 0.0,
                published_at=s.published_at,
            )
            for s in cached_query.sources
        ]
        return VerifyResponse(
            query_id=cached_query.id,
            status=cached_query.status,
            confidence=cached_query.confidence_score or 0.0,
            summary="Cached result",
            sources=sources[: payload.max_sources] if payload.include_sources else [],
            processing_time_ms=int((time.time() - start_time) * 1000),
            cached=True,
        )

    # 3. Initialize services
    fetcher = NewsFetcher()
    nlp = NLPProcessor()
    similarity = SimilarityEngine()

    # 4. Fetch articles
    try:
        articles = await fetcher.fetch_articles(text)
    except Exception:
        articles = []

    # 5. Process and score
    _ = nlp.process(text)
    processed_articles = similarity.calculate_similarity(text, articles)

    # 6. Credibility scores
    scorer = CredibilityScorer(db)
    for article in processed_articles:
        article['credibility_score'] = scorer.get_score(article.get('url', ''))

    # 7. Sort by combined score
    processed_articles.sort(
        key=lambda x: x.get('similarity_score', 0.0) * x.get('credibility_score', 0.0),
        reverse=True
    )

    # 8. Decision
    engine = DecisionEngine()
    best_match = processed_articles[0] if processed_articles else None
    result = engine.decide(
        similarity_score=best_match.get('similarity_score', 0.0) if best_match else 0.0,
        credibility_score=scorer.calculate_weighted_score(processed_articles),
        source_count=len(processed_articles),
        top_source_credibility=best_match.get('credibility_score', 0.0) if best_match else 0.0
    )

    # 9. Save to database
    new_query = VerificationQuery(
        input_text=text,
        input_hash=input_hash,
        status=result.status,
        confidence_score=result.confidence,
        processing_time_ms=int((time.time() - start_time) * 1000),
    )
    db.add(new_query)
    db.flush()

    sources_to_store = processed_articles[: payload.max_sources]
    top_source_id = None
    for idx, a in enumerate(sources_to_store):
        fs = FetchedSource(
            query_id=new_query.id,
            title=a.get('title', ''),
            content_snippet=a.get('description', ''),
            source_name=(a.get('source') or a.get('url', 'unknown')),
            source_url=a.get('url', ''),
            published_at=_parse_published_at(a.get('publishedAt')),
            credibility_score=a.get('credibility_score', 0.0),
            similarity_score=a.get('similarity_score', 0.0),
        )
        db.add(fs)
        db.flush()
        if idx == 0:
            top_source_id = fs.id

    if top_source_id:
        new_query.top_source_id = top_source_id

    db.commit()

    # 10. Response
    processing_time = int((time.time() - start_time) * 1000)
    sources_out = [
        SourceOut(
            title=a.get('title', ''),
            source=_source_domain(a.get('url', '')),
            url=a.get('url', ''),
            credibility_score=a.get('credibility_score', 0.0),
            similarity_score=a.get('similarity_score', 0.0),
            published_at=_parse_published_at(a.get('publishedAt')),
        )
        for a in sources_to_store
    ]

    return VerifyResponse(
        query_id=new_query.id,
        status=result.status,
        confidence=result.confidence,
        summary=result.reasoning,
        sources=sources_out if payload.include_sources else [],
        processing_time_ms=processing_time,
        cached=False
    )


def _parse_published_at(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _source_domain(url: str) -> str:
    from urllib.parse import urlparse
    try:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or "unknown"
    except Exception:
        return "unknown"
