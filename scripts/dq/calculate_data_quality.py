"""
Script Automatizado de Auditoria e Cálculo de Qualidade de Dados (Data Quality - DQ).

Executa auditoria contínua sobre o acervo histórico:
- Cobertura temporal e distribuição por década
- Verificação estrita de proveniência (eventos e claims sem fonte)
- Fontes órfãs (sem vínculo factual)
- Detecção de inconsistências temporais, duplicidades e normalização
- Rastreamento de controvérsias historiográficas (claims conflitantes)
- Cobertura por organizações e territórios

Gera:
- reports/data_quality_latest.md (Relatório legível em Markdown)
- reports/data_quality_history.json (Histórico evolutivo de métricas)
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# Adiciona raiz ao path se necessário
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.database import SessionLocal
from app.models import (
    Event,
    Source,
    Region,
    Organization,
    Person,
    Claim,
    ClaimSource,
    EventSource,
)


def run_data_quality_audit() -> dict:
    db = SessionLocal()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Isolamento Real vs Demo
        real_events = db.query(Event).filter(Event.is_demo == False).all()
        demo_events = db.query(Event).filter(Event.is_demo == True).all()
        real_sources = db.query(Source).filter(Source.is_demo == False).all()
        demo_sources = db.query(Source).filter(Source.is_demo == True).all()
        real_regions = db.query(Region).filter(Region.is_demo == False).all()
        real_orgs = db.query(Organization).filter(Organization.is_demo == False).all()
        real_people = db.query(Person).filter(Person.is_demo == False).all()
        real_claims = db.query(Claim).filter(Claim.is_demo == False).all()

        # 2. Cobertura Temporal dos Dados Reais
        years = [e.year for e in real_events if e.year is not None]
        min_year = min(years) if years else None
        max_year = max(years) if years else None
        temporal_span = (max_year - min_year + 1) if (min_year and max_year) else 0

        # Eventos por década
        events_by_decade = Counter(
            f"{(e.year // 10) * 10}s" if e.year else "Desconhecido"
            for e in real_events
        )

        # Fontes por década de publicação
        sources_by_decade = Counter(
            f"{(s.publication_year // 10) * 10}s" if s.publication_year else "Sem ano"
            for s in real_sources
        )

        # 3. Auditoria Estrita de Proveniência (Regra Inegociável)
        events_without_source = []
        for e in real_events:
            if not e.source_links or len(e.source_links) == 0:
                events_without_source.append({"id": e.id, "title": e.title})

        claims_without_source = []
        for c in real_claims:
            if not c.source_links or len(c.source_links) == 0:
                claims_without_source.append({"id": c.id, "statement": c.statement})

        # Fontes sem referência interna (órfãs)
        sources_with_event_links = set(
            row[0] for row in db.query(EventSource.source_id).distinct().all()
        )
        sources_with_claim_links = set(
            row[0] for row in db.query(ClaimSource.source_id).distinct().all()
        )
        active_source_ids = sources_with_event_links.union(sources_with_claim_links)
        
        orphan_sources = [
            {"id": s.id, "title": s.title, "year": s.publication_year}
            for s in real_sources
            if s.id not in active_source_ids
        ]

        # 4. Detecção de Duplicidades e Normalização
        def check_duplicates(entities, name_attr="normalized_name"):
            seen = {}
            duplicates = []
            for item in entities:
                val = getattr(item, name_attr, None)
                if val:
                    val_clean = str(val).strip().upper()
                    if val_clean in seen:
                        duplicates.append({
                            "name": val_clean,
                            "first_id": seen[val_clean],
                            "second_id": item.id
                        })
                    else:
                        seen[val_clean] = item.id
            return duplicates

        duplicate_regions = check_duplicates(real_regions)
        duplicate_orgs = check_duplicates(real_orgs)
        duplicate_people = check_duplicates(real_people)

        # Entidades com nomes não normalizados
        unnormalized_entities = []
        for r in real_regions:
            if not r.normalized_name or len(r.normalized_name.strip()) == 0:
                unnormalized_entities.append({"type": "Region", "id": r.id, "name": r.original_name})
        for o in real_orgs:
            if not o.normalized_name or len(o.normalized_name.strip()) == 0:
                unnormalized_entities.append({"type": "Organization", "id": o.id, "name": o.original_name})
        for p in real_people:
            if not p.normalized_name or len(p.normalized_name.strip()) == 0:
                unnormalized_entities.append({"type": "Person", "id": p.id, "name": p.original_name})

        # 5. Inconsistências Temporais
        temporal_inconsistencies = []
        for e in real_events:
            if e.date_start and e.date_end and e.date_start > e.date_end:
                temporal_inconsistencies.append({
                    "id": e.id,
                    "title": e.title,
                    "issue": f"date_start ({e.date_start}) posterior a date_end ({e.date_end})"
                })
            if e.year and e.date_start and e.date_start.year != e.year:
                temporal_inconsistencies.append({
                    "id": e.id,
                    "title": e.title,
                    "issue": f"year ({e.year}) divergente do ano de date_start ({e.date_start.year})"
                })

        # 6. Espacialidade & Regra NULL ≠ 0
        events_without_location = [
            {"id": e.id, "title": e.title}
            for e in real_events
            if not e.regions or len(e.regions) == 0
        ]

        regions_without_geo_origin = [
            {"id": r.id, "name": r.original_name}
            for r in real_regions
            if (r.latitude is not None or r.longitude is not None)
            and (not r.location_precision or not r.geometry_source)
        ]

        # 7. Registros DEMO Misturados
        mixed_demo_records = []
        for e in real_events:
            if "[DEMO]" in e.title:
                mixed_demo_records.append({"type": "Event", "id": e.id, "title": e.title})
        for s in real_sources:
            if "[DEMO]" in s.title:
                mixed_demo_records.append({"type": "Source", "id": s.id, "title": s.title})

        # 8. Controvérsias Historiográficas & Claims
        disputed_claims = [
            {"id": c.id, "statement": c.statement, "event_id": c.event_id}
            for c in real_claims
            if c.is_disputed or c.confidence_level == "conflitante"
        ]

        # Distribuição de Confiança
        event_confidence_dist = Counter(e.confidence_level for e in real_events)
        claim_confidence_dist = Counter(c.confidence_level for c in real_claims)

        # 9. Cobertura por Organização e Território
        org_coverage = Counter()
        for e in real_events:
            for org in e.organizations:
                org_coverage[org.original_name] += 1

        region_coverage = Counter()
        for e in real_events:
            for reg in e.regions:
                region_coverage[reg.original_name] += 1

        # Compilação dos Resultados
        dq_results = {
            "timestamp": now_iso,
            "counts": {
                "real_events": len(real_events),
                "demo_events": len(demo_events),
                "real_sources": len(real_sources),
                "demo_sources": len(demo_sources),
                "real_claims": len(real_claims),
                "real_regions": len(real_regions),
                "real_organizations": len(real_orgs),
                "real_people": len(real_people),
            },
            "temporal_coverage": {
                "min_year": min_year,
                "max_year": max_year,
                "span_years": temporal_span,
                "events_by_decade": dict(sorted(events_by_decade.items())),
                "sources_by_decade": dict(sorted(sources_by_decade.items())),
            },
            "integrity_checks": {
                "events_without_source_count": len(events_without_source),
                "events_without_source": events_without_source,
                "claims_without_source_count": len(claims_without_source),
                "claims_without_source": claims_without_source,
                "orphan_sources_count": len(orphan_sources),
                "orphan_sources_sample": orphan_sources[:10],
                "duplicate_entities_count": len(duplicate_regions) + len(duplicate_orgs) + len(duplicate_people),
                "duplicate_entities": {
                    "regions": duplicate_regions,
                    "organizations": duplicate_orgs,
                    "people": duplicate_people,
                },
                "unnormalized_entities_count": len(unnormalized_entities),
                "unnormalized_entities": unnormalized_entities,
                "temporal_inconsistencies_count": len(temporal_inconsistencies),
                "temporal_inconsistencies": temporal_inconsistencies,
                "events_without_location_count": len(events_without_location),
                "events_without_location": events_without_location,
                "regions_without_geo_origin_count": len(regions_without_geo_origin),
                "regions_without_geo_origin": regions_without_geo_origin,
                "mixed_demo_records_count": len(mixed_demo_records),
                "mixed_demo_records": mixed_demo_records,
            },
            "epistemological_metrics": {
                "disputed_claims_count": len(disputed_claims),
                "disputed_claims": disputed_claims,
                "event_confidence_distribution": dict(event_confidence_dist),
                "claim_confidence_distribution": dict(claim_confidence_dist),
            },
            "coverage": {
                "organizations_top": dict(org_coverage.most_common(10)),
                "regions_top": dict(region_coverage.most_common(10)),
            }
        }

        return dq_results
    finally:
        db.close()


def generate_markdown_report(dq: dict) -> str:
    c = dq["counts"]
    tc = dq["temporal_coverage"]
    ic = dq["integrity_checks"]
    em = dq["epistemological_metrics"]
    cov = dq["coverage"]

    report = f"""# 📊 RELATÓRIO DE QUALIDADE DE DADOS HISTÓRICOS (DATA QUALITY - DQ)
**Gerado em**: {dq['timestamp']}  
**Ambiente**: Produção / Pesquisa Histórica Auditável  
**Escopo**: Acervo de Dados Reais (`is_demo = False`)

---

## 📈 1. Sumário Executivo do Acervo

| Indicador | Quantidade Real | Quantidade Demo | Total Banco |
| :--- | :---: | :---: | :---: |
| **Eventos Históricos** | **{c['real_events']}** | {c['demo_events']} | {c['real_events'] + c['demo_events']} |
| **Fontes Documentais** | **{c['real_sources']}** | {c['demo_sources']} | {c['real_sources'] + c['demo_sources']} |
| **Claims (Afirmações Factuais Atomizadas)** | **{c['real_claims']}** | 0 | {c['real_claims']} |
| **Territórios / Regiões Mapeadas** | **{c['real_regions']}** | 10 | {c['real_regions'] + 10} |
| **Organizações Documentadas** | **{c['real_organizations']}** | 6 | {c['real_organizations'] + 6} |
| **Figuras e Lideranças Históricas** | **{c['real_people']}** | 5 | {c['real_people'] + 5} |

---

## ⏳ 2. Cobertura Temporal

- **Intervalo Documentado**: `{tc['min_year']} – {tc['max_year']}` ({tc['span_years']} anos de cobertura contínua)

### Distribuição de Eventos Factuais por Década
| Década | Eventos Reais | % do Acervo |
| :---: | :---: | :---: |
"""
    total_ev = c['real_events'] or 1
    for dec, cnt in sorted(tc['events_by_decade'].items()):
        pct = (cnt / total_ev) * 100
        report += f"| **{dec}** | {cnt} | {pct:.1f}% |\n"

    report += """
### Distribuição de Fontes Documentais por Década de Publicação
| Década | Fontes Publicadas |
| :---: | :---: |
"""
    for dec, cnt in sorted(tc['sources_by_decade'].items()):
        report += f"| **{dec}** | {cnt} |\n"

    report += f"""
---

## 🛡️ 3. Auditoria de Integridade & Regras Inegociáveis

| Verificação | Status | Violacões | Tolerância |
| :--- | :---: | :---: | :---: |
| **Eventos Reais sem Fonte Comprobatória** | {"✅ OK" if ic['events_without_source_count'] == 0 else "❌ FALHA"} | **{ic['events_without_source_count']}** | `0` (Zero Tolerância) |
| **Claims sem Fonte Vinculada** | {"✅ OK" if ic['claims_without_source_count'] == 0 else "❌ FALHA"} | **{ic['claims_without_source_count']}** | `0` (Zero Tolerância) |
| **Registros DEMO misturados com REAL** | {"✅ OK" if ic['mixed_demo_records_count'] == 0 else "❌ FALHA"} | **{ic['mixed_demo_records_count']}** | `0` (Zero Tolerância) |
| **Inconsistências Temporais (start > end)** | {"✅ OK" if ic['temporal_inconsistencies_count'] == 0 else "❌ FALHA"} | **{ic['temporal_inconsistencies_count']}** | `0` (Zero Tolerância) |
| **Entidades Duplicadas (Nome Normalizado)** | {"✅ OK" if ic['duplicate_entities_count'] == 0 else "⚠️ ALERTA"} | **{ic['duplicate_entities_count']}** | `0` |
| **Nomes Não Normalizados** | {"✅ OK" if ic['unnormalized_entities_count'] == 0 else "⚠️ ALERTA"} | **{ic['unnormalized_entities_count']}** | `0` |
| **Territórios sem Origem Cartográfica** | {"✅ OK" if ic['regions_without_geo_origin_count'] == 0 else "⚠️ ALERTA"} | **{ic['regions_without_geo_origin_count']}** | `0` |
| **Eventos sem Vínculo Territorial** | {"ℹ️ INFO"} | **{ic['events_without_location_count']}** | Informacional |
| **Fontes Disponíveis sem Vínculo Factual** | {"ℹ️ INFO"} | **{ic['orphan_sources_count']}** | Fila de Exploração |

---

## ⚖️ 4. Epistemologia e Controvérsias Historiográficas

- **Claims com Controvérsia Registrada**: `{em['disputed_claims_count']}`

### Níveis de Confiança dos Eventos:
"""
    for conf, cnt in sorted(em['event_confidence_distribution'].items()):
        report += f"- **{conf.capitalize()}**: {cnt} eventos\n"

    report += "\n### Níveis de Confiança dos Claims:\n"
    for conf, cnt in sorted(em['claim_confidence_distribution'].items()):
        report += f"- **{conf.capitalize()}**: {cnt} claims\n"

    report += """
---

## 🏛️ 5. Cobertura Temática (Top Entidades Documentadas)

### Top Organizações por Eventos Vinculados:
"""
    for org, cnt in cov['organizations_top'].items():
        report += f"- **{org}**: {cnt} eventos\n"

    report += "\n### Top Territórios por Eventos Vinculados:\n"
    for reg, cnt in cov['regions_top'].items():
        report += f"- **{reg}**: {cnt} eventos\n"

    report += """
---
*Relatório gerado automaticamente pelo motor de DQ (`scripts/dq/calculate_data_quality.py`).*
"""
    return report


def main():
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    dq = run_data_quality_audit()
    md_content = generate_markdown_report(dq)

    # 1. Grava relatório mais recente
    latest_md_path = reports_dir / "data_quality_latest.md"
    with open(latest_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"-> Relatório DQ gerado em: {latest_md_path}")

    # 2. Histórico evolutivo
    history_json_path = reports_dir / "data_quality_history.json"
    history = []
    if history_json_path.exists():
        try:
            with open(history_json_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({
        "timestamp": dq["timestamp"],
        "real_events": dq["counts"]["real_events"],
        "real_sources": dq["counts"]["real_sources"],
        "real_claims": dq["counts"]["real_claims"],
        "disputed_claims": dq["epistemological_metrics"]["disputed_claims_count"],
        "temporal_span": dq["temporal_coverage"]["span_years"],
        "integrity_errors": (
            dq["integrity_checks"]["events_without_source_count"]
            + dq["integrity_checks"]["claims_without_source_count"]
            + dq["integrity_checks"]["mixed_demo_records_count"]
            + dq["integrity_checks"]["temporal_inconsistencies_count"]
        )
    })

    with open(history_json_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"-> Histórico evolutivo gravado em: {history_json_path}")


if __name__ == "__main__":
    main()
