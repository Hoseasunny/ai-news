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
from services.decision_engine import DecisionEngine, DecisionResult
from utils.hashing import hash_input
from app.limiter import limiter
from app.config import settings

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
        trace = {"cached": True}
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
        if payload.include_sources:
            sources = sources[: payload.max_sources]
        else:
            sources = []
        suggestions = [
            SourceOut(
                title=s.title,
                source=s.source_name,
                url=s.source_url,
                credibility_score=s.credibility_score or 0.0,
                similarity_score=s.similarity_score or 0.0,
                published_at=s.published_at,
            )
            for s in cached_query.sources[payload.max_sources:payload.max_sources + 3]
        ]
        return VerifyResponse(
            query_id=cached_query.id,
            status=cached_query.status,
            confidence=cached_query.confidence_score or 0.0,
            summary="Cached result",
            sources=sources,
            suggestions=suggestions,
            reasons=["Cached result"],
            decision_trace=trace,
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

    reasons = []

    # 5. Process and score
    _ = nlp.process(text)
    processed_articles = similarity.calculate_similarity(text, articles)

    # 6. Credibility scores
    scorer = CredibilityScorer(db)
    filtered = []
    for article in processed_articles:
        score, known, blacklisted = scorer.get_score(article.get('url', ''))
        if blacklisted:
            continue
        domain = _source_domain(article.get('url', ''))
        if settings.ENFORCE_WHITELIST and not known:
            continue
        article['credibility_score'] = score
        article['domain'] = domain
        filtered.append(article)
    processed_articles = filtered

    # 7. Pre-calc high-cred signals
    has_high_cred_source = any(
        (a.get('credibility_score', 0.0) or 0.0) >= settings.HIGH_CREDIBILITY_THRESHOLD
        for a in processed_articles
    )
    high_cred_count = sum(
        1 for a in processed_articles
        if (a.get('credibility_score', 0.0) or 0.0) >= settings.HIGH_CREDIBILITY_THRESHOLD
    )

    # 8. Sort by score
    if has_high_cred_source:
        # If a high-cred domain exists, ignore similarity when ranking
        processed_articles.sort(
            key=lambda x: x.get('credibility_score', 0.0),
            reverse=True
        )
    else:
        processed_articles.sort(
            key=lambda x: x.get('similarity_score', 0.0) * x.get('credibility_score', 0.0),
            reverse=True
        )

    # 9. Decision
    engine = DecisionEngine()
    best_match = processed_articles[0] if processed_articles else None
    if has_high_cred_source:
        agreeing_sources = high_cred_count
    else:
        agreeing_sources = sum(
            1 for a in processed_articles
            if (a.get('credibility_score', 0.0) or 0.0) >= settings.HIGH_CREDIBILITY_THRESHOLD
            and (a.get('similarity_score', 0.0) or 0.0) >= settings.HIGH_CRED_MIN_SIMILARITY
        )
    is_sensitive = _is_sensitive(text)
    avg_source_similarity = 1.0 if has_high_cred_source else similarity.pairwise_similarity(processed_articles)
    freshness_penalty, freshness_reason = _freshness_penalty(processed_articles, text)
    if freshness_reason:
        reasons.append(freshness_reason)

    trace = {
        "source_count": len(processed_articles),
        "high_cred_count": high_cred_count,
        "agreeing_sources": agreeing_sources,
        "avg_source_similarity": avg_source_similarity,
        "freshness_penalty": freshness_penalty,
        "is_sensitive": is_sensitive,
        "similarity_score": best_match.get("similarity_score", 0.0) if best_match else 0.0,
        "credibility_score": scorer.calculate_weighted_score(processed_articles),
        "top_source_credibility": best_match.get("credibility_score", 0.0) if best_match else 0.0,
        "whitelist_enforced": settings.ENFORCE_WHITELIST,
        "blacklist_active": bool(settings.BLACKLIST_DOMAINS.strip()),
    }

    if not processed_articles:
        result = DecisionResult(
            status="fake",
            confidence=0.75,
            reasoning="No sources found to verify this claim",
        )
        reasons.append("No sources matched the whitelist/blacklist rules")
    else:
        if settings.ENFORCE_WHITELIST:
            reasons.append("Whitelist enforcement enabled")
        if settings.BLACKLIST_DOMAINS.strip():
            reasons.append("Blacklist filtering applied")
        if high_cred_count >= 2:
            reasons.append("Multiple high-credibility sources found")
        elif has_high_cred_source:
            reasons.append("At least one high-credibility source found")
        if avg_source_similarity < 0.3:
            reasons.append("Low agreement across sources")
        result = engine.decide(
            similarity_score=best_match.get('similarity_score', 0.0) if best_match else 0.0,
            credibility_score=scorer.calculate_weighted_score(processed_articles),
            source_count=len(processed_articles),
            top_source_credibility=best_match.get('credibility_score', 0.0) if best_match else 0.0,
            has_high_cred_source=has_high_cred_source,
            is_sensitive=is_sensitive,
            agreeing_sources=agreeing_sources,
            avg_source_similarity=avg_source_similarity,
            freshness_penalty=freshness_penalty
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
    suggestions_out = [
        SourceOut(
            title=a.get('title', ''),
            source=_source_domain(a.get('url', '')),
            url=a.get('url', ''),
            credibility_score=a.get('credibility_score', 0.0),
            similarity_score=a.get('similarity_score', 0.0),
            published_at=_parse_published_at(a.get('publishedAt')),
        )
        for a in processed_articles[payload.max_sources:payload.max_sources + 3]
    ]

    return VerifyResponse(
        query_id=new_query.id,
        status=result.status,
        confidence=result.confidence,
        summary=result.reasoning,
        sources=sources_out if payload.include_sources else [],
        suggestions=suggestions_out,
        reasons=reasons,
        decision_trace=trace,
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


def _is_sensitive(text: str) -> bool:
    import re
    pattern = re.compile(rf"\\b({settings.SENSITIVE_KEYWORDS})\\b", re.IGNORECASE)
    return bool(pattern.search(text))


def _freshness_penalty(articles, text: str):
    if not articles:
        return 0.0, None
    latest = None
    for a in articles:
        dt = _parse_published_at(a.get("publishedAt"))
        if not dt:
            continue
        if latest is None or dt > latest:
            latest = dt
    if not latest:
        return 0.0, None

    age_days = (datetime.utcnow() - latest.replace(tzinfo=None)).days
    breaking = _is_breaking(text)
    if breaking and age_days > settings.FRESHNESS_SOFT_DAYS:
        return 0.15, "Claim appears time-sensitive but sources are not recent"
    if age_days > settings.FRESHNESS_HARD_DAYS:
        return 0.2, "Sources are older than expected for a current claim"
    return 0.0, None


def _is_breaking(text: str) -> bool:
    import re
    pattern = re.compile(rf"\\b({settings.BREAKING_KEYWORDS})\\b", re.IGNORECASE)
    return bool(pattern.search(text))
