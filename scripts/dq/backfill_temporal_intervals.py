"""
Script de Alinhamento e Backfill Temporal de Eventos Históricos.

Executa a normalização temporal rigorosa em todos os registros da tabela 'events',
eliminando a falsa precisão e garantindo intervalos explícitos (date_start, date_end,
year, temporal_precision, exact_date, date_is_estimated) calculados estritamente a partir de date_display.
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import sqlite3
from src.normalization.rules import normalize_temporal_expression


def run_temporal_backfill(db_path: str = "data/rio_historico.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    events = c.execute(
        "SELECT id, title, date_display, date_start, date_end, year, temporal_precision, exact_date, date_is_estimated FROM events"
    ).fetchall()

    print(f"[*] Iniciando alinhamento temporal de {len(events)} eventos em '{db_path}'...")
    updated_count = 0

    for ev in events:
        ev_id, title, date_display, d_start, d_end, yr, prec, exact, est = ev
        parsed = normalize_temporal_expression(date_display)

        differs = (
            str(d_start) != str(parsed["date_start"]) or
            str(d_end) != str(parsed["date_end"]) or
            yr != parsed["year"] or
            prec != parsed["temporal_precision"] or
            bool(exact) != bool(parsed["exact_date"]) or
            bool(est) != bool(parsed["date_is_estimated"])
        )

        if differs:
            c.execute(
                """
                UPDATE events
                SET date_start = ?,
                    date_end = ?,
                    year = ?,
                    temporal_precision = ?,
                    exact_date = ?,
                    date_is_estimated = ?
                WHERE id = ?
                """,
                (
                    parsed["date_start"],
                    parsed["date_end"],
                    parsed["year"],
                    parsed["temporal_precision"],
                    1 if parsed["exact_date"] else 0,
                    1 if parsed["date_is_estimated"] else 0,
                    ev_id,
                ),
            )
            updated_count += 1

    conn.commit()
    conn.close()
    print(f"[+] Concluído: {updated_count} eventos atualizados com intervalos temporais rigorosos.")


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "data/rio_historico.db"
    run_temporal_backfill(db_file)
