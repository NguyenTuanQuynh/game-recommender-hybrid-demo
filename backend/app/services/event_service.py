from __future__ import annotations

from datetime import datetime
from pathlib import Path
import uuid

import pandas as pd

from app.core.paths import EVENT_LOGS_CSV_PATH
from app.data.loader import clear_cache


ALLOWED_EVENT_TYPES = {
    "view_home",
    "search",
    "click_poster",
    "view_detail",
    "click_search_result",
    "click_similar_item",
}


def _ensure_event_logs_file() -> None:
    EVENT_LOGS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not EVENT_LOGS_CSV_PATH.exists():
        df = pd.DataFrame(columns=[
            "event_id",
            "user_id",
            "game_id",
            "event_type",
            "event_value",
            "query",
            "source",
            "timestamp",
            "session_id",
            "metadata",
        ])
        df.to_csv(EVENT_LOGS_CSV_PATH, index=False, encoding="utf-8-sig")


def log_event(
    user_id: str,
    event_type: str,
    game_id: str | None = None,
    event_value: float = 1.0,
    query: str | None = None,
    source: str | None = None,
    session_id: str | None = None,
    metadata: str | None = None,
) -> dict:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(
            f"Invalid event_type '{event_type}'. Allowed: {sorted(ALLOWED_EVENT_TYPES)}"
        )

    _ensure_event_logs_file()

    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "user_id": user_id.strip() if user_id else "demo_user",
        "game_id": game_id if game_id else None,
        "event_type": event_type,
        "event_value": float(event_value),
        "query": query if query else None,
        "source": source if source else None,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id if session_id else "demo_session",
        "metadata": metadata if metadata else "{}",
    }

    row_df = pd.DataFrame([event])
    row_df.to_csv(
        EVENT_LOGS_CSV_PATH,
        mode="a",
        header=False,
        index=False,
        encoding="utf-8-sig",
    )

    clear_cache()

    return event