import re
from typing import List

import pandas as pd

from app.data.loader import load_games_df


SEARCH_RESULT_COLUMNS = [
    "game_id",
    "title",
    "categories_text",
    "avg_rating",
    "rating_count",
    "popularity_score",
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


def _normalize_query(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def search_games(query: str, limit: int = 20, offset: int = 0) -> dict:
    query = _normalize_query(query)

    if not query:
        return {
            "query": query,
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": [],
        }

    query_tokens: List[str] = query.split()

    df = load_games_df().copy()

    # Fill NaN để tránh lỗi contains
    for col in ["title_clean", "description", "categories_text", "search_text"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)

    # Chỉ giữ candidate có chứa ít nhất 1 token trong search_text
    mask = pd.Series(False, index=df.index)
    for token in query_tokens:
        mask = mask | df["search_text"].str.contains(re.escape(token), case=False, na=False)

    candidates = df[mask].copy()

    if candidates.empty:
        return {
            "query": query,
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": [],
        }

    # Score đơn giản, dễ giải thích
    candidates["score"] = 0.0

    for token in query_tokens:
        # match ở title_clean: mạnh nhất
        candidates["score"] += candidates["title_clean"].str.contains(
            re.escape(token), case=False, na=False
        ).astype(float) * 5.0

        # match ở categories_text: trung bình
        candidates["score"] += candidates["categories_text"].str.contains(
            re.escape(token), case=False, na=False
        ).astype(float) * 3.0

        # match ở description: nhẹ hơn
        candidates["score"] += candidates["description"].str.contains(
            re.escape(token), case=False, na=False
        ).astype(float) * 2.0

        # match ở search_text: nền chung
        candidates["score"] += candidates["search_text"].str.contains(
            re.escape(token), case=False, na=False
        ).astype(float) * 1.0

    # Boost nếu match nguyên cụm query ở title
    candidates["score"] += candidates["title_clean"].str.contains(
        re.escape(query), case=False, na=False
    ).astype(float) * 8.0

    # Boost nhẹ theo popularity để kết quả "đẹp" hơn
    candidates["score"] += candidates["popularity_score"].fillna(0) * 2.0

    candidates = candidates.sort_values(
        by=["score", "popularity_score", "rating_count", "avg_rating"],
        ascending=False,
    )

    total = len(candidates)
    page_df = candidates.iloc[offset: offset + limit][SEARCH_RESULT_COLUMNS + ["score"]].copy()

    items = [_clean_record(row) for row in page_df.to_dict(orient="records")]

    return {
        "query": query,
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }