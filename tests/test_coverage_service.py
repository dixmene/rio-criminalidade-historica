# -*- coding: utf-8 -*-
"""
Testes Unitários do CoverageService e Diagnóstico de Lacunas (FASE 4)
=====================================================================
"""

from pathlib import Path
from app.services.coverage_service import CoverageService, CoverageCell


def test_coverage_matrix_and_cells():
    """Valida o cálculo da matriz de cobertura por (região, década)."""
    service = CoverageService()
    matrix = service.get_coverage_matrix(is_demo=False)

    assert len(matrix) > 0
    assert isinstance(matrix[0], CoverageCell)

    # Todas as células devem ter década válida e índice entre 0.0 e 1.0
    for cell in matrix:
        assert cell.decade in CoverageService.DECADES
        assert 0.0 <= cell.evidence_density_index <= 1.0
        assert cell.coverage_status in ("bem_documentado", "parcial", "lacunar", "sem_documentacao")


def test_coverage_summary():
    """Valida os totais, contagens e médias calculadas pelo sumário de cobertura."""
    service = CoverageService()
    summary = service.get_coverage_summary(is_demo=False)

    assert summary["total_cells"] > 0
    assert 0.0 <= summary["overall_evidence_density"] <= 1.0
    assert "counts" in summary
    assert "decade_averages" in summary
    assert 1970 in summary["decade_averages"]


def test_research_queue_generation():
    """Verifica que a fila de pesquisa identifica lacunas e sugere ações prioritárias."""
    service = CoverageService()
    queue = service.get_research_queue(top_n=10, is_demo=False)

    assert len(queue) > 0
    assert len(queue) <= 10

    for item in queue:
        assert item["current_status"] in ("lacunar", "sem_documentacao")
        assert len(item["recommended_action"]) > 0


def test_research_queue_markdown_file():
    """Garante que o arquivo docs/research_queue.md existe e contém a estrutura esperada."""
    md_file = Path(__file__).resolve().parent.parent / "docs" / "research_queue.md"
    assert md_file.exists(), "docs/research_queue.md deve existir."

    content = md_file.read_text(encoding="utf-8")
    assert "# Fila de Prioridades de Pesquisa Arquivística" in content
    assert "Densidade Média de Evidências" in content
    assert "Top 15 Prioridades" in content or "Prioridades de Catalogação" in content
