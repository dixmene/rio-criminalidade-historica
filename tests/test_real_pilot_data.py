"""
Teste de Integridade, Temporalidade e Proveniência do Acervo Histórico Real (1950–2026).
Garante que a base documental integral cumpre todas as regras metodológicas:
- REGRA 1 (ZERO vs NULL): Nenhuma invenção de coordenadas.
- Rastreabilidade Estrita: 100% dos eventos possuem trechos textuais literais (excerpts) e páginas.
- Isolamento total entre dados de teste técnico [DEMO] e história real.
- Temporalidade rigorosa com date_display preservado.
"""
import pytest
from app.database import SessionLocal
from app.services import EventService
from app.models import Event, Source, Region, Organization, Person


def test_real_historical_corpus_integrity():
    db = SessionLocal()
    try:
        service = EventService(db)

        # 1. Validação Quantitativa do Acervo Histórico Real (1950–2026)
        real_events = service.list_events(is_demo=False)
        assert len(real_events) >= 30, f"Deveriam existir pelo menos 30 eventos históricos reais cadastrados, encontrados {len(real_events)}."

        real_count = service.count_real_events()
        assert real_count >= 30

        # 2. Rastreabilidade Estrita para 100% dos Eventos Reais
        for ev in real_events:
            assert ev.is_demo is False
            assert len(ev.source_links) >= 1, f"O evento '{ev.title}' (ID {ev.id}) não possui fonte documental vinculada!"
            
            for link in ev.source_links:
                assert link.source is not None
                assert link.excerpt is not None
                assert len(link.excerpt.strip()) >= 10, f"O trecho comprobatório da fonte para '{ev.title}' é muito curto."
                assert link.validation_status in ("confirmado", "provavel", "conflitante")

        # 3. Política de Não-Invenção de Coordenadas (REGRA NULL)
        regions = service.list_regions(is_demo=False)
        assert len(regions) >= 15

        # Deve existir território histórico sem coordenadas (ex: Rede Penitenciária Geral)
        unmapped_regions = [r for r in regions if r.latitude is None and r.longitude is None]
        assert len(unmapped_regions) >= 1, "Deveria existir pelo menos um território histórico com coordenadas estritamente NULL."
        for ur in unmapped_regions:
            assert ur.has_coordinates is False
            assert ur.location_precision == "desconhecida"

        # Regiões georreferenciadas devem possuir coordenadas válidas no RJ
        mapped_regions = [r for r in regions if r.latitude is not None]
        assert len(mapped_regions) >= 10
        for mr in mapped_regions:
            assert -24.0 <= mr.latitude <= -21.0
            assert -45.0 <= mr.longitude <= -41.0

        # 4. Rigor Temporal Abrangente (1958 a 2026)
        # 1958: Criação do Grupo de Diligências Especiais (Le Cocq / E.M.)
        ev_1958 = next((e for e in real_events if e.year == 1958), None)
        assert ev_1958 is not None
        assert "Diligências Especiais" in ev_1958.title
        assert ev_1958.exact_date is False

        # 1978: Fundação do NuCOE (19 de janeiro de 1978)
        ev_nucoe = next((e for e in real_events if "NuCOE" in e.title and e.year == 1978), None)
        assert ev_nucoe is not None
        assert ev_nucoe.exact_date is True
        assert ev_nucoe.temporal_precision == "dia"
        assert ev_nucoe.date_display == "19 de janeiro de 1978"

        # 1979: Massacre da Falange Jacaré (17 de setembro de 1979)
        ev_1979 = next((e for e in real_events if "Massacre" in e.title and e.year == 1979), None)
        assert ev_1979 is not None
        assert ev_1979.exact_date is True
        assert ev_1979.date_start == "1979-09-17"

        # 2018: Assassinato de Marielle Franco e Anderson Gomes (14 de março de 2018)
        ev_marielle = next((e for e in real_events if "Marielle Franco" in e.title and e.year == 2018), None)
        assert ev_marielle is not None
        assert ev_marielle.exact_date is True
        assert ev_marielle.date_start == "2018-03-14"

        # 2020: Liminar da ADPF 635 (5 de junho de 2020)
        ev_adpf = next((e for e in real_events if "ADPF 635" in e.title and e.year == 2020), None)
        assert ev_adpf is not None
        assert ev_adpf.exact_date is True
        assert ev_adpf.date_start == "2020-06-05"

        # 2026: Condenação dos Irmãos Brazão no STF (25 de fevereiro de 2026)
        ev_brazao = next((e for e in real_events if "Brazão" in e.title and e.year == 2026), None)
        assert ev_brazao is not None
        assert ev_brazao.exact_date is True
        assert ev_brazao.date_start == "2026-02-25"

        # 5. Validação das Fontes Documentais e Hashes Criptográficos
        real_sources = db.query(Source).filter(Source.is_demo == False).all()
        assert len(real_sources) >= 15
        sources_with_hash = [s for s in real_sources if s.file_hash_sha256 is not None]
        assert len(sources_with_hash) >= 4, "Fontes com arquivos no acervo local devem possuir hash SHA-256."

    finally:
        db.close()
