"""
Ponto de entrada unificado para Ingestão do Acervo Histórico Real do Rio de Janeiro.
Delega para o módulo integral scripts/ingestion/seed_full_historical_corpus.py
"""
import sys
from scripts.ingestion.seed_full_historical_corpus import seed_full_corpus

if __name__ == "__main__":
    seed_full_corpus()
