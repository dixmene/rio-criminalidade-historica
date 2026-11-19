"""
Módulo de Carregamento e Cache de Camadas Geoespaciais (GeoJSON & Parquet).
Compatível com execução direta e em runtime Streamlit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

# Caminhos canônicos
DATA_GEO_DIR = Path("data/geospatial")
DATABASE_DIR = Path("database")

PATH_FACTIONS_GEOJSON = DATA_GEO_DIR / "faccoes_rj_1671_poligonos.geojson"
PATH_AISP_GEOJSON = DATA_GEO_DIR / "aisps_batalhoes_pmerj.geojson"
PATH_AISP_GEOJSON_DB = DATABASE_DIR / "aisps_batalhoes.geojson"
PATH_BAIRROS_GEOJSON = DATA_GEO_DIR / "bairros_rio_166_poligonos.geojson"
PATH_BAIRROS_GEOJSON_DB = DATABASE_DIR / "bairros_rio.geojson"

PATH_AISP_PARQUET = DATA_GEO_DIR / "aisps_batalhoes.parquet"
PATH_BAIRROS_PARQUET = DATA_GEO_DIR / "bairros_rio.parquet"

# Caches em memória validados por (caminho_resolvido, mtime_ns, tamanho)
_MEM_CACHE: Dict[str, Any] = {}
_PARQUET_CACHE: Dict[Tuple[str, int, int], pd.DataFrame] = {}


def _stat_key(path: Path) -> Tuple[str, int, int]:
    st = path.stat()
    return (str(path.resolve()), st.st_mtime_ns, st.st_size)


def _load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {path}: {e}")
        return None


def _load_json_cached(target: Path) -> Optional[Dict[str, Any]]:
    if not target.exists():
        return None
    cache_key = str(_stat_key(target))
    if cache_key not in _MEM_CACHE:
        _MEM_CACHE[cache_key] = _load_json_file(target)
    return _MEM_CACHE[cache_key]


def _load_parquet_cached(target: Path) -> Optional[pd.DataFrame]:
    if not target.exists():
        return None
    cache_key = _stat_key(target)
    cached = _PARQUET_CACHE.get(cache_key)
    if cached is None:
        cached = pd.read_parquet(target, engine="pyarrow")
        _PARQUET_CACHE[cache_key] = cached
    # Shallow copy prevents column mutations from leaking into cache without duplicating buffers
    return cached.copy(deep=False)


def load_faction_polygons(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Carrega os 1.671 polígonos de comunidades e facções armadas."""
    target = Path(path) if path else PATH_FACTIONS_GEOJSON
    return _load_json_cached(target)


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
    return _load_json_cached(target)


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
    return _load_json_cached(target)


def load_aisp_dataframe(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Carrega o arquivo Parquet de AISPs para consultas de alta performance."""
    target = Path(path) if path else PATH_AISP_PARQUET
    if not target.exists():
        target = DATABASE_DIR / "aisps_batalhoes.parquet"
    return _load_parquet_cached(target)


def load_bairros_dataframe(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """Carrega o arquivo Parquet de Bairros para consultas de alta performance."""
    target = Path(path) if path else PATH_BAIRROS_PARQUET
    if not target.exists():
        target = DATABASE_DIR / "bairros_rio.parquet"
    return _load_parquet_cached(target)
