from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "News Verification API"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./news_verification.db"
    NEWSAPI_KEY: str = ""
    GNEWS_KEY: str = ""
    MEDIASTACK_KEY: str = ""
    MAX_ARTICLES_FETCH: int = 40
    MAX_QUERY_EXPANSIONS: int = 3
    USE_EMBEDDINGS: bool = True
    ENABLE_QUERY_EXPANSION: bool = True
    USE_ENTITY_QUERIES: bool = True
    USE_FULLTEXT_QUERY: bool = True
    QUERY_SYNONYMS: str = "election:poll|ballot;president:leader|head of state;court:tribunal|judge;protest:demonstration|rally;attack:assault|incident"
    NEWSAPI_LOAD_FACTOR: int = 2
    GNEWS_LOAD_FACTOR: int = 2
    MEDIASTACK_LOAD_FACTOR: float = 0.5
    SIMILARITY_THRESHOLD: float = 0.50
    HIGH_CREDIBILITY_THRESHOLD: float = 0.85
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _coerce_debug(cls, v):
        if isinstance(v, str) and v.lower() in {"release", "prod", "production"}:
            return False
        return v

settings = Settings()
