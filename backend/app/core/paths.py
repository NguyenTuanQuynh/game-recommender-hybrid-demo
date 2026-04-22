from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

GAMES_CSV_PATH = PROCESSED_DIR / "games.csv"
INTERACTIONS_CSV_PATH = PROCESSED_DIR / "interactions.csv"
EVENT_LOGS_CSV_PATH = PROCESSED_DIR / "event_logs.csv"