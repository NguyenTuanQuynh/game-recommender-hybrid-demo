from functools import lru_cache
from typing import Dict, List, Set

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.loader import load_games_df


SIMILAR_RESULT_COLUMNS = [
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


def _parse_pipe_ids(value) -> Set[str]:
    if value is None:
        return set()
    if isinstance(value, float) and pd.isna(value):
        return set()

    text = str(value).strip()
    if not text:
        return set()

    return {x.strip() for x in text.split("|") if x.strip()}


@lru_cache(maxsize=1)
def _build_similarity_assets():
    df = load_games_df().copy().reset_index(drop=True)

    if "search_text" not in df.columns:
        df["search_text"] = ""
    df["search_text"] = df["search_text"].fillna("").astype(str)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(df["search_text"])
    cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    game_id_to_index: Dict[str, int] = {
        game_id: idx for idx, game_id in enumerate(df["game_id"].tolist())
    }

    return df, cosine_sim_matrix, game_id_to_index


def get_similar_games(game_id: str, limit: int = 10, offset: int = 0) -> dict:
    df, cosine_sim_matrix, game_id_to_index = _build_similarity_assets()

    if game_id not in game_id_to_index:
        return {
            "source_game_id": game_id,
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": [],
        }

    source_idx = game_id_to_index[game_id]
    source_row = df.iloc[source_idx]

    candidates = df.copy()
    candidates["content_score"] = cosine_sim_matrix[source_idx]

    also_view_ids = _parse_pipe_ids(source_row.get("also_view"))
    also_buy_ids = _parse_pipe_ids(source_row.get("also_buy"))

    candidates["related_score"] = 0.0
    candidates.loc[candidates["game_id"].isin(also_view_ids), "related_score"] += 0.6
    candidates.loc[candidates["game_id"].isin(also_buy_ids), "related_score"] += 1.0

    if "popularity_score" not in candidates.columns:
        candidates["popularity_score"] = 0.0
    candidates["popularity_score"] = candidates["popularity_score"].fillna(0.0)

    candidates["similar_score"] = (
        0.6 * candidates["content_score"]
        + 0.3 * candidates["related_score"]
        + 0.1 * candidates["popularity_score"]
    )

    # bỏ chính nó
    candidates = candidates[candidates["game_id"] != game_id].copy()

    # sort giảm dần
    candidates = candidates.sort_values(
        by=["similar_score", "content_score", "related_score", "popularity_score", "rating_count"],
        ascending=False,
    )

    total = len(candidates)

    page_df = candidates.iloc[offset: offset + limit][
        SIMILAR_RESULT_COLUMNS + ["content_score", "related_score", "similar_score"]
    ].copy()

    items = [_clean_record(row) for row in page_df.to_dict(orient="records")]

    return {
        "source_game_id": game_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }