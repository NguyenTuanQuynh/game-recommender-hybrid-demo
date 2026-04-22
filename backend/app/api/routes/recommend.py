from fastapi import APIRouter, Query

from app.services.similarity_service import get_similar_games

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get("/similar/{game_id}")
def recommend_similar_games(
    game_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    return get_similar_games(game_id=game_id, limit=limit, offset=offset)