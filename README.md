# AI News Verification System

Professional, production-ready documentation for the AI-Powered News Verification & Source Attribution system.

**Overview**
This application verifies news claims by searching trusted sources, measuring similarity, and applying credibility weighting. Users submit a headline or short article and receive a verdict with sources, confidence, and suggested similar articles.

**Architecture**
- Frontend: React + Vite
- Backend: FastAPI (Python)
- Database: SQLite (SQLAlchemy)
- NLP: spaCy
- Similarity: TF-IDF + optional sentence embeddings
- External APIs: NewsAPI, GNews, MediaStack (optional)

**Key Features**
- Input validation and sanitization
- Multi-provider news search with query expansion
- Similarity scoring (TF-IDF + embeddings)
- Credibility scoring by domain
- Decision engine with configurable thresholds
- Caching by SHA256 hash (24 hours)
- Rate limiting (10 requests/minute/IP)
- Similar news suggestions
- Debug query endpoint
- Extended provider health checks

**Project Structure**
```
backend/
  app/
    main.py
    config.py
    database.py
    models.py
    schemas.py
    routers/
      verify.py
      history.py
      debug.py
  services/
    news_fetcher.py
    nlp_processor.py
    similarity.py
    credibility.py
    decision_engine.py
  utils/
    hashing.py
  scripts/
    clear_history.py
    clear-history.ps1
    start-backend.ps1
    update_seed.py
  tests/
    test_verify.py
  requirements.txt
  .env.example
frontend/
  src/
    components/
    hooks/
    services/
    styles/
    App.jsx
    main.jsx
  package.json
  vite.config.js
```

**Setup**
Backend (Windows):
```
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install --user https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

If your terminal does not auto-load `.env`:
```
cd backend
.\scripts\start-backend.ps1
```

Frontend:
```
cd frontend
npm install
npm run dev
```

**Environment Variables**
Create `backend/.env` from `backend/.env.example`.

Required:
- `NEWSAPI_KEY`
- `GNEWS_KEY`

Optional:
- `MEDIASTACK_KEY`
- `MAX_QUERY_EXPANSIONS`
- `ENABLE_QUERY_EXPANSION`
- `USE_ENTITY_QUERIES`
- `USE_FULLTEXT_QUERY`
- `QUERY_SYNONYMS`
- `NEWSAPI_LOAD_FACTOR`
- `GNEWS_LOAD_FACTOR`
- `MEDIASTACK_LOAD_FACTOR`

Frontend (optional):
- `frontend/.env` with `VITE_API_URL=http://localhost:8000/api/v1`

**Running**
Backend:
```
cd backend
uvicorn app.main:app --reload --port 8000
```

Frontend:
```
cd frontend
npm run dev
```

**API Endpoints**
Base: `http://localhost:8000/api/v1`

- `POST /verify`
  - Body: `{ "text": "...", "include_sources": true, "max_sources": 5 }`
  - Response: status, confidence, summary, sources, suggestions

- `GET /history`
  - Params: `limit`, `offset`, `status`

- `GET /health`
  - Basic health check

- `GET /health/extended`
  - Provider-level status for NewsAPI, GNews, MediaStack

- `GET /debug/queries?text=...`
  - Shows generated search queries, date window, and page size

**Verification Logic (Summary)**
- Input is sanitized, hashed, and checked for cached results (24h).
- Multi-query search is executed against news APIs.
- Articles are scored by similarity and credibility.
- If any high-credibility source is found, the result is **REAL**.
- If no sources are found, the result is **FAKE**.
- Otherwise, the decision engine uses similarity, credibility, and source count.

**Rate Limiting**
- 10 requests per minute per IP.

**Scripts**
- `backend/scripts/clear_history.py`: clear verification history only
- `backend/scripts/clear-history.ps1`: PowerShell helper to clear history
- `backend/scripts/update_seed.py`: add missing credibility domains
- `backend/scripts/start-backend.ps1`: load `.env` and start server

**Testing**
```
python -m pytest backend/tests -q
```

**Troubleshooting**
- If APIs show “unconfigured,” ensure `backend/.env` has keys and restart the backend.
- If spaCy model download fails, use the direct wheel install command in Setup.
- If frontend dev server fails with EPERM, run the terminal as Administrator or reinstall node_modules.