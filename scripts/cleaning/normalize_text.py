"""
CLI de Demonstração e Execução de Normalização de Dados.
Aplica as regras de normalização de Unicode e a REGRA 1 (ZERO vs. NULL).
"""
import sys
from src.normalization.rules import (
    normalize_nulls,
    normalize_name,
    normalize_location,
    normalize_organization,
    normalize_date,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_demonstration():
    print("=== DEMONSTRAÇÃO DAS REGRAS DE NORMALIZAÇÃO ===\n")

    # 1. Teste de Nomes
    names = ["João da Silva", "Rogério Lemgruber", "Élcio de Queiroz", "  Maré  ", None]
    print("1. Normalização de Nomes:")
    for n in names:
        res = normalize_name(n)
        print(f"   Original: '{n}' -> Dual: {res}")

    # 2. Teste de Regiões / Locais
    locs = ["São Gonçalo", "Praça Seca", "Niterói", "Duque de Caxias", "desconhecido"]
    print("\n2. Normalização de Localidades:")
    for l in locs:
        res = normalize_location(l)
        print(f"   Original: '{l}' -> Dual: {res}")

    # 3. Teste da REGRA 1 (ZERO vs NULL)
    test_values = [0, "0", None, "", "N/A", "desconhecido", "não informado", 42, "42"]
    print("\n3. Aplicação da REGRA 1 (ZERO vs. NULL):")
    for v in test_values:
        res = normalize_nulls(v)
        print(f"   Entrada: {repr(v):<18} -> Normalizado: {repr(res)}")

    # 4. Teste de Datas
    dates = ["1981-04-30", "15/03/1983", "1978-05", "1975", "c. 1982", "s/d"]
    print("\n4. Normalização de Datas:")
    for d in dates:
        dt, yr, exact = normalize_date(d)
        print(f"   Entrada: {repr(d):<15} -> Data: {repr(dt):<12} | Ano: {repr(yr):<6} | Exata: {exact}")


if __name__ == "__main__":
    run_demonstration()
