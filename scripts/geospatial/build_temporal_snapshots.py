# -*- coding: utf-8 -*-
"""
Gerador de Snapshots Espaço-Temporais Pré-computados (FASE 2)
============================================================

Gera snapshots GeoJSON anuais pré-computados (1958–2026) para permitir
scrubbing temporal a 60 FPS no frontend sem sobrecarregar o banco de dados.
Cada snapshot acompanha metadados e hash SHA-256 compilados em manifest.json.
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Adiciona raiz ao path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.services.atlas_service import AtlasService


def generate_snapshots(start_year: int = 1958, end_year: int = 2026, output_dir: Optional[Path] = None):
    if output_dir is None:
        output_dir = _ROOT / "data" / "exports" / "snapshots"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Iniciando Geração de Snapshots Espaço-Temporais ({start_year} - {end_year}) ===")
    atlas = AtlasService()
    manifest_entries = {}
    total_features_all = 0

    for year in range(start_year, end_year + 1):
        ws = atlas.get_world_state(year=year, include_anachronistic=True, is_demo=False)
        geojson_data = ws.to_geojson()
        
        file_name = f"snapshot_{year}.geojson"
        file_path = output_dir / file_name

        json_bytes = json.dumps(geojson_data, ensure_ascii=False, indent=2).encode("utf-8")
        file_hash = hashlib.sha256(json_bytes).hexdigest()

        with open(file_path, "wb") as f:
            f.write(json_bytes)

        feat_count = len(geojson_data["features"])
        total_features_all += feat_count

        manifest_entries[str(year)] = {
            "year": year,
            "filename": file_name,
            "sha256": file_hash,
            "size_bytes": len(json_bytes),
            "total_features": feat_count,
            "territories_count": len(ws.territories),
            "facilities_count": len(ws.facilities),
            "events_count": len(ws.events),
            "flows_count": len(ws.flows),
            "evidence_density_index": ws.coverage.get("evidence_density_index", 0.0),
            "coverage_status": ws.coverage.get("coverage_status", "lacunar")
        }

        if year % 10 == 0 or year == start_year or year == end_year:
            print(f"  [{year}] Gerado: {feat_count} features | SHA256: {file_hash[:12]}...")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "year_range": [start_year, end_year],
        "total_years": (end_year - start_year + 1),
        "total_features_across_timeline": total_features_all,
        "format": "GeoJSON FeatureCollection (RFC 7946)",
        "crs": "EPSG:4326",
        "snapshots": manifest_entries
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCESSO] {len(manifest_entries)} snapshots gerados com sucesso em '{output_dir}'!")
    print(f"  - Manifest gerado: {manifest_path}")
    return manifest


if __name__ == "__main__":
    from typing import Optional
    generate_snapshots()
