from fastapi import APIRouter

from app.api.routes.games import router as games_router
from app.api.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(games_router)
api_router.include_router(search_router)