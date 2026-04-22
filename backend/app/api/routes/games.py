from fastapi import APIRouter, HTTPException, Query

from app.data.repository import get_game_by_id, list_games

router = APIRouter(prefix="/games", tags=["games"])


@router.get("")
def read_games(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return list_games(limit=limit, offset=offset)


@router.get("/{game_id}")
def read_game_detail(game_id: str):
    game = get_game_by_id(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game