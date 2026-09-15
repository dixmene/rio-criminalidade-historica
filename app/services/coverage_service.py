# -*- coding: utf-8 -*-
"""
Serviço de Análise de Cobertura Historiográfica e Lacunas Documentais (FASE 4)
=============================================================================

Mapeia a densidade documental por (região, década), calculando o Índice de
Densidade de Evidências (0.0 a 1.0) e gerando a Fila de Prioridades de Pesquisa
(Research Queue) para direcionar esforços de catalogação arquivística.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models import (
    Region,
    Event,
    Source,
    EventSource,
    EventRegion,
)


@dataclass
class CoverageCell:
    """Célula da matriz de cobertura para um par (região, década)."""
    region_id: int
    region_name: str
    region_type: str
    municipality: Optional[str]
    decade: int
    decade_label: str
    events_count: int
    sources_count: int
    independent_roots_count: int
    evidence_density_index: float
    coverage_status: str  # bem_documentado | parcial | lacunar | sem_documentacao

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CoverageService:
    """
    Serviço analítico para identificação de vazios historiográficos e lacunas documentais.
    """

    DECADES = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        return self._db if self._db is not None else SessionLocal()

    def get_coverage_matrix(self, is_demo: bool = False) -> List[CoverageCell]:
        """
        Gera a matriz completa de cobertura para todas as regiões e décadas.
        Calcula o Índice de Densidade de Evidências ponderando eventos e fontes primárias independentes.
        """
        db = self._get_db()
        close_after = (self._db is None)

        try:
            regions = db.query(Region).filter(Region.is_demo == is_demo).all()
            events = db.query(Event).options(
                joinedload(Event.region_links),
                joinedload(Event.source_links).joinedload(EventSource.source)
            ).filter(Event.is_demo == is_demo).all()

            # Mapeia eventos por (region_id, decade)
            reg_decade_events = defaultdict(list)
            for ev in events:
                if ev.year is None:
                    continue
                decade = (ev.year // 10) * 10
                for rlink in ev.region_links:
                    reg_decade_events[(rlink.region_id, decade)].append(ev)

            matrix = []
            for reg in regions:
                for dec in self.DECADES:
                    evs = reg_decade_events.get((reg.id, dec), [])
                    ev_count = len(evs)

                    # Coleta fontes associadas aos eventos da região nesta década
                    sources_seen = set()
                    independent_roots = set()

                    for ev in evs:
                        for slink in ev.source_links:
                            if slink.source:
                                sources_seen.add(slink.source.id)
                                root_src = slink.source.get_root_source() if hasattr(slink.source, "get_root_source") else slink.source
                                root_id = root_src.id if root_src else slink.source.id
                                independent_roots.add(root_id)

                    src_count = len(sources_seen)
                    indep_count = len(independent_roots)

                    # Cálculo do Índice de Densidade de Evidências (0.0 a 1.0)
                    # Fórmula normalizada: min(1.0, (ev_count * 0.3) + (indep_count * 0.4) + (src_count * 0.1))
                    score = (ev_count * 0.3) + (indep_count * 0.4) + (src_count * 0.1)
                    density_index = round(min(1.0, score), 3)

                    if density_index >= 0.7:
                        status = "bem_documentado"
                    elif density_index >= 0.35:
                        status = "parcial"
                    elif density_index > 0:
                        status = "lacunar"
                    else:
                        status = "sem_documentacao"

                    cell = CoverageCell(
                        region_id=reg.id,
                        region_name=reg.original_name,
                        region_type=reg.region_type,
                        municipality=reg.municipality,
                        decade=dec,
                        decade_label=f"{dec}s",
                        events_count=ev_count,
                        sources_count=src_count,
                        independent_roots_count=indep_count,
                        evidence_density_index=density_index,
                        coverage_status=status
                    )
                    matrix.append(cell)

            return matrix
        finally:
            if close_after:
                db.close()

    def get_coverage_summary(self, is_demo: bool = False) -> Dict[str, Any]:
        """
        Retorna síntese analítica da cobertura documental da base inteira.
        """
        matrix = self.get_coverage_matrix(is_demo=is_demo)
        total_cells = len(matrix)

        counts = {
            "bem_documentado": sum(1 for c in matrix if c.coverage_status == "bem_documentado"),
            "parcial": sum(1 for c in matrix if c.coverage_status == "parcial"),
            "lacunar": sum(1 for c in matrix if c.coverage_status == "lacunar"),
            "sem_documentacao": sum(1 for c in matrix if c.coverage_status == "sem_documentacao"),
        }

        avg_density = round(sum(c.evidence_density_index for c in matrix) / total_cells, 3) if total_cells > 0 else 0.0

        # Identificação de décadas mais e menos documentadas
        decade_densities = defaultdict(list)
        for c in matrix:
            decade_densities[c.decade].append(c.evidence_density_index)

        decade_averages = {
            dec: round(sum(scores) / len(scores), 3)
            for dec, scores in decade_densities.items()
        }

        return {
            "total_cells": total_cells,
            "counts": counts,
            "percentages": {
                k: round((v / total_cells) * 100, 1) if total_cells > 0 else 0.0
                for k, v in counts.items()
            },
            "overall_evidence_density": avg_density,
            "decade_averages": decade_averages
        }

    def get_research_queue(self, top_n: int = 15, is_demo: bool = False) -> List[Dict[str, Any]]:
        """
        Gera a Fila de Prioridade de Pesquisa (Research Queue).
        Filtra os territórios e décadas historicamente sensíveis com status 'lacunar' ou 'sem_documentacao'.
        """
        matrix = self.get_coverage_matrix(is_demo=is_demo)

        # Seleciona lacunas prioritárias (décadas entre 1960 e 2000 são críticas para a historiografia)
        priority_cells = [
            c for c in matrix
            if c.coverage_status in ("lacunar", "sem_documentacao")
            and c.decade in (1960, 1970, 1980, 1990)
        ]

        # Ordena priorizando territórios emblemáticos (complexos, favelas históricas, centros penitenciários)
        def _priority_weight(c: CoverageCell):
            weight = 0
            name_u = c.region_name.upper()
            if "ILHA GRANDE" in name_u or "GERICINO" in name_u or "FREI CANECA" in name_u:
                weight += 50
            if "ALEMAO" in name_u or "MARE" in name_u or "JACAREZINHO" in name_u or "CIDADE DE DEUS" in name_u:
                weight += 40
            if "SUBURBIO" in name_u or "AP3" in name_u or "CAXIAS" in name_u:
                weight += 30
            # Décadas cruciais
            if c.decade in (1970, 1980):
                weight += 20
            return -weight

        priority_cells.sort(key=_priority_weight)

        queue = []
        for c in priority_cells[:top_n]:
            queue.append({
                "region_id": c.region_id,
                "region_name": c.region_name,
                "region_type": c.region_type,
                "decade": c.decade,
                "decade_label": c.decade_label,
                "current_status": c.coverage_status,
                "current_density": c.evidence_density_index,
                "recommended_action": (
                    f"Localizar fontes primárias (hemeroteca/processos judiciais/relatórios policiais) "
                    f"sobre a atuação em {c.region_name} durante a década de {c.decade}."
                )
            })

        return queue

    def generate_markdown_queue(self, top_n: int = 15, is_demo: bool = False) -> str:
        """
        Gera relatório em Markdown estruturado para publicação em docs/research_queue.md.
        """
        summary = self.get_coverage_summary(is_demo=is_demo)
        queue = self.get_research_queue(top_n=top_n, is_demo=is_demo)

        lines = [
            "# Fila de Prioridades de Pesquisa Arquivística (Research Queue)",
            "",
            "> Este documento é gerado automaticamente pelo `CoverageService` para orientar pesquisadores,",
            "> arquivistas e cientistas de dados sobre os vazios documentais e lacunas historiográficas críticas do projeto.",
            "",
            "## 1. Diagnóstico Geral de Cobertura",
            "",
            f"- **Densidade Média de Evidências:** {summary['overall_evidence_density']} (escala 0.0 a 1.0)",
            f"- **Bem Documentados:** {summary['counts']['bem_documentado']} células ({summary['percentages']['bem_documentado']}%)",
            f"- **Parcialmente Documentados:** {summary['counts']['parcial']} células ({summary['percentages']['parcial']}%)",
            f"- **Lacunares:** {summary['counts']['lacunar']} células ({summary['percentages']['lacunar']}%)",
            f"- **Sem Documentação Identificada:** {summary['counts']['sem_documentacao']} células ({summary['percentages']['sem_documentacao']}%)",
            "",
            "### Média Histórica por Década",
            "",
            "| Década | Índice Médio de Evidência | Nível Diagnóstico |",
            "| :--- | :--- | :--- |",
        ]

        for dec, score in sorted(summary["decade_averages"].items()):
            diag = "Crítico (Lacunar)" if score < 0.2 else ("Intermediário" if score < 0.5 else "Consolidado")
            lines.append(f"| **{dec}s** | `{score}` | {diag} |")

        lines.extend([
            "",
            "## 2. Top 15 Prioridades de Catalogação Arquivística",
            "",
            "| Território Histórico | Década | Status Atual | Ação Recomendada |",
            "| :--- | :--- | :--- | :--- |"
        ])

        for item in queue:
            lines.append(
                f"| **{item['region_name']}** | {item['decade_label']} | `{item['current_status']}` | {item['recommended_action']} |"
            )

        lines.extend([
            "",
            "---",
            "*Gerado automaticamente pelo Atlas Espaço-Temporal do Rio de Janeiro.*"
        ])

        return "\n".join(lines)
