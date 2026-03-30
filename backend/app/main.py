from fastapi import FastAPI
import httpx
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import verify, history, debug
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(verify.router)
app.include_router(history.router)
app.include_router(debug.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "news_api": "available" if settings.NEWSAPI_KEY or settings.GNEWS_KEY else "unconfigured",
        "version": "1.0.0",
    }


@app.get("/api/v1/health/extended")
async def health_extended():
    results = {
        "newsapi": "unconfigured",
        "gnews": "unconfigured",
        "mediastack": "unconfigured",
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        if settings.NEWSAPI_KEY:
            try:
                resp = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": "news",
                        "pageSize": 1,
                        "language": "en",
                        "sortBy": "relevancy",
                        "apiKey": settings.NEWSAPI_KEY,
                    },
                )
                results["newsapi"] = "available" if resp.status_code == 200 else f"error:{resp.status_code}"
            except Exception:
                results["newsapi"] = "error"

        if settings.GNEWS_KEY:
            try:
                resp = await client.get(
                    "https://gnews.io/api/v4/search",
                    params={
                        "q": "news",
                        "max": 1,
                        "lang": "en",
                        "token": settings.GNEWS_KEY,
                    },
                )
                results["gnews"] = "available" if resp.status_code == 200 else f"error:{resp.status_code}"
            except Exception:
                results["gnews"] = "error"

        if settings.MEDIASTACK_KEY:
            try:
                resp = await client.get(
                    "http://api.mediastack.com/v1/news",
                    params={
                        "access_key": settings.MEDIASTACK_KEY,
                        "keywords": "news",
                        "languages": "en",
                        "limit": 1,
                    },
                )
                results["mediastack"] = "available" if resp.status_code == 200 else f"error:{resp.status_code}"
            except Exception:
                results["mediastack"] = "error"

    return {
        "status": "healthy",
        "database": "connected",
        "providers": results,
        "version": "1.0.0",
    }
