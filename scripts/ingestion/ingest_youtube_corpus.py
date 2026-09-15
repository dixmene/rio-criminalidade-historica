"""
Pipeline de Ingestão e Estruturação: YouTube -> Corpus Histórico Versionado.

Transforma episódios audiovisuais catalogados (ex: Playlist 'Histórias do Rio de Janeiro'
do canal Iconografia da História) em fontes historiográficas estruturadas, registrando
o grafo de derivação documental (SourceDerivation) e claims atômicas com timestamps.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Garante raiz no sys.path
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.database import SessionLocal, engine, Base
from app.models.source import Source
from app.models.associations import SourceDerivation, EventSource
from app.models.claim import Claim, ClaimSource
from app.models.event import Event
from app.models.person import Person
from app.models.organization import Organization
from app.models.region import Region
from src.normalization.rules import normalize_name, normalize_organization, normalize_temporal_expression


def sync_catalog_to_sources(catalog_path: str = "data/catalogo_playlist_youtube_historias_rio.json") -> int:
    """
    Sincroniza os vídeos do catálogo JSON para a tabela 'sources' do banco de dados,
    evitando duplicidades de URL.
    """
    path = Path(catalog_path)
    if not path.exists():
        print(f"[-] Arquivo de catálogo '{catalog_path}' não encontrado.")
        return 0

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    session = SessionLocal()
    channel = data.get("channel", "Iconografia da História")
    videos = data.get("videos", [])
    inserted_count = 0

    print(f"[*] Sincronizando {len(videos)} vídeos do catálogo '{data.get('playlist_title')}'...")

    for v in videos:
        url = v.get("url")
        title = v.get("title")
        v_id = v.get("videoId")

        # Verifica se já existe por URL ou título exato
        existing = session.query(Source).filter(
            (Source.url == url) | (Source.title == title)
        ).first()

        if not existing:
            src = Source(
                title=title,
                citation=f"{channel.upper()}. {title}. YouTube, Vídeo ID: {v_id}.",
                author=channel,
                publisher="YouTube",
                source_type="audiovisual_youtube",
                url=url,
                archive_ref=f"Canal {channel} · Playlist Histórias do Rio de Janeiro",
                notes=f"Episódio catalogado no Corpus Audiovisual (ID YT: {v_id}).",
                is_demo=False
            )
            session.add(src)
            inserted_count += 1

    session.commit()
    session.close()
    print(f"[+] Sincronização concluída: {inserted_count} novos vídeos inseridos em 'sources'.")
    return inserted_count


def import_video_extraction(extraction_json_path: str) -> Dict[str, Any]:
    """
    Importa uma ficha de extração epistemológica JSON gerada conforme o
    'protocolo_extracao_video.md', populando Claims, ClaimSource e SourceDerivation.
    """
    path = Path(extraction_json_path)
    if not path.exists():
        raise FileNotFoundError(f"Ficha de extração '{extraction_json_path}' não encontrada.")

    with open(path, "r", encoding="utf-8") as f:
        extraction = json.load(f)

    session = SessionLocal()
    try:
        source_meta = extraction.get("source_meta", {})
        video_url = source_meta.get("url")
        video_title = source_meta.get("title")

        # 1. Localiza ou cria a fonte do vídeo
        src_video = session.query(Source).filter(
            (Source.url == video_url) | (Source.title == video_title)
        ).first()

        if not src_video:
            src_video = Source(
                title=video_title,
                citation=f"{source_meta.get('channel', 'Iconografia da História')}. {video_title}. YouTube.",
                author=source_meta.get("channel", "Iconografia da História"),
                publisher="YouTube",
                source_type="audiovisual_youtube",
                url=video_url,
                is_demo=False
            )
            session.add(src_video)
            session.flush()

        # 2. Localiza ou associa Evento Relacionado
        event_rel = extraction.get("evento_relacionado", {})
        ev_id = event_rel.get("id_existente")
        event = None

        if ev_id:
            event = session.query(Event).filter(Event.id == ev_id).first()
        elif event_rel.get("titulo_sugerido"):
            # Tenta localizar por título aproximado
            event = session.query(Event).filter(
                Event.title.ilike(f"%{event_rel.get('titulo_sugerido')[:25]}%")
            ).first()

        # 3. Processa Árvore de Derivação (Genealogia Documental)
        # Se o vídeo cita obras consagradas (ex: Carlos Amorim), cria SourceDerivation
        for f_citada in source_meta.get("fontes_secundarias_citadas", []):
            nome_f = f_citada.get("nome", "")
            tipo_rel = f_citada.get("tipo_relacao", "reproduz")

            # Busca no banco de dados se já temos essa fonte raiz cadastrada
            parent_src = session.query(Source).filter(
                (Source.title.ilike(f"%{nome_f[:20]}%")) | (Source.author.ilike(f"%{nome_f[:20]}%"))
            ).first()

            if parent_src and parent_src.id != src_video.id:
                # Verifica se já existe vínculo
                existing_deriv = session.query(SourceDerivation).filter(
                    SourceDerivation.parent_source_id == parent_src.id,
                    SourceDerivation.derived_source_id == src_video.id
                ).first()

                if not existing_deriv:
                    deriv = SourceDerivation(
                        parent_source_id=parent_src.id,
                        derived_source_id=src_video.id,
                        derivation_type=tipo_rel,
                        is_independent=False,
                        notes=f"O roteiro do vídeo cita ou reproduz dados de '{parent_src.title}' ({parent_src.author})."
                    )
                    session.add(deriv)
                    print(f"  [+] Derivação registrada: '{src_video.title[:35]}' reproduz '{parent_src.title[:35]}'.")

        # 4. Ingestão das Claims Atômicas
        claims_data = extraction.get("claims", [])
        created_claims = 0

        for cd in claims_data:
            statement = cd.get("statement")
            if not statement or not event:
                continue

            claim = session.query(Claim).filter(
                Claim.event_id == event.id,
                Claim.statement == statement
            ).first()

            if not claim:
                claim = Claim(
                    event_id=event.id,
                    claim_type=cd.get("claim_type", "fato"),
                    statement=statement,
                    confidence_level=cd.get("confidence_level", "provavel"),
                    is_disputed=(cd.get("stance") in ["contesta", "matiza"]),
                    epistemological_notes=cd.get("epistemological_notes"),
                    is_demo=False
                )
                session.add(claim)
                session.flush()
                created_claims += 1

            # Cria o vínculo ClaimSource com timestamp
            cs = session.query(ClaimSource).filter(
                ClaimSource.claim_id == claim.id,
                ClaimSource.source_id == src_video.id
            ).first()

            if not cs:
                timestamp_str = cd.get("timestamp", "00:00")
                discurso = cd.get("tipo_discurso", "narracao_documental")
                cs = ClaimSource(
                    claim_id=claim.id,
                    source_id=src_video.id,
                    stance=cd.get("stance", "apoia"),
                    section=f"Timestamp {timestamp_str}",
                    excerpt=cd.get("excerpt", statement),
                    source_assessment=discurso,
                    assessment_notes=f"Tipo de discurso: {discurso}. Afirmação no vídeo.",
                    confidence_level=cd.get("confidence_level", "provavel")
                )
                session.add(cs)

        session.commit()
        print(f"[+] Ingestão da ficha '{extraction_json_path}' concluída com sucesso no evento '{event.title if event else 'Nenhum'}'!")
        return {
            "source_id": src_video.id,
            "event_id": event.id if event else None,
            "created_claims": created_claims
        }
    except Exception as e:
        session.rollback()
        print(f"[-] Erro ao importar extração: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline de Ingestão do Corpus YouTube")
    parser.add_argument("--sync-catalog", action="store_true", help="Sincroniza a lista de vídeos para 'sources'")
    parser.add_argument("--import-extraction", type=str, help="Caminho do arquivo JSON de extração a ser importado")
    args = parser.parse_args()

    if args.sync_catalog:
        sync_catalog_to_sources()
    elif args.import_extraction:
        import_video_extraction(args.import_extraction)
    else:
        # Modo padrão: sincroniza o catálogo
        sync_catalog_to_sources()
