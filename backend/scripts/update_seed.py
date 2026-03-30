from sqlalchemy import select
from app.database import SessionLocal
from app.models import SourceCredibility

SEED = [
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


def main():
    db = SessionLocal()
    try:
        existing = {row[0] for row in db.execute(select(SourceCredibility.domain)).all()}
        added = 0
        for domain, score, category in SEED:
            if domain not in existing:
                db.add(SourceCredibility(domain=domain, score=score, category=category))
                added += 1
        if added:
            db.commit()
        print(f"Added {added} new domains")
    finally:
        db.close()


if __name__ == "__main__":
    main()
