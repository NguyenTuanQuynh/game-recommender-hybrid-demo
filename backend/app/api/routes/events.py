from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.event_service import log_event


router = APIRouter(prefix="/events", tags=["events"])


class EventLogRequest(BaseModel):
    user_id: str = Field(default="demo_user")
    event_type: str
    game_id: str | None = None
    event_value: float = 1.0
    query: str | None = None
    source: str | None = None
    session_id: str | None = "demo_session"
    metadata: str | None = "{}"


@router.post("/log")
def create_event_log(payload: EventLogRequest):
    event = log_event(
        user_id=payload.user_id,
        event_type=payload.event_type,
        game_id=payload.game_id,
        event_value=payload.event_value,
        query=payload.query,
        source=payload.source,
        session_id=payload.session_id,
        metadata=payload.metadata,
    )
    return {
        "message": "Event logged successfully",
        "event": event,
    }