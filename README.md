# AI News Verification System

## Quick Start

### Backend
```
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install --user https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
uvicorn app.main:app --reload --port 8000
```

If your terminal doesn't auto-load `.env`, you can use:
```
cd backend
.\scripts\start-backend.ps1
```

### Frontend
```
cd frontend
npm install
npm run dev
```

## Environment Variables
Create `backend/.env` from `backend/.env.example` and set:
- `NEWSAPI_KEY`
- `GNEWS_KEY`
- `MEDIASTACK_KEY` (optional, adds another news source)

Optional frontend:
- `frontend/.env` with `VITE_API_URL=http://localhost:8000/api/v1`

## Tests
```
python -m pytest backend/tests -q
```

## Debug Queries
See which search queries are generated for a given input:
```
http://127.0.0.1:8000/api/v1/debug/queries?text=your%20headline%20here
```

## API Health (Extended)
Check each provider directly:
```
http://127.0.0.1:8000/api/v1/health/extended
```

## Frontend Provider Status
The UI now includes an **API Status** card that shows each provider’s availability.

## Similar News Suggestions
Each verification response now includes a `suggestions` list with the next 3 most similar articles.

## Clear History (Keep Credibility)
```
cd backend
python scripts/clear_history.py
```
