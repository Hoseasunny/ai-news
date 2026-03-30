from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
from sqlalchemy import select

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
    from app.models import SourceCredibility
    Base.metadata.create_all(bind=engine)

    # Seed credibility table if empty
    db = SessionLocal()
    try:
        seed = [
                ("bbc.com", 0.95, "high"),
                ("reuters.com", 0.97, "high"),
                ("apnews.com", 0.96, "high"),
                ("nytimes.com", 0.94, "high"),
                ("theguardian.com", 0.93, "high"),
                ("washingtonpost.com", 0.92, "high"),
                ("wsj.com", 0.93, "high"),
                ("bloomberg.com", 0.92, "high"),
                ("npr.org", 0.90, "high"),
                ("cnbc.com", 0.88, "high"),
                ("cnn.com", 0.85, "medium"),
                ("foxnews.com", 0.75, "medium"),
                ("nbcnews.com", 0.86, "medium"),
                ("abcnews.go.com", 0.86, "medium"),
                ("cbsnews.com", 0.85, "medium"),
                ("usatoday.com", 0.83, "medium"),
                ("time.com", 0.85, "medium"),
                ("thehill.com", 0.80, "medium"),
                ("politico.com", 0.84, "medium"),
                ("nation.africa", 0.88, "high"),
                ("standardmedia.co.ke", 0.84, "medium"),
                ("the-star.co.ke", 0.80, "medium"),
                ("capitalfm.co.ke", 0.78, "medium"),
                ("citizen.digital", 0.82, "medium"),
                ("ktnkenya.tv", 0.80, "medium"),
                ("kbc.co.ke", 0.76, "medium"),
                ("tuko.co.ke", 0.72, "medium"),
                ("people.co.ke", 0.75, "medium"),
                ("businessdailyafrica.com", 0.83, "medium"),
                ("aljazeera.com", 0.90, "high"),
                ("buzzfeed.com", 0.60, "low"),
                ("unknown", 0.50, "low"),
            ]

        existing_domains = {
            row[0]
            for row in db.execute(select(SourceCredibility.domain)).all()
        }
        for domain, score, category in seed:
            if domain not in existing_domains:
                db.add(SourceCredibility(domain=domain, score=score, category=category))
        db.commit()
    finally:
        db.close()
