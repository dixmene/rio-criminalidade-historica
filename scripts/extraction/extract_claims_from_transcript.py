#!/usr/bin/env python3
"""
Pipeline de Extração de Claims e Validação Anti-Alucinação
===========================================================

Garante que nenhuma afirmação histórica seja ingerida no banco de dados sem
auditoria de autenticidade documental.

Critérios Verificados:
1. Fidelidade Textual: Excertos devem ser validados contra a transcrição oficial SHA-256.
2. Limites Temporais: Timestamps devem existir dentro da duração do vídeo.
3. Taxonomia Historiográfica: Classificação estrita de discurso e tipo de claim.
4. Relatório de Integridade: Gera 'reports/validation_report.json'.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Adiciona a raiz do projeto ao path para importar módulos da aplicação
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.claim_validator import ClaimValidator
from app.services.genealogy_service import GenealogyService


def load_transcript_for_video(transcripts_dir: Path, video_id: str) -> Optional[Dict[str, Any]]:
    """Carrega o arquivo de transcrição correspondente ao video_id."""
    target = transcripts_dir / f"{video_id}.json"
    if not target.exists():
        return None
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def process_extraction_file(
    extraction_path: Path,
    transcripts_dir: Path,
    strict: bool = False
) -> Dict[str, Any]:
    """Valida um arquivo de extração individual e suas claims contra a transcrição."""
    with open(extraction_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    source_meta = data.get("source_meta", {})
    video_id = source_meta.get("video_id")
    title = source_meta.get("title", extraction_path.stem)
    claims = data.get("claims", [])

    transcript_data = load_transcript_for_video(transcripts_dir, video_id) if video_id else None
    transcript_text = transcript_data.get("full_text") if transcript_data else None
    duration_seconds = transcript_data.get("duration_seconds") if transcript_data else None

    result = {
        "file": str(extraction_path.name),
        "video_id": video_id,
        "title": title,
        "has_transcript": transcript_data is not None,
        "transcript_hash": transcript_data.get("sha256_hash") if transcript_data else None,
        "total_claims": len(claims),
        "accepted_claims": [],
        "rejected_claims": [],
        "warnings": []
    }

    if not transcript_data:
        msg = f"Aviso: Transcrição não encontrada em cache para video_id '{video_id}'."
        result["warnings"].append(msg)
        if strict:
            for idx, c in enumerate(claims):
                result["rejected_claims"].append({
                    "index": idx,
                    "statement": c.get("statement", ""),
                    "errors": ["Transcrição não disponível em modo estrito."],
                    "warnings": []
                })
            return result

    for idx, c in enumerate(claims):
        validation = ClaimValidator.validate_claim(
            claim_data=c,
            transcript_text=transcript_text,
            duration_seconds=duration_seconds,
            require_transcript=strict
        )

        item = {
            "index": idx,
            "statement": c.get("statement", ""),
            "claim_type": c.get("claim_type", "fato"),
            "timestamp": c.get("timestamp"),
            "tipo_discurso": c.get("tipo_discurso"),
            "excerpt": c.get("excerpt", ""),
            "confidence_level": c.get("confidence_level", "provavel"),
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "excerpt_validation": validation.get("excerpt_validation"),
            "timestamp_validation": validation.get("timestamp_validation")
        }

        if validation["is_valid"]:
            result["accepted_claims"].append(item)
        else:
            result["rejected_claims"].append(item)

        if validation["warnings"]:
            result["warnings"].extend([f"Claim #{idx}: {w}" for w in validation["warnings"]])

    return result


def run_extractions_pipeline(
    extractions_dir: Path,
    transcripts_dir: Path,
    report_output: Path,
    single_file: Optional[Path] = None,
    strict: bool = False,
    import_to_db: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Executa a validação em lote e gera o relatório formal de verificação."""
    targets = []
    if single_file:
        if single_file.exists():
            targets.append(single_file)
        else:
            raise FileNotFoundError(f"Arquivo não encontrado: {single_file}")
    else:
        targets = list(extractions_dir.glob("*.json"))

    print("=== Pipeline de Extração e Validação Anti-Alucinação ===")
    print(f"Arquivos a validar: {len(targets)}")
    print(f"Modo Estrito: {strict} | Importar para BD: {import_to_db} | Dry Run: {dry_run}")
    print("-" * 60)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files_analyzed": len(targets),
        "total_claims_evaluated": 0,
        "accepted_claims_count": 0,
        "rejected_claims_count": 0,
        "files_results": []
    }

    for fpath in targets:
        print(f"Analisando {fpath.name}...")
        file_res = process_extraction_file(fpath, transcripts_dir, strict=strict)
        summary["files_results"].append(file_res)
        summary["total_claims_evaluated"] += file_res["total_claims"]
        summary["accepted_claims_count"] += len(file_res["accepted_claims"])
        summary["rejected_claims_count"] += len(file_res["rejected_claims"])

        print(f"  Total Claims: {file_res['total_claims']} | Aceitas: {len(file_res['accepted_claims'])} | Rejeitadas: {len(file_res['rejected_claims'])}")
        for rej in file_res["rejected_claims"]:
            print(f"    [X] REJEITADA: {rej['statement'][:40]}... -> Erros: {rej['errors']}")
        for warn in file_res["warnings"]:
            print(f"    [!] Alerta: {warn}")

    # Salva relatório de validação
    report_output.parent.mkdir(parents=True, exist_ok=True)
    with open(report_output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("-" * 60)
    print(f"[+] Relatório de validação salvo em: {report_output}")
    print(f"Resumo Final: {summary['accepted_claims_count']} aceitas, {summary['rejected_claims_count']} rejeitadas de {summary['total_claims_evaluated']} claims.")
    print("=" * 60)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Extração e Validação Anti-Alucinação")
    parser.add_argument("--extractions-dir", type=str, default="data/raw/audiovisual",
                        help="Diretório contendo arquivos de extração de vídeo")
    parser.add_argument("--transcripts-dir", type=str, default="data/raw/audiovisual/transcripts",
                        help="Diretório de transcrições em cache")
    parser.add_argument("--report-file", type=str, default="reports/validation_report.json",
                        help="Caminho para o relatório JSON de saída")
    parser.add_argument("--file", type=str, default=None,
                        help="Valida um único arquivo de extração específico")
    parser.add_argument("--strict", action="store_true",
                        help="Exige que a transcrição exista e rejeita se não houver")
    parser.add_argument("--dry-run", action="store_true",
                        help="Apenas valida sem modificar o banco de dados")

    args = parser.parse_args()

    ext_dir = PROJECT_ROOT / args.extractions_dir
    trx_dir = PROJECT_ROOT / args.transcripts_dir
    rep_file = PROJECT_ROOT / args.report_file
    single = (PROJECT_ROOT / args.file) if args.file else None

    run_extractions_pipeline(
        extractions_dir=ext_dir,
        transcripts_dir=trx_dir,
        report_output=rep_file,
        single_file=single,
        strict=args.strict,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
