from functools import lru_cache
from typing import Dict, Set

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.loader import load_event_logs_df, load_games_df


HOME_RESULT_COLUMNS = [
    "game_id",
    "title",
    "categories_text",
    "avg_rating",
    "rating_count",
    "popularity_score",
    "display_label",
    "ui_color",
]


EVENT_WEIGHTS = {
    "click_poster": 1.0,
    "view_detail": 2.0,
    "click_search_result": 2.0,
    "click_similar_item": 1.5,
}


def _clean_record(record: dict) -> dict:
    cleaned = {}
    for key, value in record.items():
        if pd.isna(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


@lru_cache(maxsize=1)
def _build_home_assets():
    df = load_games_df().copy().reset_index(drop=True)

    if "search_text" not in df.columns:
        df["search_text"] = ""
    df["search_text"] = df["search_text"].fillna("").astype(str)

    if "popularity_score" not in df.columns:
        df["popularity_score"] = 0.0
    df["popularity_score"] = df["popularity_score"].fillna(0.0)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(df["search_text"])

    game_id_to_index: Dict[str, int] = {
        game_id: idx for idx, game_id in enumerate(df["game_id"].tolist())
    }

    return df, tfidf_matrix, game_id_to_index


def _get_user_game_events(user_id: str) -> pd.DataFrame:
    events = load_event_logs_df().copy()

    if events.empty:
        return pd.DataFrame()

    events = events[events["user_id"] == user_id].copy()

    if events.empty:
        return pd.DataFrame()

    if "game_id" not in events.columns:
        return pd.DataFrame()

    events = events[events["game_id"].notna()].copy()
    events["game_id"] = events["game_id"].astype(str).str.strip()
    events = events[events["game_id"] != ""].copy()

    if events.empty:
        return pd.DataFrame()

    events = events[events["event_type"].isin(EVENT_WEIGHTS.keys())].copy()

    if events.empty:
        return pd.DataFrame()

    events["base_weight"] = events["event_type"].map(EVENT_WEIGHTS).fillna(0.0)

    if "event_value" in events.columns:
        events["event_value"] = pd.to_numeric(events["event_value"], errors="coerce").fillna(1.0)
    else:
        events["event_value"] = 1.0

    # final weight = base_weight * event_value
    events["final_weight"] = events["base_weight"] * events["event_value"]

    return events


def _popular_fallback(df: pd.DataFrame, limit: int, offset: int, user_id: str) -> dict:
    ranked = df.sort_values(
        by=["popularity_score", "rating_count", "avg_rating"],
        ascending=False,
    ).copy()

    total = len(ranked)
    page_df = ranked.iloc[offset: offset + limit][HOME_RESULT_COLUMNS].copy()
    page_df["profile_score"] = 0.0
    page_df["home_score"] = page_df["popularity_score"]

    items = [_clean_record(row) for row in page_df.to_dict(orient="records")]

    return {
        "user_id": user_id,
        "strategy": "popular_fallback",
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def get_home_recommendations(user_id: str = "demo_user", limit: int = 20, offset: int = 0) -> dict:
    df, tfidf_matrix, game_id_to_index = _build_home_assets()

    user_events = _get_user_game_events(user_id=user_id)

    if user_events.empty:
        return _popular_fallback(df=df, limit=limit, offset=offset, user_id=user_id)

    # chỉ giữ các game_id thực sự tồn tại trong games.csv
    user_events = user_events[user_events["game_id"].isin(game_id_to_index.keys())].copy()

    if user_events.empty:
        return _popular_fallback(df=df, limit=limit, offset=offset, user_id=user_id)

    # gộp trọng số theo game
    user_game_weights = (
        user_events.groupby("game_id", as_index=False)["final_weight"]
        .sum()
        .sort_values("final_weight", ascending=False)
    )

    interacted_game_ids: Set[str] = set(user_game_weights["game_id"].tolist())

    # tạo user profile vector = weighted sum các vector game đã tương tác
    weighted_vector = None
    total_weight = 0.0

    for _, row in user_game_weights.iterrows():
        gid = row["game_id"]
        weight = float(row["final_weight"])

        idx = game_id_to_index[gid]
        vec = tfidf_matrix[idx]

        if weighted_vector is None:
            weighted_vector = vec * weight
        else:
            weighted_vector = weighted_vector + (vec * weight)

        total_weight += weight

    if weighted_vector is None or total_weight == 0:
        return _popular_fallback(df=df, limit=limit, offset=offset, user_id=user_id)

    user_profile_vector = weighted_vector / total_weight

    profile_scores = cosine_similarity(user_profile_vector, tfidf_matrix).flatten()

    candidates = df.copy()
    candidates["profile_score"] = profile_scores
    candidates["home_score"] = (
        0.8 * candidates["profile_score"]
        + 0.2 * candidates["popularity_score"]
    )

    # loại game user đã tương tác rồi
    candidates = candidates[~candidates["game_id"].isin(interacted_game_ids)].copy()

    if candidates.empty:
        return _popular_fallback(df=df, limit=limit, offset=offset, user_id=user_id)

    candidates = candidates.sort_values(
        by=["home_score", "profile_score", "popularity_score", "rating_count"],
        ascending=False,
    )

    total = len(candidates)
    page_df = candidates.iloc[offset: offset + limit][
        HOME_RESULT_COLUMNS + ["profile_score", "home_score"]
    ].copy()

    items = [_clean_record(row) for row in page_df.to_dict(orient="records")]

    return {
        "user_id": user_id,
        "strategy": "personalized_home",
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }