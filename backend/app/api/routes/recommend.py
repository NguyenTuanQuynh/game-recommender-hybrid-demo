from fastapi import APIRouter, Query

from app.services.recommend_service import (
    get_home_recommendations,
    get_recently_watched,
)
from app.services.similarity_service import get_similar_games

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get("/home")
def recommend_home_games(
    user_id: str = Query(default="demo_user"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return get_home_recommendations(user_id=user_id, limit=limit, offset=offset)


@router.get("/recent")
def recommend_recent_games(
    user_id: str = Query(default="demo_user"),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    return get_recently_watched(user_id=user_id, limit=limit, offset=offset)


@router.get("/similar/{game_id}")
def recommend_similar_games(
    game_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    return get_similar_games(game_id=game_id, limit=limit, offset=offset)