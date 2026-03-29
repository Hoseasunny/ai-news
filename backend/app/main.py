from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import verify, history
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
