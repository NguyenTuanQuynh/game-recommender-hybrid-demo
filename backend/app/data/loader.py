from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.core.paths import (
    GAMES_CSV_PATH,
    INTERACTIONS_CSV_PATH,
    EVENT_LOGS_CSV_PATH,
)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_games_df() -> pd.DataFrame:
    return _read_csv(GAMES_CSV_PATH)


@lru_cache(maxsize=1)
def load_interactions_df() -> pd.DataFrame:
    return _read_csv(INTERACTIONS_CSV_PATH)


@lru_cache(maxsize=1)
def load_event_logs_df() -> pd.DataFrame:
    if not EVENT_LOGS_CSV_PATH.exists():
        return pd.DataFrame(columns=[
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
    return _read_csv(EVENT_LOGS_CSV_PATH)


def clear_cache() -> None:
    load_games_df.cache_clear()
    load_interactions_df.cache_clear()
    load_event_logs_df.cache_clear()