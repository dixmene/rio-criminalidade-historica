"""
Módulo de Carregamento e Cache de Camadas Geoespaciais (GeoJSON & Parquet).
Compatível com execução direta e em runtime Streamlit.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_GEO_DIR = Path("data/geospatial") if Path("data/geospatial").exists() else PROJECT_ROOT / "data" / "geospatial"
DATABASE_DIR = Path("database") if Path("database").exists() else PROJECT_ROOT / "database"

PATH_FACTIONS_GEOJSON = DATA_GEO_DIR / "faccoes_rj_1671_poligonos.geojson"
PATH_AISP_GEOJSON = DATA_GEO_DIR / "aisps_batalhoes_pmerj.geojson"
PATH_AISP_GEOJSON_DB = DATABASE_DIR / "aisps_batalhoes.geojson"
PATH_BAIRROS_GEOJSON = DATA_GEO_DIR / "bairros_rio_166_poligonos.geojson"
PATH_BAIRROS_GEOJSON_DB = DATABASE_DIR / "bairros_rio.geojson"

PATH_AISP_PARQUET = DATA_GEO_DIR / "aisps_batalhoes.parquet"
PATH_BAIRROS_PARQUET = DATA_GEO_DIR / "bairros_rio.parquet"

# Caches em memória simples para execução fora do Streamlit
_MEM_CACHE: Dict[str, Any] = {}


def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {path}: {e}")
        return None


def load_faction_polygons(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Carrega os 1.671 polígonos de comunidades e facções armadas."""
    target = Path(path) if path else PATH_FACTIONS_GEOJSON
    key = str(target)
    if key not in _MEM_CACHE:
        _MEM_CACHE[key] = _load_json_file(target)
    return _MEM_CACHE[key]


def load_aisp_polygons(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Carrega a malha vetorial oficial de AISP / Batalhões da PMERJ."""
    if path:
        target = Path(path)
    elif PATH_AISP_GEOJSON.exists():
        target = PATH_AISP_GEOJSON
    elif PATH_AISP_GEOJSON_DB.exists():
        target = PATH_AISP_GEOJSON_DB
    else:
        return None

    key = str(target)
    if key not in _MEM_CACHE:
        _MEM_CACHE[key] = _load_json_file(target)
    return _MEM_CACHE[key]


def load_bairros_polygons(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Carrega a malha vetorial oficial de Bairros da Prefeitura do Rio (IPP / Data.Rio)."""
    if path:
        target = Path(path)
    elif PATH_BAIRROS_GEOJSON.exists():
        target = PATH_BAIRROS_GEOJSON
    elif PATH_BAIRROS_GEOJSON_DB.exists():
        target = PATH_BAIRROS_GEOJSON_DB
    else:
        return None

    key = str(target)
    if key not in _MEM_CACHE:
        _MEM_CACHE[key] = _load_json_file(target)
    return _MEM_CACHE[key]


def load_aisp_dataframe(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Carrega o arquivo Parquet de AISPs para consultas de alta performance."""
    target = Path(path) if path else PATH_AISP_PARQUET
    if not target.exists():
        target = DATABASE_DIR / "aisps_batalhoes.parquet"
    if not target.exists():
        return None
    return pd.read_parquet(target, engine="pyarrow")


def load_bairros_dataframe(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Carrega o arquivo Parquet de Bairros para consultas de alta performance."""
    target = Path(path) if path else PATH_BAIRROS_PARQUET
    if not target.exists():
        target = DATABASE_DIR / "bairros_rio.parquet"
    if not target.exists():
        return None
    return pd.read_parquet(target, engine="pyarrow")
