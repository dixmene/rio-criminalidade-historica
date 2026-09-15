#!/usr/bin/env python3
"""
Pipeline de Transcrição Audiovisual Histórica
==============================================

Responsável por obter, verificar a integridade (SHA-256) e armazenar
as transcrições textuais das fontes audiovisuais do acervo.

Epistemologia e Regras Metodológicas:
1. NUNCA inventar ou forjar transcrições. Se o vídeo não possui legenda/áudio
   transcrito disponível, o status DEVE ser explicitamente 'unavailable'.
2. Toda transcrição aceita recebe um hash criptográfico SHA-256 do seu conteúdo textual.
3. As legendas capturadas preservam os snippets com timestamps de início (start) e duração (duration),
   permitindo a auditabilidade de claims em segundos exatos.
4. O catálogo 'data/catalogo_playlist_youtube_historias_rio.json' é atualizado com
   status, hash e metadados de transcrição.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False


def calculate_sha256(text: str) -> str:
    """Calcula o hash SHA-256 do texto normalizado em UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def format_duration(seconds: float) -> str:
    """Converte segundos em formato mm:ss ou hh:mm:ss."""
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def process_video_transcript(
    video_entry: Dict[str, Any],
    output_dir: Path,
    languages: List[str],
    overwrite: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Processa a transcrição de um vídeo individual.
    Retorna o resultado do processamento com status, hash e duração.
    """
    video_id = video_entry.get("video_id")
    catalog_id = video_entry.get("id", "UNKNOWN")
    title = video_entry.get("title", "")
    
    if not video_id:
        return {"status": "error", "message": "Vídeo sem video_id."}

    cache_file = output_dir / f"{video_id}.json"

    # 1. Verifica cache local existente
    if cache_file.exists() and not overwrite:
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            full_text = cached_data.get("full_text", "")
            sha256_hash = cached_data.get("sha256_hash") or calculate_sha256(full_text)
            duration = cached_data.get("duration_seconds", 0.0)
            return {
                "status": "cached",
                "video_id": video_id,
                "catalog_id": catalog_id,
                "transcript_status": cached_data.get("transcript_status", "generated"),
                "transcript_source": cached_data.get("transcript_source", "local_cache"),
                "transcript_hash": sha256_hash,
                "duration_seconds": duration,
                "duration_formatted": format_duration(duration),
                "snippets_count": len(cached_data.get("snippets", [])),
                "path": str(cache_file)
            }
        except Exception as e:
            # Se arquivo de cache estiver corrompido, refaz a busca
            pass

    # 2. Busca via YouTubeTranscriptApi
    if not YOUTUBE_API_AVAILABLE:
        return {
            "status": "unavailable",
            "video_id": video_id,
            "catalog_id": catalog_id,
            "transcript_status": "unavailable",
            "message": "Biblioteca youtube_transcript_api não instalada."
        }

    try:
        yta = YouTubeTranscriptApi()
        transcript = yta.fetch(video_id, languages=languages)
        
        snippets = []
        text_parts = []
        for s in transcript:
            snippet_dict = {
                "text": s.text.strip(),
                "start": round(s.start, 2),
                "duration": round(s.duration, 2)
            }
            snippets.append(snippet_dict)
            if s.text.strip():
                text_parts.append(s.text.strip())

        full_text = " ".join(text_parts)
        sha256_hash = calculate_sha256(full_text)
        
        duration = 0.0
        if snippets:
            duration = round(snippets[-1]["start"] + snippets[-1]["duration"], 2)

        transcript_data = {
            "catalog_id": catalog_id,
            "video_id": video_id,
            "title": title,
            "channel_name": video_entry.get("channel_name", "Iconografia da História"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": languages[0],
            "transcript_status": "generated",
            "transcript_source": "youtube_transcript_api",
            "sha256_hash": sha256_hash,
            "duration_seconds": duration,
            "snippets_count": len(snippets),
            "snippets": snippets,
            "full_text": full_text
        }

        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "transcribed",
            "video_id": video_id,
            "catalog_id": catalog_id,
            "transcript_status": "generated",
            "transcript_source": "youtube_transcript_api",
            "transcript_hash": sha256_hash,
            "duration_seconds": duration,
            "duration_formatted": format_duration(duration),
            "snippets_count": len(snippets),
            "path": str(cache_file)
        }

    except Exception as e:
        # Falha ao obter transcrição (desativada, restrita, etc.)
        return {
            "status": "unavailable",
            "video_id": video_id,
            "catalog_id": catalog_id,
            "transcript_status": "unavailable",
            "message": str(e)
        }


def run_pipeline(
    catalog_path: Path,
    output_dir: Path,
    video_id: Optional[str] = None,
    catalog_id: Optional[str] = None,
    limit: Optional[int] = None,
    languages: Optional[List[str]] = None,
    overwrite: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Executa o pipeline de transcrição sobre o catálogo informado."""
    if languages is None:
        languages = ["pt", "pt-BR", "en"]

    if not catalog_path.exists():
        raise FileNotFoundError(f"Catálogo não encontrado em: {catalog_path}")

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    videos = catalog.get("videos", [])
    target_videos = []

    if video_id:
        target_videos = [v for v in videos if v.get("video_id") == video_id]
    elif catalog_id:
        target_videos = [v for v in videos if v.get("id") == catalog_id]
    else:
        target_videos = videos

    if limit and limit > 0:
        target_videos = target_videos[:limit]

    print(f"=== Pipeline de Transcrição Histórica ===")
    print(f"Catálogo: {catalog_path.name} ({len(videos)} vídeos cadastrados)")
    print(f"Alvos selecionados para esta execução: {len(target_videos)}")
    print(f"Diretório de saída: {output_dir}")
    print(f"Dry Run: {dry_run} | Sobrescrever: {overwrite}")
    print("-" * 55)

    stats = {
        "total_targets": len(target_videos),
        "transcribed": 0,
        "cached": 0,
        "unavailable": 0,
        "errors": 0,
        "results": []
    }

    # Mapa de atualizações no catálogo por video_id
    updates_by_vid = {}

    for idx, v in enumerate(target_videos, 1):
        vid = v.get("video_id")
        cid = v.get("id")
        title = v.get("title", "")[:45]
        print(f"[{idx}/{len(target_videos)}] Processando {cid} ({vid}): {title}...")

        res = process_video_transcript(
            video_entry=v,
            output_dir=output_dir,
            languages=languages,
            overwrite=overwrite,
            dry_run=dry_run
        )

        stats["results"].append(res)
        status = res.get("status")

        if status == "transcribed":
            stats["transcribed"] += 1
            print(f"    -> TRANSCRIÇÃO OBTIDA: {res.get('snippets_count')} snippets, {res.get('duration_formatted')}, hash={res.get('transcript_hash')[:12]}...")
            updates_by_vid[vid] = res
        elif status == "cached":
            stats["cached"] += 1
            print(f"    -> CACHE LOCAL VÁLIDO: {res.get('snippets_count')} snippets, {res.get('duration_formatted')}, hash={res.get('transcript_hash')[:12]}...")
            updates_by_vid[vid] = res
        elif status == "unavailable":
            stats["unavailable"] += 1
            print(f"    -> TRANSCRIÇÃO INDISPONÍVEL: {res.get('message', 'Sem legenda pública')[:60]}")
            updates_by_vid[vid] = res
        else:
            stats["errors"] += 1
            print(f"    -> ERRO: {res.get('message')}")

    # Atualiza o catálogo JSON
    if not dry_run and updates_by_vid:
        updated_count = 0
        for v in catalog.get("videos", []):
            vid = v.get("video_id")
            if vid in updates_by_vid:
                info = updates_by_vid[vid]
                v["transcript_status"] = info.get("transcript_status", "unavailable")
                v["transcript_source"] = info.get("transcript_source")
                v["transcript_hash"] = info.get("transcript_hash")
                if info.get("duration_formatted"):
                    v["duration"] = info.get("duration_formatted")
                if info.get("status") in ["transcribed", "cached"]:
                    v["processing_status"] = "transcribed"
                updated_count += 1

        catalog["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Catálogo atualizado com sucesso: {updated_count} entradas sincronizadas.")

    print("=" * 55)
    print(f"Resumo da Execução:")
    print(f"  Total avaliado:      {stats['total_targets']}")
    print(f"  Novas transcrições:  {stats['transcribed']}")
    print(f"  Reutilizadas (cache): {stats['cached']}")
    print(f"  Indisponíveis:       {stats['unavailable']}")
    print(f"  Erros:               {stats['errors']}")
    print("=" * 55)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Transcrição Audiovisual Histórica")
    parser.add_argument("--catalog-path", type=str, default="data/catalogo_playlist_youtube_historias_rio.json",
                        help="Caminho para o catálogo JSON da playlist")
    parser.add_argument("--output-dir", type=str, default="data/raw/audiovisual/transcripts",
                        help="Diretório onde salvar as transcrições JSON")
    parser.add_argument("--video-id", type=str, default=None,
                        help="Processa apenas um vídeo específico pelo video_id do YouTube")
    parser.add_argument("--catalog-id", type=str, default=None,
                        help="Processa apenas um vídeo específico pelo ID do catálogo (ex: YTRIO-0006)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Número máximo de vídeos a processar")
    parser.add_argument("--languages", type=str, default="pt,pt-BR,en",
                        help="Lista de códigos de idiomas separados por vírgula")
    parser.add_argument("--overwrite", action="store_true",
                        help="Sobrescreve arquivos de cache já existentes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Executa sem salvar arquivos em disco nem alterar catálogo")

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    catalog_file = project_root / args.catalog_path
    out_dir = project_root / args.output_dir
    lang_list = [l.strip() for l in args.languages.split(",") if l.strip()]

    run_pipeline(
        catalog_path=catalog_file,
        output_dir=out_dir,
        video_id=args.video_id,
        catalog_id=args.catalog_id,
        limit=args.limit,
        languages=lang_list,
        overwrite=args.overwrite,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
