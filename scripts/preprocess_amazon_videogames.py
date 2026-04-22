import os
import re
import ast
import json
import gzip
import hashlib
from pathlib import Path
from typing import Any, List

import numpy as np
import pandas as pd


CONFIG = {
    "raw_dir": "data/raw",
    "output_dir": "data/processed",
    "reviews_file": "Video_Games_5.json.gz",
    "meta_file": "meta_Video_Games.json.gz",
    "min_rating_count": 5,
    "max_games": 1000,
}


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def parse_json_line(line: str) -> dict:
    line = line.strip()
    if not line:
        return {}
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return ast.literal_eval(line)


def read_json_gz(path: str) -> pd.DataFrame:
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            obj = parse_json_line(line)
            if obj:
                rows.append(obj)
    return pd.DataFrame(rows)


def flatten_nested_list(x: Any) -> List[str]:
    out = []

    def _flatten(v):
        if v is None:
            return
        if isinstance(v, (list, tuple, set)):
            for item in v:
                _flatten(item)
        else:
            s = str(v).strip()
            if s:
                out.append(s)

    _flatten(x)
    return out


def clean_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and np.isnan(x):
        return ""
    if isinstance(x, (list, tuple, set)):
        x = " ".join(flatten_nested_list(x))
    text = str(x)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_text(x: Any) -> str:
    text = clean_text(x).lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_price(x: Any) -> float:
    if x is None:
        return np.nan
    if isinstance(x, (int, float)):
        return float(x)
    text = clean_text(x)
    if not text:
        return np.nan
    match = re.search(r"(\d+(\.\d+)?)", text.replace(",", ""))
    if match:
        return float(match.group(1))
    return np.nan


def minmax_scale(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    min_v = s.min()
    max_v = s.max()
    if pd.isna(min_v) or pd.isna(max_v) or max_v == min_v:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - min_v) / (max_v - min_v)


def deterministic_color(text: str) -> str:
    palettes = [
        "#3A506B", "#5BC0BE", "#6C5CE7", "#E17055", "#0984E3",
        "#00B894", "#B56576", "#355C7D", "#2A9D8F", "#8D99AE",
        "#7B2CBF", "#4361EE", "#FB8500", "#2D6A4F", "#6D597A",
    ]
    idx = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % len(palettes)
    return palettes[idx]


def safe_get_related(row: pd.Series, key: str) -> List[str]:
    val = row.get(key, None)

    if val is not None:
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(v) for v in parsed if str(v).strip()]
            except Exception:
                try:
                    parsed = ast.literal_eval(val)
                    if isinstance(parsed, list):
                        return [str(v) for v in parsed if str(v).strip()]
                except Exception:
                    pass
        elif isinstance(val, list):
            return [str(v) for v in flatten_nested_list(val)]
        else:
            try:
                if not (isinstance(val, float) and np.isnan(val)):
                    return [str(v) for v in flatten_nested_list(val)]
            except Exception:
                return [str(v) for v in flatten_nested_list(val)]

    related = row.get("related", None)
    if isinstance(related, str):
        try:
            related = json.loads(related)
        except Exception:
            try:
                related = ast.literal_eval(related)
            except Exception:
                related = None

    if isinstance(related, dict):
        vals = related.get(key, [])
        return [str(v) for v in flatten_nested_list(vals)]

    return []


def build_categories_text(row: pd.Series) -> str:
    pieces = []

    categories_val = row.get("categories", None)
    if categories_val is not None:
        try:
            if not (isinstance(categories_val, float) and np.isnan(categories_val)):
                pieces.extend(flatten_nested_list(categories_val))
        except Exception:
            pieces.extend(flatten_nested_list(categories_val))

    category_val = row.get("category", None)
    if category_val is not None:
        try:
            if not (isinstance(category_val, float) and np.isnan(category_val)):
                pieces.extend(flatten_nested_list(category_val))
        except Exception:
            pieces.extend(flatten_nested_list(category_val))

    main_cat_val = row.get("main_cat", None)
    if main_cat_val is not None:
        try:
            if not (isinstance(main_cat_val, float) and np.isnan(main_cat_val)):
                pieces.append(clean_text(main_cat_val))
        except Exception:
            pieces.append(clean_text(main_cat_val))

    seen = set()
    dedup = []
    for p in pieces:
        p = clean_text(p)
        if p and p not in seen:
            seen.add(p)
            dedup.append(p)

    return " | ".join(dedup)


def clip_display_label(title: str, game_id: str, max_len: int = 28) -> str:
    base = clean_text(title) if clean_text(title) else str(game_id)
    if len(base) <= max_len:
        return base
    return base[: max_len - 3].rstrip() + "..."


def filter_pipe_ids(pipe_text: str, allowed_ids: set) -> str:
    if not pipe_text:
        return ""
    ids = [x.strip() for x in str(pipe_text).split("|") if x.strip()]
    ids = [x for x in ids if x in allowed_ids]
    return "|".join(ids)


def load_raw_data(config: dict):
    raw_dir = config["raw_dir"]
    reviews_path = os.path.join(raw_dir, config["reviews_file"])
    meta_path = os.path.join(raw_dir, config["meta_file"])

    print(f"[1/7] Loading reviews from: {reviews_path}")
    reviews_raw = read_json_gz(reviews_path)
    print(f"       reviews_raw shape = {reviews_raw.shape}")

    print(f"[2/7] Loading metadata from: {meta_path}")
    meta_raw = read_json_gz(meta_path)
    print(f"       meta_raw shape = {meta_raw.shape}")

    return reviews_raw, meta_raw


def build_interactions(reviews_raw: pd.DataFrame) -> pd.DataFrame:
    keep_cols = {
        "reviewerID": "user_id",
        "asin": "game_id",
        "overall": "rating",
        "unixReviewTime": "timestamp",
        "reviewText": "review_text",
        "summary": "summary",
    }

    existing_cols = [c for c in keep_cols.keys() if c in reviews_raw.columns]
    interactions = reviews_raw[existing_cols].copy()
    interactions = interactions.rename(columns=keep_cols)

    for col in ["user_id", "game_id", "rating", "timestamp", "review_text", "summary"]:
        if col not in interactions.columns:
            interactions[col] = np.nan

    interactions["user_id"] = interactions["user_id"].astype(str)
    interactions["game_id"] = interactions["game_id"].astype(str)
    interactions["rating"] = pd.to_numeric(interactions["rating"], errors="coerce")
    interactions["timestamp"] = pd.to_numeric(interactions["timestamp"], errors="coerce").fillna(0).astype(int)
    interactions["review_text"] = interactions["review_text"].fillna("").map(clean_text)
    interactions["summary"] = interactions["summary"].fillna("").map(clean_text)

    interactions = interactions.dropna(subset=["user_id", "game_id", "rating"])
    interactions = interactions[interactions["game_id"].str.len() > 0]

    interactions["interaction_weight"] = (interactions["rating"] / 5.0).clip(0.0, 1.0)
    interactions["interaction_type"] = "rating"

    interactions = interactions[
        [
            "user_id",
            "game_id",
            "rating",
            "timestamp",
            "review_text",
            "summary",
            "interaction_weight",
            "interaction_type",
        ]
    ].reset_index(drop=True)

    return interactions


def build_games(meta_raw: pd.DataFrame, interactions: pd.DataFrame, config: dict) -> pd.DataFrame:
    rating_stats = (
        interactions.groupby("game_id")
        .agg(
            avg_rating=("rating", "mean"),
            rating_count=("rating", "size"),
        )
        .reset_index()
    )

    meta = meta_raw.copy()

    if "asin" not in meta.columns:
        raise ValueError("Metadata file does not contain 'asin' column.")

    meta["game_id"] = meta["asin"].astype(str)

    meta["title"] = meta["title"].map(clean_text) if "title" in meta.columns else ""
    meta["description"] = meta["description"].map(clean_text) if "description" in meta.columns else ""

    if "brand" not in meta.columns:
        meta["brand"] = ""
    meta["brand"] = meta["brand"].map(clean_text)

    if "price" not in meta.columns:
        meta["price"] = np.nan
    meta["price"] = meta["price"].map(parse_price)

    meta["categories_text"] = meta.apply(build_categories_text, axis=1)
    meta["also_view"] = meta.apply(lambda row: "|".join(safe_get_related(row, "also_view")), axis=1)
    meta["also_buy"] = meta.apply(lambda row: "|".join(safe_get_related(row, "also_buy")), axis=1)
    meta["title_clean"] = meta["title"].map(normalize_text)

    meta["description"] = meta["description"].fillna("")
    meta["description"] = np.where(
        meta["description"].str.len() > 0,
        meta["description"],
        meta["categories_text"]
    )

    meta["search_text"] = (
        meta["title"].fillna("") + " " +
        meta["description"].fillna("") + " " +
        meta["categories_text"].fillna("") + " " +
        meta["brand"].fillna("")
    ).map(normalize_text)

    meta["display_label"] = meta.apply(
        lambda row: clip_display_label(row["title"], row["game_id"]),
        axis=1
    )
    meta["ui_color"] = meta["game_id"].map(deterministic_color)

    games = meta.merge(rating_stats, on="game_id", how="left")
    games["avg_rating"] = games["avg_rating"].fillna(0.0)
    games["rating_count"] = games["rating_count"].fillna(0).astype(int)

    games = games[games["title"].fillna("").str.len() > 0].copy()

    min_rating_count = config.get("min_rating_count", 0)
    if min_rating_count is not None and min_rating_count > 0:
        games = games[games["rating_count"] >= min_rating_count].copy()

    count_norm = minmax_scale(np.log1p(games["rating_count"]))
    rating_norm = (games["avg_rating"].clip(1.0, 5.0) - 1.0) / 4.0
    games["popularity_score"] = 0.7 * count_norm + 0.3 * rating_norm

    max_games = config.get("max_games", None)
    if max_games is not None:
        games = games.sort_values(
            ["popularity_score", "rating_count", "avg_rating"],
            ascending=False
        ).head(max_games).copy()

    allowed_ids = set(games["game_id"].astype(str).tolist())
    games["also_view"] = games["also_view"].map(lambda x: filter_pipe_ids(x, allowed_ids))
    games["also_buy"] = games["also_buy"].map(lambda x: filter_pipe_ids(x, allowed_ids))

    games = games[
        [
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
    ].drop_duplicates(subset=["game_id"]).reset_index(drop=True)

    return games


def filter_interactions_by_games(interactions: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    allowed_ids = set(games["game_id"].astype(str).tolist())
    interactions = interactions[interactions["game_id"].isin(allowed_ids)].copy()
    interactions = interactions.reset_index(drop=True)
    return interactions


def create_empty_event_logs() -> pd.DataFrame:
    cols = [
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
    ]
    return pd.DataFrame(columns=cols)


def save_outputs(games: pd.DataFrame, interactions: pd.DataFrame, event_logs: pd.DataFrame, config: dict):
    out_dir = config["output_dir"]
    ensure_dir(out_dir)

    games_path = os.path.join(out_dir, "games.csv")
    interactions_path = os.path.join(out_dir, "interactions.csv")
    event_logs_path = os.path.join(out_dir, "event_logs.csv")

    games.to_csv(games_path, index=False, encoding="utf-8-sig")
    interactions.to_csv(interactions_path, index=False, encoding="utf-8-sig")
    event_logs.to_csv(event_logs_path, index=False, encoding="utf-8-sig")

    print(f"[7/7] Saved:")
    print(f"      - {games_path} ({len(games)} rows)")
    print(f"      - {interactions_path} ({len(interactions)} rows)")
    print(f"      - {event_logs_path} ({len(event_logs)} rows)")


def run_pipeline(config: dict):
    ensure_dir(config["output_dir"])

    reviews_raw, meta_raw = load_raw_data(config)

    interactions = build_interactions(reviews_raw)
    print(f"[3/7] interactions built: {interactions.shape}")

    games = build_games(meta_raw, interactions, config)
    print(f"[4/7] games built: {games.shape}")

    interactions = filter_interactions_by_games(interactions, games)
    print(f"[5/7] interactions filtered by final games: {interactions.shape}")

    event_logs = create_empty_event_logs()
    print(f"[6/7] empty event_logs created: {event_logs.shape}")

    save_outputs(games, interactions, event_logs, config)

    print("\n===== QUICK SUMMARY =====")
    print(f"Unique games: {games['game_id'].nunique()}")
    print(f"Unique users: {interactions['user_id'].nunique()}")
    print(f"Avg rating: {games['avg_rating'].mean():.3f}")
    print(f"Avg rating_count: {games['rating_count'].mean():.3f}")

    print("\nTop 5 games by popularity_score:")
    print(
        games.sort_values("popularity_score", ascending=False)[
            ["game_id", "title", "avg_rating", "rating_count", "popularity_score"]
        ].head(5)
    )


if __name__ == "__main__":
    run_pipeline(CONFIG)