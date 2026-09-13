import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Database Configuration: Defaults to SQLite in workspace if not specified
DEFAULT_SQLITE_PATH = BASE_DIR / "data" / "rio_historico.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

APP_NAME = os.getenv("APP_NAME", "Daniel Systems - MVP")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEFAULT_MAP_CENTER = (-22.9068, -43.1729)  # Rio de Janeiro
DEFAULT_MAP_ZOOM = 11
