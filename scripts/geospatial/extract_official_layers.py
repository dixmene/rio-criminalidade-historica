"""
Módulo de Extração e Estruturação de Camadas Geográficas Oficiais do Rio de Janeiro:
1. Limites de Bairros do Município do Rio de Janeiro (Prefeitura da Cidade do Rio de Janeiro / IPP / Data.Rio)
2. Limites de AISP (Áreas Integradas de Segurança Pública / Batalhões da PMERJ - ISP-RJ)
Gera arquivos GeoJSON, Parquet e Metadados Sidecar com hash SHA-256 para estrita auditoria.
"""

import os
import json
import hashlib
import urllib.request
from datetime import datetime
from pathlib import Path
import pandas as pd

# Mapeamento Oficial Batalhões PMERJ por AISP
AISP_METADATA = {
    2: {"batalhao": "2º BPM", "sede": "Botafogo", "nome_completo": "2º Batalhão de Polícia Militar (Zona Sul)", "risp": 1, "municipio": "Rio de Janeiro"},
    3: {"batalhao": "3º BPM", "sede": "Méier", "nome_completo": "3º Batalhão de Polícia Militar (Méier/Grande Méier)", "risp": 1, "municipio": "Rio de Janeiro"},
    4: {"batalhao": "4º BPM", "sede": "São Cristóvão", "nome_completo": "4º Batalhão de Polícia Militar (São Cristóvão/Centro)", "risp": 1, "municipio": "Rio de Janeiro"},
    5: {"batalhao": "5º BPM", "sede": "Harmonia/Centro", "nome_completo": "5º Batalhão de Polícia Militar (Centro/Porto)", "risp": 1, "municipio": "Rio de Janeiro"},
    6: {"batalhao": "6º BPM", "sede": "Tijuca", "nome_completo": "6º Batalhão de Polícia Militar (Grande Tijuca)", "risp": 1, "municipio": "Rio de Janeiro"},
    7: {"batalhao": "7º BPM", "sede": "Alcântara", "nome_completo": "7º Batalhão de Polícia Militar (São Gonçalo)", "risp": 4, "municipio": "São Gonçalo"},
    8: {"batalhao": "8º BPM", "sede": "Campos", "nome_completo": "8º Batalhão de Polícia Militar (Campos dos Goytacazes)", "risp": 6, "municipio": "Campos dos Goytacazes"},
    9: {"batalhao": "9º BPM", "sede": "Rocha Miranda", "nome_completo": "9º Batalhão de Polícia Militar (Rocha Miranda/Madureira)", "risp": 2, "municipio": "Rio de Janeiro"},
    10: {"batalhao": "10º BPM", "sede": "Barra do Piraí", "nome_completo": "10º Batalhão de Polícia Militar (Barra do Piraí)", "risp": 5, "municipio": "Barra do Piraí"},
    11: {"batalhao": "11º BPM", "sede": "Nova Friburgo", "nome_completo": "11º Batalhão de Polícia Militar (Região Serrana Leste)", "risp": 7, "municipio": "Nova Friburgo"},
    12: {"batalhao": "12º BPM", "sede": "Niterói", "nome_completo": "12º Batalhão de Polícia Militar (Niterói/Maricá)", "risp": 4, "municipio": "Niterói"},
    14: {"batalhao": "14º BPM", "sede": "Bangu", "nome_completo": "14º Batalhão de Polícia Militar (Bangu/Realengo)", "risp": 2, "municipio": "Rio de Janeiro"},
    15: {"batalhao": "15º BPM", "sede": "Duque de Caxias", "nome_completo": "15º Batalhão de Polícia Militar (Duque de Caxias)", "risp": 3, "municipio": "Duque de Caxias"},
    16: {"batalhao": "16º BPM", "sede": "Olaria", "nome_completo": "16º Batalhão de Polícia Militar (Olaria/Penha)", "risp": 2, "municipio": "Rio de Janeiro"},
    17: {"batalhao": "17º BPM", "sede": "Ilha do Governador", "nome_completo": "17º Batalhão de Polícia Militar (Ilha do Governador/Fundão)", "risp": 1, "municipio": "Rio de Janeiro"},
    18: {"batalhao": "18º BPM", "sede": "Jacarepaguá", "nome_completo": "18º Batalhão de Polícia Militar (Jacarepaguá)", "risp": 2, "municipio": "Rio de Janeiro"},
    19: {"batalhao": "19º BPM", "sede": "Copacabana", "nome_completo": "19º Batalhão de Polícia Militar (Copacabana/Leme)", "risp": 1, "municipio": "Rio de Janeiro"},
    20: {"batalhao": "20º BPM", "sede": "Mesquita", "nome_completo": "20º Batalhão de Polícia Militar (Mesquita/Nova Iguaçu)", "risp": 3, "municipio": "Mesquita"},
    21: {"batalhao": "21º BPM", "sede": "São João de Meriti", "nome_completo": "21º Batalhão de Polícia Militar (São João de Meriti)", "risp": 3, "municipio": "São João de Meriti"},
    22: {"batalhao": "22º BPM", "sede": "Maré", "nome_completo": "22º Batalhão de Polícia Militar (Maré/Bonsucesso)", "risp": 1, "municipio": "Rio de Janeiro"},
    23: {"batalhao": "23º BPM", "sede": "Leblon", "nome_completo": "23º Batalhão de Polícia Militar (Leblon/Gávea/São Conrado)", "risp": 1, "municipio": "Rio de Janeiro"},
    24: {"batalhao": "24º BPM", "sede": "Queimados", "nome_completo": "24º Batalhão de Polícia Militar (Queimados/Baixada)", "risp": 3, "municipio": "Queimados"},
    25: {"batalhao": "25º BPM", "sede": "Cabo Frio", "nome_completo": "25º Batalhão de Polícia Militar (Região dos Lagos)", "risp": 4, "municipio": "Cabo Frio"},
    26: {"batalhao": "26º BPM", "sede": "Petrópolis", "nome_completo": "26º Batalhão de Polícia Militar (Petrópolis)", "risp": 7, "municipio": "Petrópolis"},
    27: {"batalhao": "27º BPM", "sede": "Santa Cruz", "nome_completo": "27º Batalhão de Polícia Militar (Santa Cruz/Paciência)", "risp": 2, "municipio": "Rio de Janeiro"},
    28: {"batalhao": "28º BPM", "sede": "Volta Redonda", "nome_completo": "28º Batalhão de Polícia Militar (Volta Redonda/Sul Fluminense)", "risp": 5, "municipio": "Volta Redonda"},
    29: {"batalhao": "29º BPM", "sede": "Itaperuna", "nome_completo": "29º Batalhão de Polícia Militar (Noroeste Fluminense)", "risp": 6, "municipio": "Itaperuna"},
    30: {"batalhao": "30º BPM", "sede": "Teresópolis", "nome_completo": "30º Batalhão de Polícia Militar (Teresópolis)", "risp": 7, "municipio": "Teresópolis"},
    31: {"batalhao": "31º BPM", "sede": "Barra da Tijuca", "nome_completo": "31º Batalhão de Polícia Militar (Barra/Recreio)", "risp": 2, "municipio": "Rio de Janeiro"},
    32: {"batalhao": "32º BPM", "sede": "Macaé", "nome_completo": "32º Batalhão de Polícia Militar (Macaé/Norte Fluminense)", "risp": 6, "municipio": "Macaé"},
    33: {"batalhao": "33º BPM", "sede": "Angra dos Reis", "nome_completo": "33º Batalhão de Polícia Militar (Costa Verde)", "risp": 5, "municipio": "Angra dos Reis"},
    34: {"batalhao": "34º BPM", "sede": "Magé", "nome_completo": "34º Batalhão de Polícia Militar (Magé)", "risp": 3, "municipio": "Magé"},
    35: {"batalhao": "35º BPM", "sede": "Itaboraí", "nome_completo": "35º Batalhão de Polícia Militar (Itaboraí)", "risp": 4, "municipio": "Itaboraí"},
    36: {"batalhao": "36º BPM", "sede": "Santo Antônio de Pádua", "nome_completo": "36º Batalhão de Polícia Militar (Noroeste)", "risp": 6, "municipio": "Santo Antônio de Pádua"},
    37: {"batalhao": "37º BPM", "sede": "Resende", "nome_completo": "37º Batalhão de Polícia Militar (Resende/Agulhas Negras)", "risp": 5, "municipio": "Resende"},
    38: {"batalhao": "38º BPM", "sede": "Três Rios", "nome_completo": "38º Batalhão de Polícia Militar (Centro-Sul Fluminense)", "risp": 5, "municipio": "Três Rios"},
    39: {"batalhao": "39º BPM", "sede": "Belford Roxo", "nome_completo": "39º Batalhão de Polícia Militar (Belford Roxo)", "risp": 3, "municipio": "Belford Roxo"},
    40: {"batalhao": "40º BPM", "sede": "Campo Grande", "nome_completo": "40º Batalhão de Polícia Militar (Campo Grande)", "risp": 2, "municipio": "Rio de Janeiro"},
    41: {"batalhao": "41º BPM", "sede": "Irajá", "nome_completo": "41º Batalhão de Polícia Militar (Irajá/Pavuna/Costa Barros)", "risp": 2, "municipio": "Rio de Janeiro"},
}

URL_BAIRROS = "https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Cartografia/Limites_administrativos/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
URL_AISP = "https://services.arcgis.com/qFQYQQeTXZSPY7Fs/arcgis/rest/services/Limite_AISP/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"

DATA_GEO_DIR = Path("data/geospatial")
DATABASE_DIR = Path("database")


def compute_sha256(content_bytes: bytes) -> str:
    h = hashlib.sha256()
    h.update(content_bytes)
    return h.hexdigest()


def compute_centroid(geometry) -> tuple[float, float]:
    """Calcula centroide aproximado (lat, lon) de polígono ou multipolígono GeoJSON."""
    try:
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates", [])
        lats, lons = [], []

        def extract_points(pt_list):
            if not pt_list:
                return
            if isinstance(pt_list[0], (float, int)):
                lons.append(pt_list[0])
                lats.append(pt_list[1])
            else:
                for sub in pt_list:
                    extract_points(sub)

        extract_points(coords)
        if lats and lons:
            return round(sum(lats) / len(lats), 6), round(sum(lons) / len(lons), 6)
    except Exception:
        pass
    return None, None


def fetch_and_process_bairros():
    print(f"Baixando malha oficial de Bairros de {URL_BAIRROS}...")
    req = urllib.request.Request(URL_BAIRROS, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()

    data = json.loads(raw_bytes.decode("utf-8"))
    raw_features = data.get("features", [])
    print(f"Bairros brutos recebidos: {len(raw_features)}")

    enriched_features = []
    parquet_rows = []

    for idx, feat in enumerate(raw_features):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        c_lat, c_lon = compute_centroid(geom)

        nome = str(props.get("nome", "")).strip()
        regiao_adm = str(props.get("regiao_adm", "")).strip()
        area_plane = str(props.get("area_plane", "")).strip()
        codbairro = str(props.get("codbairro", "")).strip()
        rp = str(props.get("rp", "")).strip()

        clean_props = {
            "id": idx + 1,
            "nome": nome,
            "regiao_adm": regiao_adm,
            "area_planejamento": area_plane,
            "cod_bairro": codbairro,
            "regiao_planejamento": rp,
            "centroide_lat": c_lat,
            "centroide_lon": c_lon,
            "fonte_oficial": "PCRJ / IPP / Data.Rio (Cartografia Limites Administrativos)",
            "camada": "Bairros Oficiais PCRJ"
        }

        enriched_features.append({
            "type": "Feature",
            "properties": clean_props,
            "geometry": geom
        })

        parquet_rows.append({
            "id": idx + 1,
            "nome": nome,
            "regiao_adm": regiao_adm,
            "area_planejamento": area_plane,
            "cod_bairro": codbairro,
            "regiao_planejamento": rp,
            "centroide_lat": c_lat,
            "centroide_lon": c_lon,
            "geometry_json": json.dumps(geom)
        })

    clean_geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "titulo": "Limites Oficiais dos Bairros do Município do Rio de Janeiro",
            "total_bairros": len(enriched_features),
            "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": "Prefeitura da Cidade do Rio de Janeiro / IPP (Data.Rio)",
            "url_fonte": URL_BAIRROS,
            "epsg": "EPSG:4326"
        },
        "features": enriched_features
    }

    geojson_bytes = json.dumps(clean_geojson, ensure_ascii=False, indent=2).encode("utf-8")
    geojson_path = DATA_GEO_DIR / "bairros_rio_166_poligonos.geojson"
    with open(geojson_path, "wb") as f:
        f.write(geojson_bytes)

    # Copiar também para database/
    with open(DATABASE_DIR / "bairros_rio.geojson", "wb") as f:
        f.write(geojson_bytes)

    # Salvar Parquet
    df_bairros = pd.DataFrame(parquet_rows)
    parquet_path = DATA_GEO_DIR / "bairros_rio.parquet"
    df_bairros.to_parquet(parquet_path, engine="pyarrow", index=False)
    df_bairros.to_parquet(DATABASE_DIR / "bairros_rio.parquet", engine="pyarrow", index=False)

    # Metadados Sidecar
    meta = {
        "arquivo": "bairros_rio_166_poligonos.geojson",
        "formato": "GeoJSON (RFC 7946) & Parquet",
        "total_bairros": len(enriched_features),
        "sha256_geojson": compute_sha256(geojson_bytes),
        "tamanho_bytes": len(geojson_bytes),
        "data_extracao": datetime.now().isoformat(),
        "url_origem": URL_BAIRROS,
        "orgao_gestor": "Instituto Pereira Passos (IPP) / Prefeitura da Cidade do Rio de Janeiro",
        "resumo": "Malha vetorial georreferenciada de todos os 166 bairros oficiais do Rio de Janeiro em WGS84 (EPSG:4326)."
    }
    with open(DATA_GEO_DIR / "bairros_rio_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Bairros processados com sucesso: {len(enriched_features)} polígonos salvos.")


def fetch_and_process_aisp():
    print(f"Baixando malha oficial de AISP de {URL_AISP}...")
    req = urllib.request.Request(URL_AISP, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()

    data = json.loads(raw_bytes.decode("utf-8"))
    raw_features = data.get("features", [])
    print(f"AISPs brutas recebidas: {len(raw_features)}")

    enriched_features = []
    parquet_rows = []

    # Cores distintas para AISP no tema Dark (tons táticos e operacionais)
    palette = [
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899",
        "#14B8A6", "#F97316", "#6366F1", "#84CC16", "#06B6D4", "#A855F7"
    ]

    for idx, feat in enumerate(raw_features):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        c_lat, c_lon = compute_centroid(geom)

        aisp_num = props.get("AISP")
        meta_bpm = AISP_METADATA.get(aisp_num, {})
        batalhao = meta_bpm.get("batalhao", f"{aisp_num}º BPM")
        sede = meta_bpm.get("sede", "Desconhecido")
        nome_completo = meta_bpm.get("nome_completo", f"AISP {aisp_num} - {batalhao}")
        risp = meta_bpm.get("risp", props.get("RISP"))
        municipio = meta_bpm.get("municipio", "Estado do Rio de Janeiro")
        cor_hex = palette[idx % len(palette)]

        clean_props = {
            "id": idx + 1,
            "aisp": aisp_num,
            "batalhao": batalhao,
            "sede": sede,
            "nome_completo": nome_completo,
            "risp": risp,
            "municipio": municipio,
            "cor_hex": cor_hex,
            "centroide_lat": c_lat,
            "centroide_lon": c_lon,
            "fonte_oficial": "Instituto de Segurança Pública (ISP-RJ) / PMERJ",
            "camada": "Áreas Integradas de Segurança Pública (AISP)"
        }

        enriched_features.append({
            "type": "Feature",
            "properties": clean_props,
            "geometry": geom
        })

        parquet_rows.append({
            "id": idx + 1,
            "aisp": aisp_num,
            "batalhao": batalhao,
            "sede": sede,
            "nome_completo": nome_completo,
            "risp": risp,
            "municipio": municipio,
            "cor_hex": cor_hex,
            "centroide_lat": c_lat,
            "centroide_lon": c_lon,
            "geometry_json": json.dumps(geom)
        })

    clean_geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "titulo": "Áreas Integradas de Segurança Pública (AISP) - Batalhões PMERJ",
            "total_aisps": len(enriched_features),
            "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fonte": "Instituto de Segurança Pública (ISP-RJ) / PMERJ",
            "url_fonte": URL_AISP,
            "epsg": "EPSG:4326"
        },
        "features": enriched_features
    }

    geojson_bytes = json.dumps(clean_geojson, ensure_ascii=False, indent=2).encode("utf-8")
    geojson_path = DATA_GEO_DIR / "aisps_batalhoes_pmerj.geojson"
    with open(geojson_path, "wb") as f:
        f.write(geojson_bytes)

    # Copiar também para database/ conforme estrutura sugerida
    with open(DATABASE_DIR / "aisps_batalhoes.geojson", "wb") as f:
        f.write(geojson_bytes)

    # Salvar Parquet
    df_aisp = pd.DataFrame(parquet_rows)
    parquet_path = DATA_GEO_DIR / "aisps_batalhoes.parquet"
    df_aisp.to_parquet(parquet_path, engine="pyarrow", index=False)
    df_aisp.to_parquet(DATABASE_DIR / "aisps_batalhoes.parquet", engine="pyarrow", index=False)

    # Metadados Sidecar
    meta = {
        "arquivo": "aisps_batalhoes_pmerj.geojson",
        "formato": "GeoJSON (RFC 7946) & Parquet",
        "total_aisps": len(enriched_features),
        "sha256_geojson": compute_sha256(geojson_bytes),
        "tamanho_bytes": len(geojson_bytes),
        "data_extracao": datetime.now().isoformat(),
        "url_origem": URL_AISP,
        "orgao_gestor": "Instituto de Segurança Pública (ISP-RJ) / Secretaria de Estado de Polícia Militar (SEPM)",
        "resumo": "Delimitação territorial de todas as 39 AISPs (Áreas Integradas de Segurança Pública) vinculadas aos Batalhões da PMERJ."
    }
    with open(DATA_GEO_DIR / "aisps_batalhoes_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"AISPs processadas com sucesso: {len(enriched_features)} batalhões mapeados.")


if __name__ == "__main__":
    DATA_GEO_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    fetch_and_process_bairros()
    fetch_and_process_aisp()
