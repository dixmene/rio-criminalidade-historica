import pytest
from app.scripts.seed_demo import seed_demo_data
from app.services import EventService
from app.database import SessionLocal


def test_timeline_and_filters():
    # Inicializa e popula banco de teste com dados [DEMO]
    seed_demo_data()
    db = SessionLocal()
    try:
        service = EventService(db)

        # 1. Teste de intervalo de anos (1975 a 1980)
        events_75_80 = service.list_events(year_min=1975, year_max=1980)
        assert len(events_75_80) >= 4
        for ev in events_75_80:
            assert 1975 <= ev.year <= 1980

        # 2. Teste de busca por região (Centro) e validação de nomes normalizados
        regions = service.list_regions()
        centro = next((r for r in regions if r.original_name == "Centro"), None)
        assert centro is not None
        assert centro.normalized_name == "CENTRO"

        events_centro = service.list_events(region_id=centro.id)
        assert len(events_centro) >= 2
        for ev in events_centro:
            assert any(r.id == centro.id for r in ev.regions)

        # 3. Teste de busca por nível de confiança (conflitante)
        conflitantes = service.list_events(confidence_level="conflitante")
        assert len(conflitantes) >= 1
        assert any("Explosão" in ev.title or "Incidente" in ev.title for ev in conflitantes)

        # 4. Teste de isolamento DEMO vs REAL
        demo_count = service.count_demo_events()
        assert demo_count >= 10
        real_events = service.list_events(is_demo=False)
        for rev in real_events:
            assert rev.is_demo is False

        # 5. Teste de região sem coordenadas geográficas (não inventa coordenadas)
        unmapped_region = next((r for r in regions if r.latitude is None), None)
        assert unmapped_region is not None
        assert unmapped_region.has_coordinates is False

    finally:
        db.close()
