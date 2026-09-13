"""
Módulo de Extração e Estruturação de Polígonos Territoriais (RJ)
Fonte Primária: dadosderiscos.com.br/mapa-rj-risco-faccoes.html
Compilação: 1.671 áreas mapeadas com polígonos vetoriais e classificação faccional.
"""

import os
import json
import hashlib
import urllib.request
from datetime import datetime
from pathlib import Path


SOURCE_URL = "https://dadosderiscos.com.br/mapa-rj-risco-faccoes.html"
OUTPUT_DIR = Path("data/geospatial")
OUTPUT_GEOJSON = OUTPUT_DIR / "faccoes_rj_1671_poligonos.geojson"
OUTPUT_META = OUTPUT_DIR / "faccoes_rj_1671_meta.json"

FACTION_NAMES = {
    "CV": "Comando Vermelho",
    "TCP": "Terceiro Comando Puro",
    "ADA": "Amigos dos Amigos",
    "MIL": "Milícia (Geral)",
    "LJ": "Liga da Justiça (CL220)",
    "MNI": "Milícia de Nova Iguaçu",
    "NEU": "Área Neutra / Disputada"
}

FACTION_COLORS = {
    "CV": "#E0342C",
    "TCP": "#2FA46B",
    "ADA": "#EDB72B",
    "MIL": "#4E9DE0",
    "LJ": "#2B5BC7",
    "MNI": "#9B6BD6",
    "NEU": "#8C97A3"
}


def compute_sha256(content_bytes: bytes) -> str:
    h = hashlib.sha256()
    h.update(content_bytes)
    return h.hexdigest()


def compute_polygon_centroid(coordinates) -> tuple[float, float]:
    """Calcula o centroide aproximado (lat, lon) de um anel poligonal simples."""
    try:
        ring = coordinates[0]
        if not ring:
            return None, None
        lons = [pt[0] for pt in ring]
        lats = [pt[1] for pt in ring]
        return sum(lats) / len(lats), sum(lons) / len(lons)
    except Exception:
        return None, None


def extract_and_save():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Baixando dados de {SOURCE_URL}...")
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp:
        raw_html = resp.read()

    html_str = raw_html.decode("utf-8", errors="ignore")
    raw_hash = compute_sha256(raw_html)

    # Localizar script#zonas
    marker_start = '<script id="zonas" type="application/json">'
    start_idx = html_str.find(marker_start)
    if start_idx == -1:
        raise ValueError("Script id='zonas' não localizado no HTML baixado.")

    start_idx += len(marker_start)
    end_idx = html_str.find("</script>", start_idx)
    if end_idx == -1:
        raise ValueError("Fim da tag </script> de 'zonas' não localizado.")

    json_str = html_str[start_idx:end_idx].strip()
    geojson_data = json.loads(json_str)

    features = geojson_data.get("features", [])
    print(f"Features GeoJSON brutas encontradas: {len(features)}")

    enriched_features = []
    faction_counts = {}

    for idx, feat in enumerate(features):
        props = feat.get("properties", {})
        code = props.get("f", "NEU")
        name = props.get("n", f"Área {idx+1}")
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])

        c_lat, c_lon = compute_polygon_centroid(coords)

        enriched_props = {
            "id": idx + 1,
            "nome": name,
            "faccao_sigla": code,
            "faccao_nome": FACTION_NAMES.get(code, code),
            "cor_hex": FACTION_COLORS.get(code, "#8C97A3"),
            "centroide_lat": round(c_lat, 6) if c_lat is not None else None,
            "centroide_lon": round(c_lon, 6) if c_lon is not None else None,
            "fonte_origem": "dadosderiscos.com.br"
        }

        enriched_features.append({
            "type": "Feature",
            "properties": enriched_props,
            "geometry": geom
        })

        faction_counts[code] = faction_counts.get(code, 0) + 1

    clean_geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "titulo": "Mapeamento Territorial de Facções e Grupos Armados - Rio de Janeiro",
            "total_areas": len(enriched_features),
            "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url_fonte": SOURCE_URL,
            "faccoes_resumo": faction_counts
        },
        "features": enriched_features
    }

    geojson_bytes = json.dumps(clean_geojson, ensure_ascii=False, indent=2).encode("utf-8")
    with open(OUTPUT_GEOJSON, "wb") as f:
        f.write(geojson_bytes)

    geojson_hash = compute_sha256(geojson_bytes)

    # Metadados Sidecar (Padrão de auditoria e custódia digital do projeto)
    metadata = {
        "arquivo": str(OUTPUT_GEOJSON.name),
        "formato": "GeoJSON (RFC 7946)",
        "total_poligonos": len(enriched_features),
        "sha256_geojson": geojson_hash,
        "sha256_html_original": raw_hash,
        "tamanho_bytes": len(geojson_bytes),
        "data_extracao": datetime.now().isoformat(),
        "url_origem": SOURCE_URL,
        "distribuicao_faccoes": {
            f"{k} ({FACTION_NAMES.get(k, k)})": count for k, count in sorted(faction_counts.items(), key=lambda x: -x[1])
        },
        "resumo_metodologico": (
            "Compilação de 1.671 polígonos de favelas e comunidades com presença registrada "
            "de facções do tráfico e milícias no Estado do Rio de Janeiro. Extraído do projeto "
            "aberto dadosderiscos.com.br para análise cartográfica complementar ao acervo histórico."
        )
    }

    with open(OUTPUT_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Salvo com sucesso em {OUTPUT_GEOJSON} ({len(geojson_bytes)} bytes)")
    print(f"Metadados de custódia salvos em {OUTPUT_META}")
    print("Distribuição das facções:", faction_counts)


if __name__ == "__main__":
    extract_and_save()
