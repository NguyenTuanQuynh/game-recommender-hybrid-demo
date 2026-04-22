import pandas as pd

from app.data.loader import load_games_df


GAME_LIST_COLUMNS = [
    "game_id",
    "title",
    "categories_text",
    "avg_rating",
    "rating_count",
    "popularity_score",
    "display_label",
    "ui_color",
]

GAME_DETAIL_COLUMNS = [
    "game_id",
    "title",
    "title_clean",
    "description",
    "categories_text",
    "brand",
    "price",
    "avg_rating",
    "rating_count",
    "popularity_score",
    "also_view",
    "also_buy",
    "search_text",
    "display_label",
    "ui_color",
]


def _clean_record(record: dict) -> dict:
    cleaned = {}
    for key, value in record.items():
        if pd.isna(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


def list_games(limit: int = 20, offset: int = 0) -> dict:
    df = load_games_df().copy()
    total = len(df)

    page_df = df.iloc[offset: offset + limit][GAME_LIST_COLUMNS].copy()
    items = [_clean_record(row) for row in page_df.to_dict(orient="records")]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def get_game_by_id(game_id: str) -> dict | None:
    df = load_games_df()
    match = df[df["game_id"] == game_id]

    if match.empty:
        return None

    record = match.iloc[0][GAME_DETAIL_COLUMNS].to_dict()
    return _clean_record(record)