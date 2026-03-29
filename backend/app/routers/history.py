from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database import get_db
from app.models import VerificationQuery
from app.schemas import HistoryResponse, HistoryItem

router = APIRouter(prefix="/api/v1")

@router.get("/history", response_model=HistoryResponse)
def get_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    base_query = select(VerificationQuery)
    if status in {"real", "fake", "uncertain"}:
        base_query = base_query.where(VerificationQuery.status == status)

    total = db.execute(
        select(func.count()).select_from(base_query.subquery())
    ).scalar_one()

    rows = db.execute(
        base_query.order_by(VerificationQuery.created_at.desc()).limit(limit).offset(offset)
    ).scalars().all()

    items = [
        HistoryItem(
            query_id=r.id,
            input_preview=(r.input_text[:60] + "...") if len(r.input_text) > 60 else r.input_text,
            status=r.status,
            confidence=r.confidence_score or 0.0,
            created_at=r.created_at,
        )
        for r in rows
    ]

    return HistoryResponse(total=total, items=items)