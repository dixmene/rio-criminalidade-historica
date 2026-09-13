"""
Script de Ingestão e Indexação do Catálogo Completo de Fontes (lista_fontes_pesquisa_rio.xlsx).
Importa 159 fontes bibliográficas, acadêmicas, jornalísticas e judiciais para o banco data/rio_historico.db.
Preserva as fontes existentes e seus vínculos com os 31 eventos históricos reais.
"""
import sys
import re
from pathlib import Path
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import SessionLocal, Base, engine
from app.models import Source
from src.utils.unicode_normalization import normalize_string_unicode


def infer_source_type(media_type: str, publisher: str, title: str) -> str:
    media = str(media_type).lower()
    pub = str(publisher).lower()
    tit = str(title).lower()

    if "youtube" in media or "vídeo" in media:
        return "historia_oral"
    if any(k in pub for k in ["stf", "mprj", "tribunal", "emerj", "depen", "judicial", "vara"]) or any(k in tit for k in ["adpf", "acórdão", "sentença", "ação penal"]):
        return "documento_judicial"
    if any(k in pub for k in ["alerj", "câmara", "senado", "governo", "isp", "ibge", "sepm"]) or any(k in tit for k in ["relatório final", "cpi", "boletim"]):
        return "oficial_relatorio"
    if any(k in pub for k in ["scielo", "ufrj", "uff", "fgv", "clio", "passagens", "redalyc", "ineac", "uerj", "fapesp", "ibccrim", "cesec"]) or "tese" in tit or "dissertação" in tit or "revisão de escopo" in tit:
        return "academico_artigo"
    if any(k in tit for k in ["condomínio do diabo", "a máquina e a revolta", "quatrocentos contra um", "livro"]):
        return "academico_livro"
    return "jornalismo_investigativo"


def extract_year(text: str):
    matches = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    if matches:
        valid = [int(m) for m in matches if 1900 <= int(m) <= 2026]
        if valid:
            return valid[-1]
    return None


def import_excel_sources(excel_path: str = "lista_fontes_pesquisa_rio.xlsx"):
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Planilha não encontrada em: {excel_path}")

    df = pd.read_excel(excel_path, sheet_name="Catálogo Completo de Fontes")
    print(f"-> Carregadas {len(df)} fontes da planilha '{excel_path}'")

    db = SessionLocal()
    try:
        existing_sources = db.query(Source).filter(Source.is_demo == False).all()
        existing_by_norm = {normalize_string_unicode(s.title): s for s in existing_sources}

        updated_count = 0
        created_count = 0

        for idx, row in df.iterrows():
            excel_id = str(row["ID"]).strip()
            title = str(row["Título da Fonte"]).strip()
            media = str(row["Tipo de Mídia"]).strip()
            publisher = str(row["Instituição / Veículo"]).strip()
            axis = str(row["Eixo Temático Principal"]).strip()
            ref_access = str(row["Link / Referência de Acesso"]).strip()

            title_norm = normalize_string_unicode(title)

            # Verificar se já existe por correspondência exata ou substring
            matched_src = existing_by_norm.get(title_norm)
            if not matched_src:
                for norm_k, s_obj in existing_by_norm.items():
                    if norm_k in title_norm or title_norm in norm_k:
                        matched_src = s_obj
                        break

            note_meta = f"ID: {excel_id} | Eixo Temático: {axis} | Tipo de Mídia: {media} | Ref: {ref_access}"

            if matched_src:
                # Atualizar / enriquecer metadados preservando a fonte existente
                if not matched_src.notes or excel_id not in matched_src.notes:
                    matched_src.notes = f"{matched_src.notes} | {note_meta}" if matched_src.notes else note_meta
                if not matched_src.archive_ref:
                    matched_src.archive_ref = f"{axis} ({excel_id})"
                updated_count += 1
            else:
                stype = infer_source_type(media, publisher, title)
                year = extract_year(title)
                author = publisher if not ("/" in publisher) else publisher.split("/")[0].strip()
                citation = f"{author.upper()}. {title}. {publisher}, {year or 's.d.'}."

                url_val = ref_access if ref_access.startswith("http") else None

                new_src = Source(
                    title=title,
                    citation=citation,
                    author=author,
                    publisher=publisher,
                    source_type=stype,
                    publication_year=year,
                    url=url_val,
                    archive_ref=f"{axis} ({excel_id})",
                    notes=note_meta,
                    is_demo=False
                )
                db.add(new_src)
                created_count += 1

        db.commit()
        total_real = db.query(Source).filter(Source.is_demo == False).count()
        print(f"\n================================================================================")
        print(f"   INGESTÃO CONCLUÍDA:")
        print(f"   - Fontes Existentes Atualizadas/Enriquecidas: {updated_count}")
        print(f"   - Novas Fontes Inseridas no Banco:           {created_count}")
        print(f"   - Total de Fontes Reais no Banco:            {total_real}")
        print(f"================================================================================\n")

    except Exception as e:
        db.rollback()
        print(f"[ERRO]: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    import_excel_sources()
