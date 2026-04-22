from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.paths import PROCESSED_DIR

app = FastAPI(
    title="Hybrid Game Recommender API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Backend is running",
        "processed_data_dir": str(PROCESSED_DIR),
    }


@app.get("/health")
def health():
    return {"status": "ok"}