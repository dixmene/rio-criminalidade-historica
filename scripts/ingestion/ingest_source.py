"""
Script de Ingestão de Fontes e Documentos Brutos.
Pipeline: URL / Arquivo -> Download / Cópia -> SHA-256 Hash -> Armazenamento em data/raw/ -> Registro de Metadados
"""
import sys
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict
import requests

from config.settings import settings

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def calculate_sha256(file_path: Path) -> str:
    """Calcula o hash criptográfico SHA-256 para integridade e auditoria."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ingest_file(
    source_path: Path,
    category: str = "outros",
    title: Optional[str] = None,
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    url: Optional[str] = None,
) -> Dict:
    """
    Registra um documento local na estrutura data/raw/ e gera metadados de auditoria.
    """
    target_dir = settings.DATA_RAW_DIR / category
    target_dir.mkdir(parents=True, exist_ok=True)

    dest_file = target_dir / source_path.name
    shutil.copy2(source_path, dest_file)

    file_hash = calculate_sha256(dest_file)

    metadata = {
        "title": title or source_path.stem,
        "filename": source_path.name,
        "category": category,
        "author": author,
        "publisher": publisher,
        "url": url,
        "sha256": file_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "file_size_bytes": dest_file.stat().st_size,
    }

    meta_file = target_dir / f"{source_path.stem}_meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] Documento ingerido com sucesso: {dest_file.name}")
    print(f"     SHA-256: {file_hash}")
    return metadata


def ingest_url(
    url: str,
    category: str = "jornalismo",
    custom_filename: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict:
    """
    Baixa uma fonte remota e registra com metadados de proveniência.
    """
    target_dir = settings.DATA_RAW_DIR / category
    target_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=30, headers={"User-Agent": "RioCriminalidadeHistoricaResearch/1.0"})
    response.raise_for_status()

    filename = custom_filename or url.split("/")[-1].split("?")[0] or "source_download.html"
    dest_file = target_dir / filename

    with open(dest_file, "wb") as f:
        f.write(response.content)

    file_hash = calculate_sha256(dest_file)

    metadata = {
        "title": title or filename,
        "filename": filename,
        "category": category,
        "url": url,
        "sha256": file_hash,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "file_size_bytes": len(response.content),
    }

    meta_file = target_dir / f"{Path(filename).stem}_meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] URL ingerida com sucesso: {filename}")
    print(f"     SHA-256: {file_hash}")
    return metadata


if __name__ == "__main__":
    print("Módulo de Ingestão de Fontes pronto para integração.")
