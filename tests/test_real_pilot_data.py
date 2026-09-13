"""
Teste de Integridade e Proveniência dos Dados Históricos Reais (Piloto 1970–1989).
Garante que a base real cumpre todas as regras do projeto:
- Zero invenção de coordenadas em territórios desconhecidos (REGRA NULL).
- Proveniência documental estrita: 100% dos eventos possuem trechos textuais literais.
- Isolamento total entre dados [DEMO] e dados reais.
- Temporalidade rigorosa preservando data original.
"""
import pytest
from app.database import SessionLocal
from app.services import EventService
from app.models import Event, Source, Region, Organization, Person


def test_real_pilot_dataset_integrity():
    db = SessionLocal()
    try:
        service = EventService(db)

        # 1. Validação quantitativa do piloto
        real_events = service.list_events(is_demo=False)
        assert len(real_events) >= 10, "Deveriam existir pelo menos 10 eventos históricos reais cadastrados."

        real_count = service.count_real_events()
        assert real_count >= 10

        # 2. Verificação de Proveniência Estrita para 100% dos eventos reais
        for ev in real_events:
            assert ev.is_demo is False
            assert len(ev.source_links) >= 1, f"O evento '{ev.title}' não possui fonte vinculada!"
            
            for link in ev.source_links:
                assert link.source is not None
                assert link.excerpt is not None
                assert len(link.excerpt.strip()) >= 10, f"O trecho da fonte para '{ev.title}' é muito curto ou vazio."
                assert link.validation_status in ("confirmado", "provavel", "conflitante")

        # 3. Verificação da Política de Não-Invenção de Coordenadas (REGRA NULL)
        regions = service.list_regions(is_demo=False)
        assert len(regions) >= 8

        # Deve existir pelo menos um território histórico sem coordenadas (ex: Rede Penitenciária Geral)
        unmapped_regions = [r for r in regions if r.latitude is None and r.longitude is None]
        assert len(unmapped_regions) >= 1, "Deveria existir pelo menos um território histórico sem coordenadas forçadas."
        for ur in unmapped_regions:
            assert ur.has_coordinates is False
            assert ur.location_precision == "desconhecida"

        # Regiões com coordenadas devem ter valores válidos no estado do Rio de Janeiro
        mapped_regions = [r for r in regions if r.latitude is not None]
        assert len(mapped_regions) >= 5
        for mr in mapped_regions:
            assert -24.0 <= mr.latitude <= -21.0
            assert -45.0 <= mr.longitude <= -41.0

        # 4. Verificação de Rigor Temporal
        # Evento de data exata: Fundação NuCOE (19 de janeiro de 1978)
        nucoe_ev = next((e for e in real_events if "NuCOE" in e.title and e.year == 1978), None)
        assert nucoe_ev is not None
        assert nucoe_ev.exact_date is True
        assert nucoe_ev.temporal_precision == "dia"
        assert nucoe_ev.date_display == "19 de janeiro de 1978"
        assert nucoe_ev.date_start == "1978-01-19"

        # Evento de ano aproximado: LSN na Ilha Grande (1970)
        lsn_ev = next((e for e in real_events if "Segurança Nacional" in e.title and e.year == 1970), None)
        assert lsn_ev is not None
        assert lsn_ev.exact_date is False
        assert lsn_ev.temporal_precision == "ano"
        assert lsn_ev.date_display == "1970"

        # 5. Verificação das Fontes e Hashes SHA-256
        real_sources = db.query(Source).filter(Source.is_demo == False).all()
        assert len(real_sources) >= 8
        sources_with_hash = [s for s in real_sources if s.file_hash_sha256 is not None]
        assert len(sources_with_hash) >= 4, "Fontes com arquivos físicos devem possuir hash SHA-256."

    finally:
        db.close()
