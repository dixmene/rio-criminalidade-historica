#!/usr/bin/env python3
"""
Utilitário de Busca em Transcrições Audiovisuais
=================================================

Permite a pesquisadores buscar palavras-chave ou entidades nas transcrições
capturadas, exibindo o timestamp exato e o contexto de fala.
"""

import json
import argparse
from pathlib import Path

def search_transcript(video_id: str, query: str, transcripts_dir: Path):
    target = transcripts_dir / f"{video_id}.json"
    if not target.exists():
        print(f"Erro: Transcrição para '{video_id}' não encontrada em {transcripts_dir}.")
        return

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "")
    snippets = data.get("snippets", [])
    q = query.lower()

    print(f"=== Busca em: {title} ({video_id}) ===")
    print(f"Termo: '{query}' | Total de snippets: {len(snippets)}")
    print("-" * 50)

    matches = 0
    for idx, s in enumerate(snippets):
        text = s.get("text", "")
        if q in text.lower():
            matches += 1
            start = s.get("start", 0.0)
            mins = int(start // 60)
            secs = int(start % 60)
            # Contexto: pega snippet anterior e posterior se houver
            prev_txt = snippets[idx - 1]["text"] if idx > 0 else ""
            next_txt = snippets[idx + 1]["text"] if idx + 1 < len(snippets) else ""
            print(f"[{mins:02d}:{secs:02d}] (start: {start:.1f}s)")
            print(f"   Trecho: \"{text}\"")
            print(f"   Contexto: ... {prev_txt} [{text}] {next_txt} ...")
            print()

    print(f"[+] Total de ocorrências encontradas: {matches}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca em transcrições")
    parser.add_argument("video_id", type=str, help="ID do vídeo (ex: z-6FAKUvUUc)")
    parser.add_argument("query", type=str, help="Termo a buscar")
    parser.add_argument("--dir", type=str, default="data/raw/audiovisual/transcripts")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    search_transcript(args.video_id, args.query, project_root / args.dir)
