import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.scripts.seed_demo import seed_demo_data
from app.services import EventService
from app.database import engine, SessionLocal


def test_timeline_and_filters():
    # Inicializa e popula banco de teste
    seed_demo_data()
    db = SessionLocal()
    try:
        service = EventService(db)

        # 1. Teste de intervalo de anos (1975 a 1980)
        events_75_80 = service.list_events(year_min=1975, year_max=1980)
        assert len(events_75_80) >= 4
        for ev in events_75_80:
            assert 1975 <= ev.year <= 1980

        # 2. Teste de busca por região (Centro)
        regions = service.list_regions()
        centro = next((r for r in regions if r.name == "Centro"), None)
        assert centro is not None

        events_centro = service.list_events(region_id=centro.id)
        assert len(events_centro) >= 2
        for ev in events_centro:
            assert any(r.id == centro.id for r in ev.regions)

        # 3. Teste de busca por nível de confiança
        conflitantes = service.list_events(confidence_level="conflitante")
        assert len(conflitantes) >= 1
        assert any("Explosão" in ev.title or "Incidente" in ev.title for ev in conflitantes)

    finally:
        db.close()
