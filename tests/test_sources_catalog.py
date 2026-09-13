"""
Teste do Catálogo Completo de Fontes Bibliográficas e Documentais.
Valida a integridade das 159+ fontes importadas de lista_fontes_pesquisa_rio.xlsx.
"""
import pytest
from app.database import SessionLocal
from app.models import Source


def test_sources_catalog_coverage_and_metadata():
    db = SessionLocal()
    try:
        real_sources = db.query(Source).filter(Source.is_demo == False).all()
        assert len(real_sources) >= 150, f"Deveriam existir pelo menos 150 fontes reais no acervo, encontradas {len(real_sources)}."

        # Validação de metadados obrigatórios em todas as fontes
        for s in real_sources:
            assert s.title is not None and len(s.title.strip()) > 0
            assert s.citation is not None and len(s.citation.strip()) > 0
            assert s.source_type in (
                "academico_artigo",
                "academico_livro",
                "academico_tese",
                "documento_judicial",
                "oficial_relatorio",
                "jornalismo_investigativo",
                "jornalismo_hemeroteca",
                "historia_oral",
                "cartografia_digital"
            )

        # Verificar presença de eixos temáticos estruturantes
        notes_blob = " ".join([s.notes or "" for s in real_sources])
        assert "Milícias & Governança Armada" in notes_blob
        assert "História das Facções do Tráfico" in notes_blob
        assert "Economia & Desindustrialização" in notes_blob
        assert "Letalidade Policial & ADPF 635" in notes_blob
        assert "Fundamentos Teóricos & Sociologia" in notes_blob
        assert "Caso Marielle & Conexões Políticas" in notes_blob
    finally:
        db.close()
