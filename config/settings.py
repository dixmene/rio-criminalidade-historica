import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Projeto
    APP_NAME: str = os.getenv("APP_NAME", "Mapa Histórico e Territorial da Criminalidade no RJ")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Diretórios de Dados
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_STAGING_DIR: Path = BASE_DIR / "data" / "staging"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    DATA_GEOSPATIAL_DIR: Path = BASE_DIR / "data" / "geospatial"
    DATA_EXPORTS_DIR: Path = BASE_DIR / "data" / "exports"

    # Banco de Dados
    # Se não configurado PostgreSQL, utiliza SQLite local em data/
    DEFAULT_SQLITE_PATH = BASE_DIR / "data" / "rio_historico.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

    # Configurações Cartográficas (Rio de Janeiro)
    MAP_DEFAULT_LAT: float = float(os.getenv("MAP_DEFAULT_LAT", "-22.9068"))
    MAP_DEFAULT_LON: float = float(os.getenv("MAP_DEFAULT_LON", "-43.1729"))
    MAP_DEFAULT_ZOOM: int = int(os.getenv("MAP_DEFAULT_ZOOM", "11"))

settings = Settings()
