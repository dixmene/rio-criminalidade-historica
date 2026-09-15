#!/usr/bin/env python3
"""
Gerenciador da Fila de Verificação Epistemológica (Verification Queue CLI)
========================================================================

Executa a auditoria heurística e genealógica de todas as afirmações do banco,
identificando casos de falsa triangulação, controvérsias ativas e dependência
exclusiva de fontes secundárias.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.services.verification_service import VerificationService


def main():
    parser = argparse.ArgumentParser(description="Gerenciamento da Fila de Verificação Epistemológica")
    parser.add_argument("--output", type=str, default="data/verification_queue.json",
                        help="Arquivo JSON onde salvar a fila de verificação")
    parser.add_argument("--include-demo", action="store_true",
                        help="Inclui dados marcados como demonstração/sintéticos")
    parser.add_argument("--min-priority", type=str, default=None,
                        choices=["CRITICA", "ALTA", "MEDIA", "BAIXA"],
                        help="Filtra a fila por prioridade mínima")
    args = parser.parse_args()

    out_path = PROJECT_ROOT / args.output
    session = SessionLocal()

    try:
        print("=== Auditoria da Fila de Verificação Epistemológica ===")
        print(f"Incluir dados DEMO: {args.include_demo}")
        print(f"Prioridade mínima: {args.min_priority or 'TODAS'}")
        print("-" * 60)

        report = VerificationService.generate_verification_queue(
            session=session,
            include_demo=args.include_demo,
            min_priority=args.min_priority
        )

        report["generated_at"] = datetime.now(timezone.utc).isoformat()
        report["output_file"] = str(out_path)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"Total de Claims auditadas:          {report['total_claims_audited']}")
        print(f"Itens na fila de verificação:       {report['queue_size']}")
        print(f"  - Prioridade CRÍTICA (Disputa):   {report['summary_by_priority']['CRITICA']}")
        print(f"  - Prioridade ALTA (Triangulação): {report['summary_by_priority']['ALTA']}")
        print(f"  - Prioridade MÉDIA (Sem Primária):{report['summary_by_priority']['MEDIA']}")
        print(f"  - Prioridade BAIXA (Ancorada):    {report['summary_by_priority']['BAIXA']}")
        print("-" * 60)
        print(f"Falsa Triangulação detectada:       {report['false_triangulations_detected']} casos")
        print(f"Claims sem Fonte Primária:          {report['unanchored_secondary_claims']}")
        print(f"Claims com Controvérsia/Disputa:    {report['disputed_claims']}")
        print(f"[+] Fila de verificação salva em: {out_path}")
        print("=" * 60)

    finally:
        session.close()


if __name__ == "__main__":
    main()
