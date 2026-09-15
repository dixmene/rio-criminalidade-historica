# -*- coding: utf-8 -*-
"""
Script para Geração da Fila de Prioridades de Pesquisa (docs/research_queue.md)
==============================================================================
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.services.coverage_service import CoverageService


def main():
    service = CoverageService()
    md_content = service.generate_markdown_queue(top_n=20, is_demo=False)

    out_file = _ROOT / "docs" / "research_queue.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[SUCESSO] Fila de prioridades de pesquisa gerada em: {out_file}")


if __name__ == "__main__":
    main()
