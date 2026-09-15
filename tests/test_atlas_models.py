# -*- coding: utf-8 -*-
"""
Testes Unitários dos Modelos e Fundações do Atlas Espaço-Temporal (FASE 1)
========================================================================

Verifica:
1. Integridade de TerritorialDataset (metadados arquivísticos, licença, CRS).
2. Versionamento territorial (RegionVersion), vigência temporal e flag de anacronismo.
3. Preservação estrita da regra NULL != 0 (regiões 89, 91, 124 sem coordenadas inventadas).
4. Ciclo de vida de equipamentos institucionais (InstitutionalFacility).
5. Fluxos de deslocamento (MovementFlow).
6. Semântica estrita de relações territoriais (TerritorialRelation: controle vs presença vs disputa).
"""

import json
from datetime import date
from app.database import SessionLocal
from app.models.region import Region
from app.models.atlas import (
    TerritorialDataset,
    RegionVersion,
    TerritorialRelation,
    InstitutionalFacility,
    MovementFlow,
)


def test_territorial_datasets_integrity():
    """Verifica se os datasets geográficos foram devidamente cadastrados com proveniência."""
    db = SessionLocal()
    try:
        datasets = db.query(TerritorialDataset).all()
        assert len(datasets) >= 3, "Devem existir pelo menos 3 datasets cartográficos fundamentais cadastrados."

        for ds in datasets:
            assert ds.name is not None and len(ds.name) > 0
            assert ds.provider is not None and len(ds.provider) > 0
            assert ds.version is not None
            assert ds.crs in ("EPSG:4326", "EPSG:4674")
            assert ds.feature_count > 0, "feature_count deve ser positivo e auditável."
            assert ds.sha256 is not None, "Datasets oficiais devem possuir hash SHA-256 de auditoria."
    finally:
        db.close()


def test_region_versions_and_anachronism():
    """Verifica se as versões territoriais possuem GeoJSON válido e sinalização de anacronismo."""
    db = SessionLocal()
    try:
        versions = db.query(RegionVersion).all()
        assert len(versions) >= 25, "Devem existir versões espaciais para as regiões reais com coordenadas."

        for ver in versions:
            assert ver.region_id is not None
            assert ver.dataset_id is not None
            
            # Validação sintática do GeoJSON
            geom = json.loads(ver.geometry_geojson)
            assert "type" in geom
            assert geom["type"] in ("Polygon", "MultiPolygon", "Point")

            # Sinalização de anacronismo
            if ver.is_anachronistic:
                assert ver.anachronism_note is not None and len(ver.anachronism_note) > 0

            # Teste de método is_valid_for_year
            assert ver.is_valid_for_year(2025) is True
    finally:
        db.close()


def test_strict_null_preservation_in_atlas():
    """Garante que as regiões sem coordenadas da auditoria (89, 91, 124) NÃO possuem versões inventadas."""
    db = SessionLocal()
    try:
        for reg_id in (89, 91, 124):
            reg = db.query(Region).filter(Region.id == reg_id).first()
            if reg:
                assert reg.latitude is None and reg.longitude is None
                versions = db.query(RegionVersion).filter(RegionVersion.region_id == reg_id).all()
                assert len(versions) == 0, f"Região ID {reg_id} tem coordenadas NULL e não pode ter geometria inventada."
    finally:
        db.close()


def test_institutional_facility_lifecycle():
    """Testa o ciclo de vida (abertura e desativação) de instalações institucionais do Estado."""
    db = SessionLocal()
    try:
        facilities = db.query(InstitutionalFacility).all()
        assert len(facilities) >= 4

        # Ilha Grande: aberta ~1903, fechada/implodida em 1994
        candido_mendes = next((f for f in facilities if "Cândido Mendes" in f.name or "Dois Rios" in f.name), None)
        assert candido_mendes is not None
        assert candido_mendes.opened_at.year <= 1905
        assert candido_mendes.closed_at == date(1994, 4, 3)
        assert candido_mendes.is_operational_at_year(1979) is True
        assert candido_mendes.is_operational_at_year(1993) is True
        assert candido_mendes.is_operational_at_year(1995) is False
        assert candido_mendes.is_operational_at_year(2025) is False

        # Bangu 1: aberta em 1988, ainda ativa (closed_at is None)
        bangu1 = next((f for f in facilities if "Bangu 1" in f.name or "Laércio" in f.name), None)
        assert bangu1 is not None
        assert bangu1.opened_at == date(1988, 3, 1)
        assert bangu1.closed_at is None
        assert bangu1.is_operational_at_year(1980) is False
        assert bangu1.is_operational_at_year(1988) is True
        assert bangu1.is_operational_at_year(2025) is True

        # Frei Caneca: aberta em 1928, implodida em 2006
        frei_caneca = next((f for f in facilities if "Frei Caneca" in f.name), None)
        assert frei_caneca is not None
        assert frei_caneca.is_operational_at_year(1980) is True
        assert frei_caneca.is_operational_at_year(2010) is False

        # NuCOE: aberto em 19/01/1978
        nucoe = next((f for f in facilities if "NuCOE" in f.name), None)
        assert nucoe is not None
        assert nucoe.opened_at == date(1978, 1, 19)
        assert nucoe.is_operational_at_year(1977) is False
        assert nucoe.is_operational_at_year(1978) is True
    finally:
        db.close()


def test_movement_flows():
    """Testa o registro de fluxos e arcos de deslocamento espaço-temporal."""
    db = SessionLocal()
    try:
        flows = db.query(MovementFlow).all()
        assert len(flows) >= 2

        fuga = next((fl for fl in flows if fl.flow_type == "fuga"), None)
        assert fuga is not None
        assert fuga.date_start == date(1985, 12, 31)
        assert "Escadinha" in fuga.notes

        transf = next((fl for fl in flows if fl.flow_type == "transferencia_penitenciaria"), None)
        assert transf is not None
        assert transf.date_start == date(1988, 3, 1)
        assert "Bangu 1" in transf.notes
    finally:
        db.close()


def test_territorial_relations_strict_semantics():
    """Verifica a semântica rigorosa das relações de domínio e presença armada."""
    db = SessionLocal()
    try:
        relations = db.query(TerritorialRelation).all()
        assert len(relations) >= 4

        types = {r.relation_type for r in relations}
        assert "controle" in types
        assert "disputa" in types
        assert "presenca_estatal" in types

        # Relação em disputa deve estar marcada como is_contested
        disputa_rel = next((r for r in relations if r.relation_type == "disputa"), None)
        assert disputa_rel is not None
        assert disputa_rel.is_contested is True
    finally:
        db.close()
