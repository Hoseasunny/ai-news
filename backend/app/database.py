from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from app.models import SourceCredibility

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Seed credibility table if empty
    db = SessionLocal()
    try:
        existing = db.execute(select(SourceCredibility)).first()
        if not existing:
            seed = [
                ("bbc.com", 0.95, "high"),
                ("reuters.com", 0.97, "high"),
                ("apnews.com", 0.96, "high"),
                ("nytimes.com", 0.94, "high"),
                ("theguardian.com", 0.93, "high"),
                ("washingtonpost.com", 0.92, "high"),
                ("cnn.com", 0.85, "medium"),
                ("foxnews.com", 0.75, "medium"),
                ("buzzfeed.com", 0.60, "low"),
                ("unknown", 0.50, "low"),
            ]
            for domain, score, category in seed:
                db.add(SourceCredibility(domain=domain, score=score, category=category))
            db.commit()
    finally:
        db.close()