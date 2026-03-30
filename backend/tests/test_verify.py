import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from services.decision_engine import DecisionEngine

client = TestClient(app)

def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200


def test_input_validation_too_short():
    resp = client.post("/api/v1/verify", json={"text": "short"})
    assert resp.status_code == 422


def test_decision_engine_real():
    engine = DecisionEngine()
    result = engine.decide(0.2, 0.9, 1, 0.9, True)
    assert result.status == "real"


def test_decision_engine_fake():
    engine = DecisionEngine()
    result = engine.decide(0.1, 0.2, 0, 0.2, False)
    assert result.status == "fake"


def test_decision_engine_uncertain():
    engine = DecisionEngine()
    result = engine.decide(0.5, 0.5, 1, 0.5, False)
    assert result.status == "uncertain"
