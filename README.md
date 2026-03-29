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

Optional frontend:
- `frontend/.env` with `VITE_API_URL=http://localhost:8000/api/v1`

## Tests
```
python -m pytest backend/tests -q
```