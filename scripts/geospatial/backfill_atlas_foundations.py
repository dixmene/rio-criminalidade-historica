# -*- coding: utf-8 -*-
"""
Script de Backfill das Fundações do Atlas Espaço-Temporal (FASE 1)
==================================================================

1. Registra metadados arquivísticos dos datasets cartográficos (TerritorialDataset):
   - dadosderiscos (1.671 polígonos de comunidades e facções)
   - aisp_batalhoes_pmerj (39 circunscrições policiais)
   - bairros_pcrj (166 bairros oficiais do Rio de Janeiro)

2. Associa RegionVersion às 32 regiões existentes no banco de dados:
   - Vincula geometrias oficiais (polígonos do IPP ou dadosderiscos) ou pontos referenciais
   - Sinaliza rigorosamente is_anachronistic=True para malhas contemporâneas aplicadas a períodos pretéritos
   - Preserva estritamente NULL para regiões sem coordenadas/geometrias (NULL != 0)

3. Semeia equipamentos institucionais com ciclo de vida (InstitutionalFacility):
   - Presídio de Ilha Grande (abertura ~1903, implosão 1994)
   - Bangu 1 (abertura 1988, ativo)
   - Complexo da Frei Caneca (abertura 1928, desativação 2006)
   - NuCOE / BOPE (abertura 1978 no CFAP/Sulacap)

4. Semeia fluxos espaço-temporais (MovementFlow):
   - Fuga de Escadinha da Ilha Grande (1985)
   - Transferência inaugural de lideranças para Bangu 1 (1988)

5. Semeia relações territoriais iniciais com semântica estrita (TerritorialRelation):
   - Separação rigorosa entre 'controle', 'presenca', 'disputa' e 'presenca_estatal'
"""

import sys
import os
import json
import unicodedata
from datetime import date
from pathlib import Path

# Adiciona a raiz do projeto ao path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.database import SessionLocal
from app.models.region import Region
from app.models.organization import Organization
from app.models.source import Source
from app.models.claim import Claim
from app.models.atlas import (
    TerritorialDataset,
    RegionVersion,
    TerritorialRelation,
    InstitutionalFacility,
    MovementFlow,
)


def _normalize(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def run_backfill():
    db = SessionLocal()
    try:
        print("[1/5] Registrando TerritorialDatasets...")
        
        # 1. TerritorialDataset: dadosderiscos
        ds_faccoes = db.query(TerritorialDataset).filter(TerritorialDataset.name.like("%dadosderiscos%")).first()
        if not ds_faccoes:
            ds_faccoes = TerritorialDataset(
                name="Mapeamento de Áreas de Risco e Facções Armadas — dadosderiscos",
                provider="dadosderiscos.com.br",
                provider_url="https://dadosderiscos.com.br/mapa-rj-risco-faccoes.html",
                version="2024.1",
                reference_period_start=date(2024, 1, 1),
                reference_period_end=date(2026, 12, 31),
                methodology_summary="Compilação colaborativa e georreferenciada de 1.671 polígonos de comunidades e favelas com presença e atuação armada no Grande Rio.",
                license="Uso Acadêmico/Pesquisa",
                sha256="c0ea0aed7aab3768974028162be3a99415a555b471fa90b1daa23d0d755d1b6d",
                crs="EPSG:4326",
                geometry_type="Polygon",
                feature_count=1671,
                notes="Camada contemporânea. A aplicação desta malha a eventos anteriores a 2024 constitui anacronismo cartográfico ilustrativo.",
                is_demo=False
            )
            db.add(ds_faccoes)
            db.flush()
            print(f"  + Criado TerritorialDataset: {ds_faccoes.name} (id={ds_faccoes.id})")
        else:
            print(f"  = TerritorialDataset já existente: {ds_faccoes.name} (id={ds_faccoes.id})")

        # 2. TerritorialDataset: aisp_batalhoes_pmerj
        ds_aisp = db.query(TerritorialDataset).filter(TerritorialDataset.name.like("%AISP%")).first()
        if not ds_aisp:
            ds_aisp = TerritorialDataset(
                name="Delimitação das Áreas Integradas de Segurança Pública (AISP / PMERJ)",
                provider="Instituto de Segurança Pública (ISP-RJ) / SEPM",
                provider_url="https://services.arcgis.com/qFQYQQeTXZSPY7Fs/arcgis/rest/services/Limite_AISP/FeatureServer/0",
                version="2023.1",
                reference_period_start=date(2023, 1, 1),
                reference_period_end=date(2026, 12, 31),
                methodology_summary="Divisão territorial oficial das 39 circunscrições integradas da Polícia Militar do Estado do Rio de Janeiro.",
                license="Dados Abertos Governo RJ",
                sha256="33f7e28f0ba39ce1185bdaf67d0d89670a48acd3e6addf8e84e91c6099faf2b3",
                crs="EPSG:4326",
                geometry_type="MultiPolygon",
                feature_count=39,
                notes="Malha de divisão policial militar contemporânea oficial.",
                is_demo=False
            )
            db.add(ds_aisp)
            db.flush()
            print(f"  + Criado TerritorialDataset: {ds_aisp.name} (id={ds_aisp.id})")
        else:
            print(f"  = TerritorialDataset já existente: {ds_aisp.name} (id={ds_aisp.id})")

        # 3. TerritorialDataset: bairros_pcrj
        ds_bairros = db.query(TerritorialDataset).filter(TerritorialDataset.name.like("%Bairros Oficiais%")).first()
        if not ds_bairros:
            ds_bairros = TerritorialDataset(
                name="Malha Vetorial de Bairros Oficiais do Município do Rio de Janeiro",
                provider="Instituto Pereira Passos (IPP) / PCRJ / Data.Rio",
                provider_url="https://pgeo3.rio.rj.gov.br/arcgis/rest/services/Cartografia/Limites_administrativos/MapServer/4",
                version="2022.1",
                reference_period_start=date(2022, 1, 1),
                reference_period_end=date(2026, 12, 31),
                methodology_summary="Delimitação cartográfica oficial dos 166 bairros do Município do Rio de Janeiro estabelecida pela legislação municipal vigente.",
                license="Dados Abertos PCRJ",
                sha256="6c7b74046992ffa5115c7804a7a3612a901a6503b0d00447522b419eb148270c",
                crs="EPSG:4326",
                geometry_type="MultiPolygon",
                feature_count=166,
                notes="Delimitação contemporânea de bairros segundo limites político-administrativos de 2022.",
                is_demo=False
            )
            db.add(ds_bairros)
            db.flush()
            print(f"  + Criado TerritorialDataset: {ds_bairros.name} (id={ds_bairros.id})")
        else:
            print(f"  = TerritorialDataset já existente: {ds_bairros.name} (id={ds_bairros.id})")

        # Carrega GeoJSONs para associação de geometrias
        bairros_path = _ROOT / "data" / "geospatial" / "bairros_rio_166_poligonos.geojson"
        faccoes_path = _ROOT / "data" / "geospatial" / "faccoes_rj_1671_poligonos.geojson"

        bairros_features = {}
        if bairros_path.exists():
            with open(bairros_path, "r", encoding="utf-8") as f:
                b_data = json.load(f)
                for feat in b_data.get("features", []):
                    nome = feat.get("properties", {}).get("nome", "")
                    if nome:
                        bairros_features[_normalize(nome)] = feat

        faccoes_features = {}
        if faccoes_path.exists():
            with open(faccoes_path, "r", encoding="utf-8") as f:
                f_data = json.load(f)
                for feat in f_data.get("features", []):
                    nome = feat.get("properties", {}).get("nome", "")
                    if nome:
                        faccoes_features[_normalize(nome)] = feat

        print("\n[2/5] Populando RegionVersions para regiões existentes...")
        regions = db.query(Region).all()
        created_versions_count = 0

        for reg in regions:
            # Verifica se já possui versão
            existing_ver = db.query(RegionVersion).filter(RegionVersion.region_id == reg.id).first()
            if existing_ver:
                continue

            # Regra estrita NULL != 0: se a região não tem coordenadas nem geometria,
            # NÃO criamos geometria artificial. O atlas não deve mentir.
            if reg.latitude is None or reg.longitude is None:
                print(f"  - Região ID {reg.id} ('{reg.original_name}'): coordenadas estritamente NULL. Nenhuma versão inventada.")
                continue

            norm_name = _normalize(reg.original_name)
            geometry = None
            assigned_ds = ds_bairros
            geom_source = "IPP / PCRJ (2022)"
            precision = reg.location_precision or "aproximada"
            is_anach = True
            anach_note = "Malha de 2022/2024 aplicada como referência contemporânea — fronteira ilustrativa, não histórica para períodos anteriores."

            # Tenta match com bairros oficiais
            if norm_name in bairros_features:
                geometry = bairros_features[norm_name]["geometry"]
                assigned_ds = ds_bairros
                geom_source = "Bairros Oficiais PCRJ / IPP (2022)"
                precision = "oficial_bairro"
            else:
                # Tenta match aproximado em bairros
                matched_bairro = None
                for b_name, b_feat in bairros_features.items():
                    if b_name in norm_name or norm_name in b_name:
                        matched_bairro = b_feat
                        break
                if matched_bairro and reg.region_type in ("bairro", "municipio"):
                    geometry = matched_bairro["geometry"]
                    assigned_ds = ds_bairros
                    geom_source = f"Bairros Oficiais PCRJ / IPP (2022) — match por '{matched_bairro['properties']['nome']}'"
                    precision = "oficial_bairro"

            # Tenta match em favelas/comunidades
            if not geometry:
                matched_faccao = None
                for f_name, f_feat in faccoes_features.items():
                    if f_name == norm_name or f_name in norm_name or norm_name in f_name:
                        matched_faccao = f_feat
                        break
                if matched_faccao:
                    geometry = matched_faccao["geometry"]
                    assigned_ds = ds_faccoes
                    geom_source = f"dadosderiscos.com.br (2024) — polígono '{matched_faccao['properties']['nome']}'"
                    precision = "poligono_comunidade"

            # Se não encontrou polígono, utiliza Ponto GeoJSON a partir das coordenadas verificadas
            if not geometry:
                geometry = {
                    "type": "Point",
                    "coordinates": [float(reg.longitude), float(reg.latitude)]
                }
                geom_source = reg.geometry_source or "Levantamento documental / Coordenada de referência"
                precision = "centroide_ponto"

            ver = RegionVersion(
                region_id=reg.id,
                dataset_id=assigned_ds.id,
                geometry_geojson=json.dumps(geometry, ensure_ascii=False),
                valid_from=assigned_ds.reference_period_start,
                valid_to=assigned_ds.reference_period_end,
                geometry_source=geom_source,
                location_precision=precision,
                is_anachronistic=is_anach,
                anachronism_note=anach_note
            )
            db.add(ver)
            created_versions_count += 1

        db.flush()
        print(f"  + Total de RegionVersions criadas: {created_versions_count}")

        print("\n[3/5] Semeando Equipamentos Institucionais (InstitutionalFacility)...")
        # Busca fonte documental de referência para ancoragem arquivística
        doc_source = db.query(Source).filter(Source.citation.like("%Amorim%")).first()
        source_id = doc_source.id if doc_source else None

        # Busca versões de regiões para ancoragem espacial
        reg_ver_ilha = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%ILHA GRANDE%")).first()
        reg_ver_bangu = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%GERICINO%")).first()
        reg_ver_centro = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%CENTRO%")).first()
        reg_ver_sulacap = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%SULACAP%")).first()

        facilities_to_seed = [
            {
                "name": "Instituto Penal Cândido Mendes (Colônia Penal de Dois Rios)",
                "facility_type": "presidio",
                "region_version_id": reg_ver_ilha.id if reg_ver_ilha else None,
                "latitude": -23.1856,
                "longitude": -44.1925,
                "opened_at": date(1903, 1, 1),
                "closed_at": date(1994, 4, 3),  # Implosão histórica sob governo Nilo Batista
                "capacity": 1200,
                "source_id": source_id,
                "notes": "Colônia correcional e presídio de segurança máxima da Ilha Grande. Berço da convivência entre presos políticos e comuns sob a LSN (1969-1979) e da gênese da Falange Vermelha. Desativado e implodido em abril de 1994.",
                "geometry_geojson": json.dumps({"type": "Point", "coordinates": [-44.1925, -23.1856]})
            },
            {
                "name": "Penitenciária Laércio da Costa Pellegrino (Bangu 1)",
                "facility_type": "presidio_seguranca_maxima",
                "region_version_id": reg_ver_bangu.id if reg_ver_bangu else None,
                "latitude": -22.855,
                "longitude": -43.483,
                "opened_at": date(1988, 3, 1),
                "closed_at": None,
                "capacity": 48,
                "source_id": source_id,
                "notes": "Primeiro presídio de segurança máxima construído no Complexo de Gericinó (Bangu), projetado para abrigar lideranças de facções criminosas em isolamento estrito celular.",
                "geometry_geojson": json.dumps({"type": "Point", "coordinates": [-43.483, -22.855]})
            },
            {
                "name": "Complexo Penitenciário da Rua Frei Caneca (Hélio Gomes / Milton Dias Moreira)",
                "facility_type": "complexo_penitenciario",
                "region_version_id": reg_ver_centro.id if reg_ver_centro else None,
                "latitude": -22.911,
                "longitude": -43.193,
                "opened_at": date(1928, 1, 1),
                "closed_at": date(2006, 3, 25),  # Implosão em 2006
                "capacity": 2500,
                "source_id": source_id,
                "notes": "Conjunto prisional histórico localizado na região central/Estácio. Cenário de rebeliões e transferências fundamentais na década de 1980. Implodido em 2006 para moradia popular.",
                "geometry_geojson": json.dumps({"type": "Point", "coordinates": [-43.193, -22.911]})
            },
            {
                "name": "Núcleo da Cia. de Operações Especiais — NuCOE / BOPE (Sede Fundacional)",
                "facility_type": "batalhao_pmerj",
                "region_version_id": reg_ver_sulacap.id if reg_ver_sulacap else None,
                "latitude": -22.889,
                "longitude": -43.402,
                "opened_at": date(1978, 1, 19),  # Boletim da PM nº 33 de 19/01/1978
                "closed_at": None,
                "capacity": None,
                "source_id": source_id,
                "notes": "Sede fundacional do NuCOE nas instalações do Centro de Formação e Aperfeiçoamento de Praças (CFAP) em Jardim Sulacap, embrião do moderno BOPE.",
                "geometry_geojson": json.dumps({"type": "Point", "coordinates": [-43.402, -22.889]})
            }
        ]

        seeded_fac_count = 0
        for fac_data in facilities_to_seed:
            existing = db.query(InstitutionalFacility).filter(InstitutionalFacility.name == fac_data["name"]).first()
            if not existing:
                fac = InstitutionalFacility(
                    name=fac_data["name"],
                    facility_type=fac_data["facility_type"],
                    region_version_id=fac_data["region_version_id"],
                    latitude=fac_data["latitude"],
                    longitude=fac_data["longitude"],
                    opened_at=fac_data["opened_at"],
                    closed_at=fac_data["closed_at"],
                    capacity=fac_data["capacity"],
                    source_id=fac_data["source_id"],
                    notes=fac_data["notes"],
                    geometry_geojson=fac_data["geometry_geojson"],
                    is_demo=False
                )
                db.add(fac)
                seeded_fac_count += 1
                print(f"  + Criado InstitutionalFacility: {fac.name}")
            else:
                print(f"  = InstitutionalFacility já existente: {existing.name}")

        db.flush()

        print("\n[4/5] Semeando Fluxos Espaço-Temporais (MovementFlow)...")
        flows_to_seed = [
            {
                "flow_type": "fuga",
                "origin_geometry": json.dumps({"type": "Point", "coordinates": [-44.1925, -23.1856]}),
                "origin_region_version_id": reg_ver_ilha.id if reg_ver_ilha else None,
                "destination_geometry": json.dumps({"type": "Point", "coordinates": [-43.327, -22.863]}),
                "destination_region_version_id": None,
                "date_start": date(1985, 12, 31),
                "date_end": date(1985, 12, 31),
                "temporal_precision": "dia",
                "evidence_strength": "documentada_primaria",
                "notes": "Fuga cinematográfica em helicóptero Bell 206 alugado pousando no campo de futebol do Instituto Penal Cândido Mendes na Ilha Grande, levando a liderança José Carlos dos Reis Encina (Escadinha) para o Morro do Juramento."
            },
            {
                "flow_type": "transferencia_penitenciaria",
                "origin_geometry": json.dumps({"type": "Point", "coordinates": [-43.193, -22.911]}),
                "origin_region_version_id": reg_ver_centro.id if reg_ver_centro else None,
                "destination_geometry": json.dumps({"type": "Point", "coordinates": [-43.483, -22.855]}),
                "destination_region_version_id": reg_ver_bangu.id if reg_ver_bangu else None,
                "date_start": date(1988, 3, 1),
                "date_end": date(1988, 3, 1),
                "temporal_precision": "dia",
                "evidence_strength": "documentada_primaria",
                "notes": "Transferência inaugural e em massa de 48 principais lideranças do Comando Vermelho da Frei Caneca para o recém-inaugurado isolamento celular de Bangu 1 sob o governo Moreira Franco."
            }
        ]

        seeded_flows_count = 0
        for fl_data in flows_to_seed:
            existing = db.query(MovementFlow).filter(
                MovementFlow.flow_type == fl_data["flow_type"],
                MovementFlow.date_start == fl_data["date_start"]
            ).first()
            if not existing:
                fl = MovementFlow(
                    flow_type=fl_data["flow_type"],
                    origin_geometry=fl_data["origin_geometry"],
                    origin_region_version_id=fl_data["origin_region_version_id"],
                    destination_geometry=fl_data["destination_geometry"],
                    destination_region_version_id=fl_data["destination_region_version_id"],
                    date_start=fl_data["date_start"],
                    date_end=fl_data["date_end"],
                    temporal_precision=fl_data["temporal_precision"],
                    evidence_strength=fl_data["evidence_strength"],
                    notes=fl_data["notes"],
                    is_demo=False
                )
                db.add(fl)
                seeded_flows_count += 1
                print(f"  + Criado MovementFlow: {fl.flow_type} em {fl.date_start}")
            else:
                print(f"  = MovementFlow já existente: {existing.flow_type} em {existing.date_start}")

        db.flush()

        print("\n[5/5] Semeando Relações Territoriais Iniciais (TerritorialRelation)...")
        # Busca organizações históricas
        cv_org = db.query(Organization).filter(Organization.acronym == "CV").first()
        mil_org = db.query(Organization).filter(Organization.acronym.like("%MIL%")).first()
        bope_org = db.query(Organization).filter(Organization.acronym == "BOPE").first()

        # Busca versões de regiões
        reg_ver_alemao = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%ALEMAO%")).first()
        reg_ver_cdd = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%CIDADE DE DEUS%")).first()
        reg_ver_pedras = db.query(RegionVersion).join(Region).filter(Region.normalized_name.like("%RIO DAS PEDRAS%")).first()

        relations_to_seed = []
        if reg_ver_ilha and cv_org:
            relations_to_seed.append({
                "region_version_id": reg_ver_ilha.id,
                "organization_id": cv_org.id,
                "relation_type": "controle",
                "date_start": date(1979, 9, 17),
                "date_end": date(1994, 4, 3),
                "temporal_precision": "dia",
                "evidence_strength": "documentada_primaria",
                "independent_root_count": 2,
                "is_contested": False,
                "notes": "Hegemonia prisional consolidada no Cândido Mendes após a eliminação das lideranças da Falange Jacaré em 17/09/1979 até a implosão do presídio em 1994."
            })

        if reg_ver_alemao and cv_org:
            relations_to_seed.append({
                "region_version_id": reg_ver_alemao.id,
                "organization_id": cv_org.id,
                "relation_type": "controle",
                "date_start": date(1994, 1, 1),
                "date_end": None,
                "temporal_precision": "ano",
                "evidence_strength": "documentada_primaria",
                "independent_root_count": 3,
                "is_contested": False,
                "notes": "Bastião histórico e quartel-general de comando territorial do Comando Vermelho na Zona Norte."
            })

        if reg_ver_pedras and mil_org:
            relations_to_seed.append({
                "region_version_id": reg_ver_pedras.id,
                "organization_id": mil_org.id,
                "relation_type": "controle",
                "date_start": date(1995, 1, 1),
                "date_end": None,
                "temporal_precision": "ano",
                "evidence_strength": "documentada_primaria",
                "independent_root_count": 3,
                "is_contested": False,
                "notes": "Berço histórico e centro de consolidação do modelo miliciano baseado em cobrança de taxas e controle imobiliário/comercial."
            })

        if reg_ver_cdd and cv_org:
            relations_to_seed.append({
                "region_version_id": reg_ver_cdd.id,
                "organization_id": cv_org.id,
                "relation_type": "disputa",
                "date_start": date(2000, 1, 1),
                "date_end": None,
                "temporal_precision": "ano",
                "evidence_strength": "documentada_secundaria",
                "independent_root_count": 2,
                "is_contested": True,
                "notes": "Território historicamente caracterizado por sucessivas disputas territoriais entre facções de tráfico e incursões de milícias vizinhas."
            })

        if reg_ver_sulacap and bope_org:
            relations_to_seed.append({
                "region_version_id": reg_ver_sulacap.id,
                "organization_id": bope_org.id,
                "relation_type": "presenca_estatal",
                "date_start": date(1978, 1, 19),
                "date_end": None,
                "temporal_precision": "dia",
                "evidence_strength": "documentada_primaria",
                "independent_root_count": 2,
                "is_contested": False,
                "notes": "Presença militar institucional oficial fundacional do NuCOE nas dependências do CFAP."
            })

        seeded_rel_count = 0
        for rel_data in relations_to_seed:
            existing = db.query(TerritorialRelation).filter(
                TerritorialRelation.region_version_id == rel_data["region_version_id"],
                TerritorialRelation.organization_id == rel_data["organization_id"],
                TerritorialRelation.relation_type == rel_data["relation_type"]
            ).first()
            if not existing:
                rel = TerritorialRelation(
                    region_version_id=rel_data["region_version_id"],
                    organization_id=rel_data["organization_id"],
                    relation_type=rel_data["relation_type"],
                    date_start=rel_data["date_start"],
                    date_end=rel_data["date_end"],
                    temporal_precision=rel_data["temporal_precision"],
                    evidence_strength=rel_data["evidence_strength"],
                    independent_root_count=rel_data["independent_root_count"],
                    is_contested=rel_data["is_contested"],
                    notes=rel_data["notes"],
                    is_demo=False
                )
                db.add(rel)
                seeded_rel_count += 1
                print(f"  + Criado TerritorialRelation: {rel.relation_type} em RegVer {rel.region_version_id}")
            else:
                print(f"  = TerritorialRelation já existente: {existing.relation_type} em RegVer {existing.region_version_id}")

        db.commit()
        print(f"\n[SUCESSO] Backfill das fundações do Atlas concluído com integridade!")
        print(f"  - Datasets: {db.query(TerritorialDataset).count()}")
        print(f"  - RegionVersions: {db.query(RegionVersion).count()}")
        print(f"  - InstitutionalFacilities: {db.query(InstitutionalFacility).count()}")
        print(f"  - MovementFlows: {db.query(MovementFlow).count()}")
        print(f"  - TerritorialRelations: {db.query(TerritorialRelation).count()}")

    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] Falha durante o backfill: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_backfill()
