# -*- coding: utf-8 -*-
"""
Edge-case and regression test suite for refactored and optimized modules:
- ClaimValidator (bit-parallel LCS exactness, ellipsis fallback, Unicode)
- EventService / DataService / IngestionService (selectinload, batch validation, cache isolation)
- GenealogyService / VerificationService (O(V+E) GenealogyIndex parity, cycles, min_priority)
- Normalization rules & legislative taxonomy classifier (word boundaries, overlapping terms)
- Geospatial STRtree spatial join, Parquet cache safety, ISP aggregation ZERO != NULL & SHA-256
"""

from datetime import date
from difflib import SequenceMatcher
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.map.layers import load_aisp_dataframe
from app.models import (
    Claim,
    ClaimSource,
    Event,
    EventOrganization,
    EventRegion,
    EventSource,
    Organization,
    Region,
    Source,
    SourceDerivation,
)
from app.schemas import ClaimCreate, ClaimSourceLinkInput, EventCreate, EventSourceLinkInput
from app.services.claim_validator import (
    ClaimValidator,
    _bit_parallel_lcs_len,
    _build_lcs_masks,
    normalize_text,
)
from app.services.data_service import DataService
from app.services.event_service import EventService
from app.services.genealogy_service import GenealogyService
from app.services.ingestion_service import IngestionService
from app.services.verification_service import VerificationService
from scripts.classifier_pautas import classify_legislative_text
from scripts.etl_tse_votacao import calculate_hhi, match_point_to_aisp
from scripts.geospatial.process_isp_timeseries import aggregate_isp_timeseries
from scripts.ingestion.ingest_source import calculate_sha256
from src.normalization.rules import normalize_nulls, normalize_temporal_expression
from src.utils.unicode_normalization import normalize_string_unicode


# =============================================================================
# 1. CLAIM VALIDATOR & BIT-PARALLEL LCS REGRESSION TESTS
# =============================================================================


def test_bit_parallel_lcs_always_upper_bounds_sequence_matcher():
    """Bit-parallel LCS ratio must unconditionally >= SequenceMatcher.ratio()."""
    pairs = [
        ("beira mar se uniu a 30 homens em bangu", "beira mar se uniu a 30 homens em bangu"),
        ("beira mar se uniu a 30 homens", "beira mar reuniu trinta homens no presidio"),
        ("operacao policial na mare 1994", "submarino nuclear invisivel no corcovado"),
        ("a b c d e f g h", "a x b x c x d x e x f x g x h"),
        ("sao goncalo duque de caxias", "sao goncalo e duque caxias"),
    ]
    for window, needle in pairs:
        masks = _build_lcs_masks(needle)
        lcs_len = _bit_parallel_lcs_len(window, masks)
        lcs_ub = (2.0 * lcs_len) / (len(window) + len(needle))
        sm_ratio = SequenceMatcher(None, window, needle).ratio()
        assert lcs_ub + 1e-12 >= sm_ratio


def test_claim_validator_fuzzy_asr_drift_and_unicode_symbols():
    """Fuzzy ASR variations near threshold must pass; Unicode symbols must not break."""
    transcript = (
        "no dia 11 de setembro de 2002 na galeria b do presidio de bangu 1 "
        "o grupo liderado por fernandinho beira mar atacou a ala controlada por erinaldo § 1º"
    )
    # 2 slight ASR typos -> still well above 0.75
    excerpt = (
        "na galeria b do presidio de bangu 1 o grupo liderado por "
        "fernandinho beira mars atacou a ala controlada por erinaldos"
    )
    res = ClaimValidator.validate_verbatim_excerpt(excerpt, transcript, min_similarity=0.75)
    assert res["valid"] is True
    assert res["match_type"] == "fuzzy"
    assert res["similarity"] >= 0.75

    # Pure ASCII vs accented/NFKD vs non-Latin Unicode normalization parity
    assert normalize_text("São Gonçalo — 1º BPM!") == "sao goncalo 1o bpm"
    assert normalize_text("plain ascii 123, test!") == "plain ascii 123 test"
    assert normalize_text("Análise β-teste!") == "analise β teste"


def test_claim_validator_ellipsis_rejects_partial_hallucination():
    """If the second clause in an ellipsis quote is fabricated, it must be rejected."""
    transcript = (
        "a reuniao ocorreu no presidio da ilha grande em 1979 com liderancas locais "
        "e resultou na reorganizacao do coletivo interno"
    )
    fake_ellipsis = (
        "a reuniao ocorreu no presidio da ilha grande em 1979 ... "
        "helicopteros estrangeiros bombardearam o telhado do pavilhao central"
    )
    res = ClaimValidator.validate_verbatim_excerpt(fake_ellipsis, transcript)
    assert res["valid"] is False
    assert res["match_type"] == "none"


def test_claim_validator_timestamp_edge_cases():
    assert ClaimValidator.validate_timestamp("-10")["valid"] is False
    assert ClaimValidator.validate_timestamp("00:00", duration_seconds=60.0)["valid"] is True
    # Within 5s end tolerance
    assert ClaimValidator.validate_timestamp("01:04", duration_seconds=60.0)["valid"] is True
    assert ClaimValidator.validate_timestamp("01:06", duration_seconds=60.0)["valid"] is False


# =============================================================================
# 2. EVENT / DATA / INGESTION SERVICES REGRESSION TESTS
# =============================================================================


def test_event_service_filters_and_empty_bounds(db_session):
    """Verify selectinload + .any() filters never duplicate events and handle empty DB."""
    svc = EventService(db_session)
    assert svc.get_timeline_bounds(is_demo=False) == (1970, 1989)
    assert svc.count_real_events() == 0

    src = Source(title="Doc A", citation="Ref A", source_type="oficial_relatorio", is_demo=False)
    reg1 = Region(original_name="Bangu", normalized_name="BANGU", is_demo=False)
    reg2 = Region(original_name="Maré", normalized_name="MARE", is_demo=False)
    org = Organization(original_name="CV", normalized_name="CV", is_demo=False)
    db_session.add_all([src, reg1, reg2, org])
    db_session.flush()

    ev = Event(
        title="Evento Multi-Região",
        date_display="1985",
        date_start=date(1985, 1, 1),
        date_end=date(1985, 12, 31),
        year=1985,
        temporal_precision="ano",
        description="Evento conectado a duas regiões.",
        is_demo=False,
    )
    db_session.add(ev)
    db_session.flush()

    db_session.add_all([
        EventSource(event_id=ev.id, source_id=src.id, excerpt="Trecho documental válido."),
        EventRegion(event_id=ev.id, region_id=reg1.id),
        EventRegion(event_id=ev.id, region_id=reg2.id),
        EventOrganization(event_id=ev.id, organization_id=org.id),
    ])
    db_session.commit()

    by_reg = svc.list_events(region_id=reg1.id, is_demo=False)
    assert len(by_reg) == 1
    assert len(by_reg[0].region_links) == 2
    assert svc.get_timeline_bounds(is_demo=False) == (1985, 1985)
    assert svc.count_real_events() == 1


def test_ingestion_service_batch_source_validation(db_session):
    """Batch source check must reject missing source IDs and short excerpts cleanly."""
    ing = IngestionService(db_session)
    src = Source(title="Inquérito", citation="PCERJ, 1980", source_type="documento_judicial", is_demo=False)
    db_session.add(src)
    db_session.commit()

    bad_event = EventCreate(
        title="Evento Fonte Inexistente",
        date_display="1980",
        description="Descrição suficientemente longa para validação.",
        is_demo=False,
        sources=[EventSourceLinkInput(source_id=99999, excerpt="Trecho válido com mais de 5 chars")],
    )
    with pytest.raises(ValueError, match="não encontrada"):
        ing.create_event(bad_event)

    bad_claim = ClaimCreate(
        event_id=1,
        statement="Afirmação com fonte ausente",
        is_demo=True,
        sources=[ClaimSourceLinkInput(source_id=99999, stance="apoia", excerpt="Trecho válido")],
    )
    with pytest.raises(ValueError, match="não encontrada"):
        ing.create_claim(bad_claim)


def test_data_service_faction_cache_isolation(db_session):
    """Mutating the dict returned by get_faction_distribution must not poison cache."""
    ds = DataService(db_session)
    first = ds.get_faction_distribution()
    assert first["total_areas"] == 1671
    first["factions"]["CV"] = -999
    first["total_areas"] = 0

    second = ds.get_faction_distribution()
    assert second["total_areas"] == 1671
    assert second["factions"]["CV"] > 0

    missing = ds.get_faction_distribution(geojson_path=Path("nonexistent_factions.geojson"))
    assert missing == {"total_areas": 0, "factions": {}, "percentages": {}}


# =============================================================================
# 3. GENEALOGY INDEX & VERIFICATION QUEUE PARITY / CYCLE TESTS
# =============================================================================


def test_genealogy_index_handles_chains_independence_and_cycles(db_session):
    """build_genealogy_index must match get_root_source and detect cycles in O(V+E)."""
    s_root = Source(title="Inquérito Original", citation="Ref 0", source_type="documento_judicial", is_demo=True)
    s_mid = Source(title="Livro Intermediário", citation="Ref 1", source_type="academico_livro", is_demo=True)
    s_leaf = Source(title="Vídeo Derivado", citation="Ref 2", source_type="audiovisual_youtube", is_demo=True)
    s_indep = Source(title="Pesquisa Independente", citation="Ref 3", source_type="academico_tese", is_demo=True)
    s_cyc_a = Source(title="Ciclo A", citation="Ref A", source_type="academico_artigo", is_demo=True)
    s_cyc_b = Source(title="Ciclo B", citation="Ref B", source_type="academico_artigo", is_demo=True)
    db_session.add_all([s_root, s_mid, s_leaf, s_indep, s_cyc_a, s_cyc_b])
    db_session.flush()

    db_session.add_all([
        SourceDerivation(parent_source_id=s_root.id, derived_source_id=s_mid.id, is_independent=False),
        SourceDerivation(parent_source_id=s_mid.id, derived_source_id=s_leaf.id, is_independent=False),
        # Independent citation must NOT collapse s_indep into s_root
        SourceDerivation(parent_source_id=s_root.id, derived_source_id=s_indep.id, is_independent=True),
        # Cycle: s_cyc_a <-> s_cyc_b
        SourceDerivation(parent_source_id=s_cyc_b.id, derived_source_id=s_cyc_a.id, is_independent=False),
        SourceDerivation(parent_source_id=s_cyc_a.id, derived_source_id=s_cyc_b.id, is_independent=False),
    ])
    db_session.commit()

    idx = GenealogyService.build_genealogy_index(db_session)
    assert idx.root_cache[s_leaf.id].id == s_root.id
    assert idx.root_cache[s_mid.id].id == s_root.id
    assert idx.root_cache[s_root.id].id == s_root.id
    assert idx.root_cache[s_indep.id].id == s_indep.id

    cyclic = GenealogyService.find_cyclic_sources(idx)
    cyclic_ids = {item["source_id"] for item in cyclic}
    assert cyclic_ids == {s_cyc_a.id, s_cyc_b.id}


def test_verification_queue_min_priority_filtering(db_session):
    """min_priority filter must return only items at or above the threshold."""
    ev = Event(title="Ev", date_display="1990", description="Desc", is_demo=True)
    s1 = Source(title="Oficial 1", citation="C1", source_type="documento_judicial", is_demo=True)
    s2 = Source(title="Oficial 2", citation="C2", source_type="documento_oficial", is_demo=True)
    db_session.add_all([ev, s1, s2])
    db_session.flush()

    c_crit = Claim(event_id=ev.id, statement="Disputada", is_disputed=True, is_demo=True)
    c_low = Claim(event_id=ev.id, statement="Bem fundamentada", confidence_level="confirmado", is_demo=True)
    db_session.add_all([c_crit, c_low])
    db_session.flush()

    db_session.add_all([
        ClaimSource(claim_id=c_low.id, source_id=s1.id, stance="apoia", excerpt="Trecho oficial 1"),
        ClaimSource(claim_id=c_low.id, source_id=s2.id, stance="apoia", excerpt="Trecho oficial 2"),
    ])
    db_session.commit()

    only_crit = VerificationService.generate_verification_queue(
        db_session, include_demo=True, min_priority="CRITICA"
    )
    assert only_crit["total_claims_audited"] == 2
    assert only_crit["queue_size"] == 1
    assert only_crit["queue"][0]["priority"] == "CRITICA"
    assert only_crit["summary_by_priority"]["BAIXA"] == 1


# =============================================================================
# 4. NORMALIZATION & LEGISLATIVE CLASSIFIER REGRESSION TESTS
# =============================================================================


def test_temporal_and_unicode_edge_cases():
    assert normalize_temporal_expression(1975)["temporal_precision"] == "ano"
    assert normalize_temporal_expression(123)["temporal_precision"] == "desconhecido"
    assert normalize_temporal_expression("29/02/2020")["date_start"] == "2020-02-29"
    assert normalize_temporal_expression("década de 1980")["date_end"] == "1989-12-31"
    assert normalize_temporal_expression("abril de 1981")["date_end"] == "1981-04-30"
    assert normalize_temporal_expression("por volta de 1994 no Rio")["date_is_estimated"] is True
    assert normalize_nulls(float("nan")) is None

    assert normalize_string_unicode("  Rio   de  Janeiro  ") == "RIO DE JANEIRO"
    assert normalize_string_unicode("São João de Meriti") == "SAO JOAO DE MERITI"
    assert normalize_string_unicode(None) is None


def test_legislative_classifier_overlapping_terms_and_word_boundaries():
    """Must detect overlapping keywords independently and respect word boundaries."""
    res_van = classify_legislative_text("Regulamenta o itinerário de van na Zona Oeste")
    assert "van" in res_van["termos_identificados"]
    assert "itinerario de van" in res_van["termos_identificados"]

    res_cobre = classify_legislative_text("Combate ao furto de fios de cobre")
    assert "cobre" in res_cobre["termos_identificados"]
    assert "fios de cobre" in res_cobre["termos_identificados"]

    # Word boundary check: "descobre" and "vanguarda" must NOT trigger "cobre" or "van"
    res_false = classify_legislative_text("Projeto cultural de vanguarda que descobre novos talentos")
    assert res_false["possui_convergencia_sensivel"] is False
    assert res_false["termos_identificados"] == []


# =============================================================================
# 5. GEOSPATIAL, ISP VECTORIZATION & SHA-256 REGRESSION TESTS
# =============================================================================


def test_match_point_to_aisp_edge_cases():
    assert match_point_to_aisp(-22.9, -43.2, []) is None
    square = {
        "type": "Feature",
        "properties": {"aisp": 99, "batalhao": "99º BPM"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-43.3, -23.0], [-43.1, -23.0], [-43.1, -22.8], [-43.3, -22.8], [-43.3, -23.0]]],
        },
    }
    assert match_point_to_aisp(-22.9, -43.2, [square]) == {"aisp": 99, "batalhao": "99º BPM"}
    assert match_point_to_aisp(0.0, 0.0, [square]) is None
    assert calculate_hhi([]) == 0.0
    assert calculate_hhi([0.0, 0.0]) == 0.0


def test_isp_aggregation_preserves_zero_vs_null_and_totals():
    """Vectorized ISP aggregation must preserve NaN before 2007 and exact AISP->State sums."""
    df_cisp = pd.DataFrame([
        {"aisp": 14, "cisp": 34, "ano": 2006, "mes": 1, "hom_doloso": 5, "hom_por_interv_policial": 0, "armas_apreendidas": np.nan},
        {"aisp": 14, "cisp": 35, "ano": 2006, "mes": 1, "hom_doloso": 3, "hom_por_interv_policial": 0, "armas_apreendidas": np.nan},
        {"aisp": 14, "cisp": 34, "ano": 2007, "mes": 1, "hom_doloso": 4, "hom_por_interv_policial": 2, "armas_apreendidas": 0.0},
        {"aisp": 15, "cisp": 59, "ano": 2007, "mes": 1, "hom_doloso": 6, "hom_por_interv_policial": 1, "armas_apreendidas": 7.0},
    ])
    out = aggregate_isp_timeseries(df_cisp)

    row_2006 = out[(out["nivel_geografico"] == "aisp") & (out["periodicidade"] == "mensal") & (out["ano"] == 2006)].iloc[0]
    assert row_2006["hom_doloso"] == 8
    assert row_2006["hom_por_interv_policial"] == 0
    assert pd.isna(row_2006["armas_apreendidas"])  # NULL preserved, not turned into 0!
    assert row_2006["data_referencia"] == "2006-01"
    assert row_2006["batalhao"] == "14º BPM"

    est_2007 = out[(out["nivel_geografico"] == "estado") & (out["periodicidade"] == "anual") & (out["ano"] == 2007)].iloc[0]
    assert est_2007["hom_doloso"] == 10
    assert est_2007["armas_apreendidas"] == 7.0
    assert est_2007["batalhao"] == "Total Estadual"


def test_parquet_cache_defensive_copy_and_sha256_streaming(tmp_path):
    df1 = load_aisp_dataframe()
    assert df1 is not None
    df1["_temp_test_col"] = 123
    df2 = load_aisp_dataframe()
    assert "_temp_test_col" not in df2.columns

    sample = tmp_path / "custody_sample.bin"
    payload = b"arquivo historico rio de janeiro " * 10000
    sample.write_bytes(payload)
    assert calculate_sha256(sample) == hashlib.sha256(payload).hexdigest()
