import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models import FetchedSource, VerificationQuery

db = SessionLocal()
try:
    db.query(FetchedSource).delete()
    db.query(VerificationQuery).delete()
    db.commit()
    print("History cleared")
finally:
    db.close()
