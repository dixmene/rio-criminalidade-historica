"""
Script Automatizado de Verificação de Invariantes (Catraca de Qualidade).
Executado ao fim de TODO ciclo de pesquisa ou alteração no projeto.

Invariantes verificados:
- I1: Eventos reais sem fonte (exigido: 0)
- I2: Claims sem fonte (exigido: 0)
- I3: Claims sem excerpt literal (exigido: 0)
- I4: Registros DEMO visíveis em consultas de produção (exigido: 0)
- I5: Testes automatizados (100% verdes no pytest)
- I6: Territórios com coordenadas válidas e sem geometry_source (exigido: 0)
- I7: Eventos com data exata sem lastro documental (exigido: 0)
- I8: Referências no catálogo não resolvidas (exigido: 0 no catálogo ativo)
- I9: Proporção de eventos/claims com nível 'confirmado' (exigido: <= 70%)
- I10: Organizações sem organization_type / org_type (exigido: 0)
"""

import sys
import subprocess
from pathlib import Path

# Suporte UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona raiz ao path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.database import SessionLocal
from app.models import Event, Claim, Region, Organization, Source, EventSource, ClaimSource


def check_all_invariants() -> dict:
    db = SessionLocal()
    results = {}
    violations = []

    try:
        # I1: Eventos reais sem fonte
        real_events = db.query(Event).filter(Event.is_demo == False).all()
        i1_fails = [e.id for e in real_events if not e.source_links]
        results["I1_eventos_sem_fonte"] = len(i1_fails)
        if i1_fails:
            violations.append(f"I1 Falhou: {len(i1_fails)} eventos reais sem fontes ({i1_fails})")

        # I2: Claims sem fonte
        real_claims = db.query(Claim).filter(Claim.is_demo == False).all()
        i2_fails = [c.id for c in real_claims if not c.source_links]
        results["I2_claims_sem_fonte"] = len(i2_fails)
        if i2_fails:
            violations.append(f"I2 Falhou: {len(i2_fails)} claims sem fontes ({i2_fails})")

        # I3: Claims sem excerpt literal
        i3_fails = []
        for c in real_claims:
            for sl in c.source_links:
                if not sl.excerpt or len(sl.excerpt.strip()) < 5:
                    i3_fails.append(c.id)
                    break
        results["I3_claims_sem_excerpt"] = len(i3_fails)
        if i3_fails:
            violations.append(f"I3 Falhou: {len(i3_fails)} claims sem excerpt literal ({i3_fails})")

        # I4: Registros DEMO em consultas reais
        demo_leaks = db.query(Event).filter(Event.is_demo == False, Event.title.like("%[DEMO]%")).all()
        results["I4_demo_vazando"] = len(demo_leaks)
        if demo_leaks:
            violations.append(f"I4 Falhou: {len(demo_leaks)} registros [DEMO] em consultas reais")

        # I6: Territórios com coordenada e sem geometry_source
        real_regions = db.query(Region).filter(Region.is_demo == False).all()
        i6_fails = [r.id for r in real_regions if r.has_coordinates and not r.geometry_source]
        results["I6_territorios_sem_geometry_source"] = len(i6_fails)
        if i6_fails:
            violations.append(f"I6 Falhou: {len(i6_fails)} territórios com coordenadas sem geometry_source")

        # I7: Eventos com data exata sem lastro
        # Se exact_date=True, temporal_precision deve ser 'dia'
        i7_fails = [e.id for e in real_events if e.exact_date and e.temporal_precision != "dia"]
        results["I7_datas_exatas_sem_lastro"] = len(i7_fails)
        if i7_fails:
            violations.append(f"I7 Falhou: {len(i7_fails)} eventos com data exata inconsistente")

        # I8: Referências no catálogo não resolvidas (todas as fontes devem ter título e citação)
        real_sources = db.query(Source).filter(Source.is_demo == False).all()
        i8_fails = [s.id for s in real_sources if not s.title or not s.citation]
        results["I8_fontes_nao_resolvidas"] = len(i8_fails)
        if i8_fails:
            violations.append(f"I8 Falhou: {len(i8_fails)} fontes sem título ou citação")

        # I9: Proporção de eventos com nível 'confirmado' (exigido: <= 70%)
        total_events = len(real_events)
        confirmados = sum(1 for e in real_events if e.confidence_level == "confirmado")
        pct_confirmados = (confirmados / total_events * 100) if total_events > 0 else 0
        results["I9_pct_confirmados"] = round(pct_confirmados, 1)
        if pct_confirmados > 70.0:
            violations.append(f"I9 Falhou: Proporção de eventos 'confirmado' ({pct_confirmados:.1f}%) excede o teto de 70.0% (inflação de certeza)")

        # I10: Organizações sem organization_type
        real_orgs = db.query(Organization).filter(Organization.is_demo == False).all()
        i10_fails = [o.id for o in real_orgs if not o.org_type]
        results["I10_orgs_sem_tipo"] = len(i10_fails)
        if i10_fails:
            violations.append(f"I10 Falhou: {len(i10_fails)} organizações sem tipologia institucional")

    finally:
        db.close()

    # I5: Testes automatizados (pytest)
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_root)
        )
        results["I5_pytest_exit_code"] = res.returncode
        if res.returncode != 0:
            violations.append(f"I5 Falhou: Testes do pytest falharam com código {res.returncode}")
    except Exception as exc:
        results["I5_pytest_exit_code"] = -1
        violations.append(f"I5 Falhou ao rodar pytest: {exc}")

    results["passed"] = len(violations) == 0
    results["violations"] = violations
    return results


if __name__ == "__main__":
    res = check_all_invariants()
    print("=" * 60)
    print("VERIFICAÇÃO DE INVARIANTES DO PROJETO (CATRACA DE QUALIDADE)")
    print("=" * 60)
    for k, v in res.items():
        if k not in ("violations", "passed"):
            print(f"  {k:35s}: {v}")
    print("-" * 60)
    if res["passed"]:
        print("✅ TODOS OS INVARIANTES SATISFEITOS COM SUCESSO!")
        sys.exit(0)
    else:
        print("🚨 VIOLAÇÕES DE INVARIANTES DETECTADAS:")
        for v in res["violations"]:
            print(f"  ❌ {v}")
        sys.exit(1)
