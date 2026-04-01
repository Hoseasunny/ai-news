from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class VerifyRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    include_sources: bool = True
    max_sources: int = Field(5, ge=1, le=20)

class SourceOut(BaseModel):
    title: str
    source: str
    url: str
    credibility_score: float
    similarity_score: float
    published_at: Optional[datetime] = None

class VerifyResponse(BaseModel):
    query_id: int
    status: Literal['real', 'fake', 'uncertain']
    confidence: float
    summary: str
    sources: List[SourceOut]
    suggestions: List[SourceOut] = []
    reasons: List[str] = []
    decision_trace: dict = {}
    processing_time_ms: int
    cached: bool

class HistoryItem(BaseModel):
    query_id: int
    input_preview: str
    status: Literal['real', 'fake', 'uncertain']
    confidence: float
    created_at: datetime

class HistoryResponse(BaseModel):
    total: int
    items: List[HistoryItem]
