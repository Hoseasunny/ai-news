from fastapi import APIRouter, Query
from services.news_fetcher import NewsFetcher

router = APIRouter(prefix="/api/v1")

@router.get("/debug/queries")
def debug_queries(text: str = Query(..., min_length=3, max_length=5000)):
    fetcher = NewsFetcher()
    plan = fetcher.build_query_plan(text)
    return {
        "queries": plan["queries"],
        "page_size": plan["page_size"],
        "date_from": plan["date_from"],
        "date_to": plan["date_to"],
    }