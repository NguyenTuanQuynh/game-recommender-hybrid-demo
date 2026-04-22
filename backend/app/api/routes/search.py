from fastapi import APIRouter, Query

from app.services.search_service import search_games

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return search_games(query=q, limit=limit, offset=offset)