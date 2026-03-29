from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, TIMESTAMP, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.database import Base

class VerificationQuery(Base):
    __tablename__ = "verification_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    input_text = Column(Text, nullable=False)
    input_hash = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    confidence_score = Column(Float)
    top_source_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    processing_time_ms = Column(Integer)

    sources = relationship("FetchedSource", back_populates="query", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('real','fake','uncertain')", name="status_check"),
        CheckConstraint("confidence_score BETWEEN 0.0 AND 1.0", name="confidence_check"),
    )

class FetchedSource(Base):
    __tablename__ = "fetched_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("verification_queries.id"), nullable=False)
    title = Column(Text, nullable=False)
    content_snippet = Column(Text)
    source_name = Column(String, nullable=False)
    source_url = Column(Text, nullable=False)
    published_at = Column(TIMESTAMP)
    credibility_score = Column(Float)
    similarity_score = Column(Float)

    query = relationship("VerificationQuery", back_populates="sources")

    __table_args__ = (
        CheckConstraint("credibility_score BETWEEN 0.0 AND 1.0", name="credibility_check"),
        CheckConstraint("similarity_score BETWEEN 0.0 AND 1.0", name="similarity_check"),
    )

class SourceCredibility(Base):
    __tablename__ = "source_credibility"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, unique=True, nullable=False)
    score = Column(Float, nullable=False)
    category = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("score BETWEEN 0.0 AND 1.0", name="source_score_check"),
        CheckConstraint("category IN ('high','medium','low')", name="category_check"),
    )
