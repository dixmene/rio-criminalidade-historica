# -*- coding: utf-8 -*-
"""
Módulo de Exploração do Acervo Audiovisual
=========================================

Atlas Histórico da Criminalidade no Rio de Janeiro (1950–2026)
Componente: Explorador do Corpus Audiovisual (YouTube - Iconografia da História)

Funcionalidades:
- Carregamento resiliente do catálogo de 100 documentários (JSON).
- Resumo analítico do acervo: total de horas, cobertura de personagens históricos, facções e territórios.
- Busca rápida unificada por nome de personagem, facção, território, favela e termos de transcrição.
- Filtros por status de transcrição, matriz de criminalidade, território e duração.
- Renderização visual em cartões editoriais com miniaturas, links diretos para o YouTube, badges de verificação e hashes SHA-256.
- Visualizador de transcrições com busca interna de falas, timestamps clicáveis e gerador de citação formal ABNT.
"""

import os
import re
import json
import math
import unicodedata
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import streamlit as st

# =============================================================================
# CONSTANTES & TAXONOMIA DE EXTRAÇÃO ENTITÁRIA
# =============================================================================

DEFAULT_CATALOG_RELPATH = "data/catalogo_playlist_youtube_historias_rio.json"
DEFAULT_TRANSCRIPTS_RELDIR = "data/raw/audiovisual/transcripts"

HISTORICAL_CHARACTERS_TAXONOMY: List[Tuple[str, List[str]]] = [
    ("Brasileirinho", ["brasileirinho"]),
    ("Jorge Luiz de Acari", ["jorge luiz de acari", "jorge luiz do acari", "jorge negao", "jorge negão"]),
    ("Bem-Te-Vi", ["bem-te-vi", "bem te vi"]),
    ("Madame Satã", ["madame sata", "madame satã"]),
    ("Uê", [" uê", " ué", " ue ", "traição de uê", "a história de uê"]),
    ("Elias Maluco", ["elias maluco"]),
    ("Adriano da Nóbrega", ["adriano da nobrega", "adriano da nóbrega"]),
    ("Johnny", ["johnny"]),
    ("Fernandinho Beira-Mar", ["beira-mar", "beira mar"]),
    ("Castor de Andrade", ["castor de andrade"]),
    ("Escadinha", ["escadinha"]),
    ("Marcinho VP", ["marcinho vp"]),
    ("Nem da Rocinha", ["nem da rocinha"]),
    ("Luciano Pezão", ["luciano pezao", "luciano pezão"]),
    ("Márcio Matemático", ["marcio matematico", "márcio matemático"]),
    ("Febrônio", ["febronio", "febrônio"]),
    ("Guarabú", ["guarabu", "guarabú"]),
    ("Milton Le Cocq", ["le cocq", "lecocq"]),
    ("Nazareth Cerqueira", ["nazareth cerqueira"]),
    ("Toninho Turco", ["toninho turco"]),
    ("Perpétuo de Freitas", ["perpetuo de freitas", "perpétuo de freitas"]),
    ("Tenório Cavalcanti", ["tenorio cavalcanti", "tenório cavalcanti"]),
    ("Tião Medonho", ["tiao medonho", "tião medonho"]),
    ("Zé do Bigode", ["ze do bigode", "zé do bigode"]),
    ("Fat Family & My Thor", ["fat family", "my thor"]),
    ("Flávia Fróes", ["flavia froes", "flávia fróes"]),
    ("Professor do CV", ["professor do cv", "o professor"]),
    ("Sandra Sapatão", ["sandra sapatao", "sandra sapatão"]),
    ("Lili Carabina", ["lili carabina"]),
    ("Zé do Queijo", ["ze do queijo", "zé do queijo"]),
    ("Carlinha do Rodo", ["carlinha do rodo"]),
    ("Hélio Vigio", ["helio vigio", "hélio vigio"]),
    ("Lúcio Flávio", ["lucio flavio", "lúcio flávio"]),
    ("Mariel Mariscott", ["mariel mariscott"]),
    ("Raimundinho", ["raimundinho"]),
    ("Carlinhos Três Pontes", ["carlinhos tres pontes", "carlinhos três pontes"]),
    ("Ecko", ["ecko"]),
    ("Zinho", ["zinho"]),
    ("Tandera", ["tandera"]),
    ("Cara de Cavalo", ["cara de cavalo"]),
    ("Dager", ["dager"]),
    ("Dona Zika", ["dona zika", "aunt zika"]),
    ("Rogério Lemgruber", ["rogerio lemgruber", "rogério lemgruber"]),
    ("Aída Curi", ["aida curi", "aída curi"]),
    ("Serginho Ratazana", ["serginho ratazana"]),
    ("Gangan", ["gangan"]),
    ("Tio Patinhas", ["tio patinhas"]),
    ("Maninho", ["maninho"]),
    ("Batoré", ["batore", "batoré"]),
    ("Tim Lopes", ["tim lopes"]),
    ("Delegado Sivuca", ["sivuca"]),
    ("Denis da Rocinha", ["denis da rocinha"]),
    ("Cy de Acari", ["cy de acari"]),
    ("Gregório Fortunato", ["gregorio fortunato", "gregório fortunato"]),
    ("Mães de Acari", ["maes de acari", "mães de acari"]),
    ("Rambo da Rocinha", ["rambo"]),
    ("João Hélio", ["joao helio", "joão hélio"]),
    ("Robinho Pinga", ["robinho pinga"]),
    ("Salamone", ["salamone"]),
    ("Linho", ["linho"]),
    ("Ronnie Lessa", ["ronnie lessa"]),
    ("Vovô Paulo", ["vovo paulo", "vovô paulo"]),
    ("Felipe Curi", ["felipe curi"]),
    ("Marcelinho Niterói", ["marcelinho niteroi", "marcelinho niterói"]),
    ("Peixão", ["peixao", "peixão"]),
    ("Orlando Curicica", ["orlando curicica"]),
    ("Mineirinho", ["mineirinho"]),
]

FACTIONS_TAXONOMY: List[Tuple[str, str]] = [
    ("Comando Vermelho (CV)", r"\b(comando vermelho|cv|beira-mar|beira mar|marcinho vp|elias maluco|rogerio lemgruber|escadinha|ze do bigode|serginho ratazana|brasileirinho|bem-te-vi|denis da rocinha|marcelinho niteroi|luciano pezao|fat family|my thor)\b"),
    ("Milícias & Paramilitares", r"\b(militia|milicia|milicias|militias|justice league|liga da justica|liga da justiça|adriano da nobrega|adriano da nóbrega|ecko|zinho|tandera|carlinhos tres pontes|carlinhos três pontes|orlando curicica|killer consortium|consorcio de matadores|consórcio de matadores|ronnie lessa|narco-mili)\b"),
    ("Terceiro Comando (TCP)", r"\b(tcp|terceiro comando|marcio matematico|márcio matemático|peixao|peixão|robinho pinga|narco-pentecostal|narcopentecostalismo)\b"),
    ("Amigos dos Amigos (ADA)", r"\b(ada|amigos dos amigos|linho|gangan|nem da rocinha)\b|(\bue\b|\buê\b|\bué\b)"),
    ("Jogo do Bicho & Contravenção", r"\b(jogo do bicho|castor de andrade|maninho|tio patinhas|salamone|bookmaker|bookie|bicheiro)\b"),
    ("Esquadrões da Morte & Vigilantismo", r"\b(le cocq|lecocq|scuderie|esquadrao da morte|esquadrão da morte|cara de cavalo|mariel mariscott|white hand|mao branca|mão branca|cavalos corredores|running horses|sivuca|vigilante)\b"),
    ("Aparelho Policial & Investigação", r"\b(nazareth cerqueira|helio vigio|hélio vigio|perpetuo de freitas|perpétuo de freitas|felipe curi|delegado|police chief|batoré|batore)\b"),
]

TERRITORIES_TAXONOMY: List[Tuple[str, List[str]]] = [
    ("Rocinha", ["rocinha", "brasileirinho", "bem-te-vi", "nem da rocinha", "denis da rocinha", "rambo"]),
    ("Acari", ["acari", "jorge luiz de acari", "cy de acari", "maes de acari", "mães de acari"]),
    ("Complexo do Alemão / Penha", ["alemao", "alemão", "complexo", "luciano pezao", "luciano pezão", "penha", "fera da penha"]),
    ("Maré & Vigário Geral", ["vigario geral", "vigário geral", "cavalos corredores", "running horses", "mare", "maré"]),
    ("Cidade de Deus", ["cidade de deus", "city of god"]),
    ("Santa Marta", ["santa marta", "dager"]),
    ("Bangu & Gericinó", ["bangu 1", "bangu"]),
    ("Ilha Grande", ["ilha grande", "caldeirao do diabo", "caldeirão do diabo"]),
    ("Zona Oeste (Campo Grande / Curicica)", ["tres pontes", "três pontes", "curicica", "campo grande", "rio das pedras", "gardenia", "gardênia"]),
    ("Centro & Zona Sul", ["copacabana", "vovo paulo", "vovô paulo", "aida curi", "aída curi", "playboys", "lapa", "madame sata", "madame satã", "piedade"]),
]


# =============================================================================
# FUNÇÕES DE NORMALIZAÇÃO E RESOLUÇÃO DE CAMINHOS
# =============================================================================

def normalize_string(text: str) -> str:
    """Normaliza texto removendo acentos e convertendo para minúsculas."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def parse_duration_to_seconds(duration_str: Optional[str]) -> int:
    """Converte duração no formato 'MM:SS' ou 'HH:MM:SS' em segundos inteiros."""
    if not duration_str or not isinstance(duration_str, str):
        return 0
    parts = duration_str.strip().split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except (ValueError, TypeError):
        return 0
    return 0


def format_seconds_display(total_seconds: int) -> str:
    """Formata segundos em representação legível (HHh MMm ou MM:SS)."""
    if total_seconds <= 0:
        return "S/D"
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hrs > 0:
        return f"{hrs}h {mins:02d}m"
    return f"{mins:02d}:{secs:02d}"


def resolve_project_file(rel_path: str) -> Optional[Path]:
    """Resolve caminhos relativos ao projeto suportando múltiplos diretórios de trabalho."""
    cwd = Path.cwd()
    candidates = [
        Path(rel_path),
        cwd / rel_path,
        Path(__file__).resolve().parent / rel_path,
        Path(__file__).resolve().parents[1] / rel_path,
        Path(__file__).resolve().parents[2] / rel_path,
        Path(__file__).resolve().parents[3] / rel_path,
    ]
    for p in candidates:
        try:
            if p.exists():
                return p.resolve()
        except Exception:
            continue
    return None


# =============================================================================
# CARREGAMENTO DE DADOS COM TRATAMENTO GRACIOSO DE ERROS
# =============================================================================

@st.cache_data(show_spinner=False)
def load_video_catalog(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carrega o catálogo oficial da playlist de documentários do YouTube.
    Trata exceções graciosamente e garante estrutura íntegra de retorno.
    """
    target_path = None
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            target_path = p.resolve()

    if not target_path:
        target_path = resolve_project_file(DEFAULT_CATALOG_RELPATH)

    default_structure: Dict[str, Any] = {
        "corpus_id": "CORPUS-AV-YTRIO-01",
        "playlist_title": "Histórias do Rio de Janeiro",
        "channel_name": "Iconografia da História",
        "total_cataloged": 0,
        "videos": [],
        "_source_path": None,
        "_error": None
    }

    if not target_path or not target_path.exists():
        default_structure["_error"] = f"Arquivo do catálogo não localizado: {DEFAULT_CATALOG_RELPATH}"
        return default_structure

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["_source_path"] = str(target_path)
            return data
    except json.JSONDecodeError as jde:
        default_structure["_error"] = f"Erro de sintaxe JSON no catálogo ({target_path}): {jde}"
        return default_structure
    except Exception as e:
        default_structure["_error"] = f"Erro ao abrir catálogo ({target_path}): {e}"
        return default_structure


@st.cache_data(show_spinner=False)
def load_transcript_file(video_id: str, custom_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Carrega o arquivo de transcrição correspondente ao video_id."""
    if not video_id:
        return None

    filename = f"{video_id}.json"
    dir_path = None

    if custom_dir:
        p = Path(custom_dir)
        if p.exists():
            dir_path = p.resolve()

    if not dir_path:
        resolved = resolve_project_file(DEFAULT_TRANSCRIPTS_RELDIR)
        if resolved and resolved.exists():
            dir_path = resolved

    if not dir_path:
        return None

    target = dir_path / filename
    if not target.exists():
        return None

    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def get_available_transcripts_map() -> Dict[str, Dict[str, Any]]:
    """Mapeia todas as transcrições brutas disponíveis no repositório."""
    transcripts_dir = resolve_project_file(DEFAULT_TRANSCRIPTS_RELDIR)
    results: Dict[str, Dict[str, Any]] = {}
    if not transcripts_dir or not transcripts_dir.exists():
        return results

    try:
        for json_file in transcripts_dir.glob("*.json"):
            video_id = json_file.stem
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results[video_id] = {
                        "video_id": video_id,
                        "duration_seconds": data.get("duration_seconds", 0),
                        "snippets_count": len(data.get("snippets", [])),
                        "sha256_hash": data.get("sha256_hash") or data.get("transcript_hash"),
                        "title": data.get("title", ""),
                        "snippets": data.get("snippets", []),
                    }
            except Exception:
                continue
    except Exception:
        pass
    return results


# =============================================================================
# ENRIQUECIMENTO E TAGGING DOS DOCUMENTÁRIOS
# =============================================================================

def enrich_video_entry(video: Dict[str, Any], transcripts_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enriquece cada registro de documentário com:
    - Personagens identificados
    - Facções e matrizes
    - Territórios
    - Duração consolidada
    - Citação formal ABNT
    - Status auditado de transcrição
    """
    vid_id = video.get("video_id")
    raw_title = video.get("title") or ""
    norm_title = normalize_string(raw_title)

    # Identificação de Personagens
    detected_chars = []
    for char_name, aliases in HISTORICAL_CHARACTERS_TAXONOMY:
        for alias in aliases:
            norm_alias = normalize_string(alias)
            if f" {norm_alias} " in f" {norm_title} " or norm_title.startswith(f"{norm_alias} ") or norm_title.endswith(f" {norm_alias}"):
                detected_chars.append(char_name)
                break
            elif norm_alias in norm_title and len(norm_alias) >= 5:
                detected_chars.append(char_name)
                break

    # Identificação de Facções
    detected_factions = []
    for fac_name, fac_regex in FACTIONS_TAXONOMY:
        if re.search(fac_regex, norm_title, flags=re.IGNORECASE):
            detected_factions.append(fac_name)

    # Identificação de Territórios
    detected_territories = []
    for terr_name, aliases in TERRITORIES_TAXONOMY:
        for alias in aliases:
            norm_alias = normalize_string(alias)
            if norm_alias in norm_title:
                detected_territories.append(terr_name)
                break

    # Resolução de Duração
    dur_str = video.get("duration")
    dur_seconds = parse_duration_to_seconds(dur_str)

    # Checagem na base de transcrições locais se a duração não estiver informada
    trans_info = transcripts_map.get(vid_id)
    if dur_seconds <= 0 and trans_info:
        dur_seconds = int(trans_info.get("duration_seconds", 0))
        if dur_seconds > 0 and not dur_str:
            mins = dur_seconds // 60
            secs = dur_seconds % 60
            dur_str = f"{mins:02d}:{secs:02d}"

    # Balde de Duração
    if dur_seconds > 0:
        if dur_seconds < 12 * 60:
            dur_bucket = "Curta (<12 min)"
        elif dur_seconds <= 18 * 60:
            dur_bucket = "Média (12–18 min)"
        else:
            dur_bucket = "Longa (>18 min)"
    else:
        dur_bucket = "Duração não aferida"

    # Status de Transcrição
    has_hash = bool(video.get("transcript_hash") or (trans_info and trans_info.get("sha256_hash")))
    is_transcribed = video.get("transcript_status") in ("generated", "exact", "manually_verified") or bool(trans_info)
    hash_val = video.get("transcript_hash") or (trans_info.get("sha256_hash") if trans_info else None)

    # Citação ABNT
    channel = video.get("channel_name") or "Iconografia da História"
    url = video.get("youtube_url") or f"https://www.youtube.com/watch?v={vid_id}"
    hash_txt = f"Hash de custódia SHA-256: {hash_val}." if hash_val else "Registro em fase de transcrição."
    abnt_citation = (
        f"{channel.upper()}. {raw_title}. YouTube, 2024–2026. "
        f"Disponível em: <{url}>. Acesso em: 15 set. 2026. {hash_txt}"
    )

    enriched = dict(video)
    enriched.update({
        "detected_characters": detected_chars,
        "detected_factions": detected_factions,
        "detected_territories": detected_territories,
        "duration_seconds": dur_seconds,
        "duration_display": dur_str or "S/D",
        "duration_bucket": dur_bucket,
        "is_transcribed": is_transcribed,
        "has_hash": has_hash,
        "sha256_hash": hash_val,
        "abnt_citation": abnt_citation,
        "thumbnail_url": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg" if vid_id else None,
        "has_local_snippets": bool(trans_info and trans_info.get("snippets")),
        "snippets_count": trans_info.get("snippets_count", 0) if trans_info else 0,
    })
    return enriched


# =============================================================================
# RESUMO ANALÍTICO DO ACERVO AUDIOVISUAL
# =============================================================================

def get_video_corpus_analytics(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula indicadores quantitativos e qualitativos sobre o corpus de 100 documentários:
    - Total de horas documentadas e estimativa de acervo
    - Cobertura de personagens históricos
    - Facções e matrizes criminais representadas
    - Territórios e favelas mapeadas
    - Índice de custódia criptográfica
    """
    total_vids = len(videos)
    if total_vids == 0:
        return {
            "total_videos": 0,
            "total_transcribed": 0,
            "total_pending": 0,
            "documented_seconds": 0,
            "documented_hours_str": "0h 00m",
            "estimated_total_hours_str": "0h",
            "characters_coverage": {},
            "factions_coverage": {},
            "territories_coverage": {},
            "integrity_score": 0.0,
            "unique_characters_count": 0,
        }

    total_transcribed = sum(1 for v in videos if v.get("is_transcribed"))
    total_with_hash = sum(1 for v in videos if v.get("has_hash"))
    total_pending = total_vids - total_transcribed

    documented_seconds = sum(v.get("duration_seconds", 0) for v in videos)
    vids_with_duration = [v for v in videos if v.get("duration_seconds", 0) > 0]
    avg_duration = (documented_seconds / len(vids_with_duration)) if vids_with_duration else 900  # 15m default

    # Estimativa total: soma dos documentados + média para os pendentes
    estimated_total_seconds = documented_seconds + (total_vids - len(vids_with_duration)) * avg_duration
    est_hours = estimated_total_seconds / 3600

    # Cobertura de Personagens
    chars_counter: Dict[str, int] = {}
    for v in videos:
        for c in v.get("detected_characters", []):
            chars_counter[c] = chars_counter.get(c, 0) + 1

    # Cobertura de Facções
    factions_counter: Dict[str, int] = {}
    for v in videos:
        for f in v.get("detected_factions", []):
            factions_counter[f] = factions_counter.get(f, 0) + 1

    # Cobertura de Territórios
    territories_counter: Dict[str, int] = {}
    for v in videos:
        for t in v.get("detected_territories", []):
            territories_counter[t] = territories_counter.get(t, 0) + 1

    integrity_score = round((total_with_hash / total_vids) * 100, 1) if total_vids > 0 else 0.0

    return {
        "total_videos": total_vids,
        "total_transcribed": total_transcribed,
        "total_with_hash": total_with_hash,
        "total_pending": total_pending,
        "documented_seconds": documented_seconds,
        "documented_hours_str": format_seconds_display(documented_seconds),
        "estimated_total_hours_str": f"~{math.ceil(est_hours)} horas",
        "characters_coverage": dict(sorted(chars_counter.items(), key=lambda x: -x[1])),
        "factions_coverage": dict(sorted(factions_counter.items(), key=lambda x: -x[1])),
        "territories_coverage": dict(sorted(territories_counter.items(), key=lambda x: -x[1])),
        "integrity_score": integrity_score,
        "unique_characters_count": len(chars_counter),
    }


def render_video_corpus_summary(analytics: Dict[str, Any]):
    """Renderiza a faixa editorial de síntese e o painel analítico do acervo."""
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #D8D3C9; border-top: 3px solid #7A2E2E; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem; border-radius: 2px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #7A2E2E; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem;">
            Acervo Audiovisual & História Oral Documentada
        </div>
        <h3 style="font-family: 'Libre Baskerville', serif; margin: 0 0 0.5rem 0; font-size: 1.4rem; color: #20201E;">
            100 Documentários de Investigação Histórica (Iconografia da História)
        </h3>
        <p style="font-size: 0.9rem; color: #5A564F; margin-bottom: 1rem; max-width: 85ch;">
            Coleção integral de episódios catalogados e auditados, cobrindo a gênese do crime organizado, esquadrões de extermínio,
            guerras de facções, milícias paramilitares e a contravenção no Rio de Janeiro de 1950 a 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Grid de Indicadores Principais
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Documentários", analytics["total_videos"], help="Total de episódios integrados ao catálogo permanente")
    with col2:
        st.metric("Transcrições com Hash", f"{analytics['total_with_hash']} / {analytics['total_videos']}", help="Documentários com transcrição textual verificada por hash SHA-256")
    with col3:
        st.metric("Acervo Audiovisual", analytics["estimated_total_hours_str"], help="Tempo total estimado da coleção documental")
    with col4:
        st.metric("Personagens Indexados", analytics["unique_characters_count"], help="Figuras centrais com documentário biográfico dedicado")
    with col5:
        st.metric("Matrizes & Frentes", len(analytics["factions_coverage"]), help="Fações prisionais, grupos paramilitares e forças policiais mapeadas")

    # Painel Expansível de Cobertura Temática e Epistemológica
    with st.expander("📊 Distribuição Analítica: Personagens Históricos, Facções & Territórios Cobertos"):
        c_factions, c_chars, c_terrs = st.columns(3)

        with c_factions:
            st.markdown("<div style='font-size:0.82rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.06em; margin-bottom:8px;'>Matrizes Criminais & Institucionais</div>", unsafe_allow_html=True)
            for fac, count in analytics["factions_coverage"].items():
                pct = int((count / analytics["total_videos"]) * 100)
                st.markdown(f"""
                <div style="margin-bottom: 6px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#20201E;">
                        <span>{fac}</span>
                        <span style="font-family:'JetBrains Mono',monospace; font-weight:600; color:#7A2E2E;">{count} ({pct}%)</span>
                    </div>
                    <div style="background-color:#EBE7DF; height:5px; border-radius:2px; margin-top:2px;">
                        <div style="background-color:#7A2E2E; height:5px; width:{pct}%; border-radius:2px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with c_chars:
            st.markdown("<div style='font-size:0.82rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.06em; margin-bottom:8px;'>Principais Personagens Retratados</div>", unsafe_allow_html=True)
            top_chars = list(analytics["characters_coverage"].items())[:8]
            for ch, count in top_chars:
                badge_color = "#EAF2E8" if count > 1 else "#FAF8F5"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 8px; margin-bottom:4px; background:{badge_color}; border:1px solid #D8D3C9; border-radius:3px; font-size:0.82rem;">
                    <span style="font-weight:600; color:#20201E;">{ch}</span>
                    <span style="font-family:'JetBrains Mono',monospace; color:#7A2E2E; font-weight:700;">{count} ep.</span>
                </div>
                """, unsafe_allow_html=True)

        with c_terrs:
            st.markdown("<div style='font-size:0.82rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.06em; margin-bottom:8px;'>Territórios & Favelas em Destaque</div>", unsafe_allow_html=True)
            for terr, count in analytics["territories_coverage"].items():
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 8px; margin-bottom:4px; background:#FFFFFF; border:1px solid #D8D3C9; border-radius:3px; font-size:0.82rem;">
                    <span style="color:#20201E;">{terr}</span>
                    <span style="font-family:'JetBrains Mono',monospace; color:#20201E; font-weight:600;">{count} ep.</span>
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# MODAL / VISUALIZADOR DE TRANSCRIÇÃO INTERATIVA
# =============================================================================

def render_transcript_viewer(video: Dict[str, Any]):
    """Renderiza a gaveta de inspeção da transcrição com busca interna e timestamps clicáveis."""
    vid_id = video.get("video_id")
    title = video.get("title")
    tdata = load_transcript_file(vid_id)

    st.markdown(f"""
    <div style="background-color:#FAF9F5; border:1px solid #D8D3C9; border-left:4px solid #7A2E2E; padding:12px 16px; margin: 10px 0 16px 0; border-radius:2px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#7A2E2E; font-weight:700;">TRANSCRIÇÃO AUDITADA · {video.get('id')}</div>
        <div style="font-family:'Libre Baskerville',serif; font-size:1.05rem; font-weight:700; color:#20201E; margin:3px 0 6px 0;">{title}</div>
        <div style="font-size:0.78rem; color:#5A564F; font-family:'JetBrains Mono',monospace;">
            SHA-256: <b>{video.get('sha256_hash') or 'Calculando...'}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not tdata or not tdata.get("snippets"):
        st.warning("O arquivo textual bruto desta transcrição não está disponível localmente no momento.")
        return

    snippets = tdata.get("snippets", [])
    st.caption(f"Total de fragmentos de fala capturados: {len(snippets)} | Duração aferida: {video.get('duration_display')}")

    # Busca interna na transcrição
    search_term = st.text_input(
        f"Buscar dentro da transcrição de '{vid_id}':",
        placeholder="Ex: pistola, fuzil, polícia, propina, liderança...",
        key=f"search_trans_{vid_id}"
    )

    matching_snippets = []
    norm_search = normalize_string(search_term) if search_term else None

    for idx, s in enumerate(snippets):
        txt = s.get("text", "")
        if not norm_search or norm_search in normalize_string(txt):
            matching_snippets.append((idx, s))

    if search_term:
        st.caption(f"Exibindo {len(matching_snippets)} de {len(snippets)} trechos correspondentes ao termo '{search_term}'.")

    # Contêiner rolável de falas
    transcript_html = ['<div style="max-height: 380px; overflow-y: auto; background:#FFFFFF; border:1px solid #D8D3C9; border-radius:2px; padding:10px 14px; font-family:\'Source Sans 3\',sans-serif; font-size:0.88rem; line-height:1.5;">']

    for idx, s in matching_snippets[:120]:
        start = float(s.get("start", 0.0))
        mins = int(start // 60)
        secs = int(start % 60)
        yt_timestamp_url = f"https://www.youtube.com/watch?v={vid_id}&t={int(start)}s"
        txt = s.get("text", "")

        # Destaque de termo buscado
        if norm_search:
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)
            txt_display = pattern.sub(lambda m: f"<mark style='background:#FDE047; font-weight:700;'>{m.group(0)}</mark>", txt)
        else:
            txt_display = txt

        transcript_html.append(
            f"<div style='margin-bottom: 8px; border-bottom: 1px dotted #E5E0D8; padding-bottom: 4px;'>"
            f"<a href='{yt_timestamp_url}' target='_blank' style='font-family:\"JetBrains Mono\",monospace; font-size:0.75rem; color:#7A2E2E; font-weight:700; text-decoration:none; margin-right:8px;'>[{mins:02d}:{secs:02d}]</a> "
            f"<span style='color:#20201E;'>{txt_display}</span>"
            f"</div>"
        )

    transcript_html.append('</div>')
    st.markdown("".join(transcript_html), unsafe_allow_html=True)

    # Botões de Exportação da Transcrição
    c_dl1, c_dl2 = st.columns(2)
    with c_dl1:
        full_text = "\n".join([f"[{int(s.get('start',0)//60):02d}:{int(s.get('start',0)%60):02d}] {s.get('text','')}" for s in snippets])
        st.download_button(
            "📥 Baixar Transcrição Completa (.TXT)",
            data=full_text.encode("utf-8"),
            file_name=f"transcricao_{vid_id}.txt",
            mime="text/plain",
            key=f"dl_txt_{vid_id}",
            use_container_width=True
        )
    with c_dl2:
        st.download_button(
            "📥 Baixar Estrutura JSON com Timestamps",
            data=json.dumps(tdata, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"transcricao_{vid_id}.json",
            mime="application/json",
            key=f"dl_json_{vid_id}",
            use_container_width=True
        )


# =============================================================================
# COMPONENTE PRINCIPAL — EXPLORADOR DO CORPUS AUDIOVISUAL
# =============================================================================

def render_video_corpus_explorer(
    catalog_path: Optional[str] = None,
    compact: bool = False
):
    """
    Renderiza o componente completo de exploração do acervo audiovisual.
    Pode ser invocado diretamente em 'Acervo de Fontes', 'Metodologia' ou 'Visão Geral'.
    """
    raw_catalog = load_video_catalog(catalog_path)
    if raw_catalog.get("_error"):
        st.error(f"⚠️ Atenção metodológica: {raw_catalog.get('_error')}")
        st.info("Execute 'python scripts/transcription/pipeline_transcription.py --sync-catalog' para reindexar o acervo.")
        return

    raw_videos = raw_catalog.get("videos", [])
    if not raw_videos:
        st.info("Nenhum documentário cadastrado no catálogo audiovisual.")
        return

    transcripts_map = get_available_transcripts_map()
    videos = [enrich_video_entry(v, transcripts_map) for v in raw_videos]
    analytics = get_video_corpus_analytics(videos)

    # 1. Resumo Analítico Superior
    if not compact:
        render_video_corpus_summary(analytics)
    else:
        st.markdown(f"""
        <div style="font-size:0.9rem; color:#5A564F; margin-bottom:0.8rem;">
            <b>{analytics['total_videos']}</b> documentários catalogados · <b>{analytics['total_with_hash']}</b> com transcrição SHA-256 · <b>{analytics['estimated_total_hours_str']}</b> de conteúdo.
        </div>
        """, unsafe_allow_html=True)

    # 2. Barra Unificada de Filtros e Busca Rápida
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    f_col_search, f_col_sort = st.columns([3, 1])

    with f_col_search:
        search_query = st.text_input(
            "🔍 Busca Rápida no Acervo (Personagem, Facção, Favela, Território ou Fato):",
            placeholder="Ex: Bem-Te-Vi, Brasileirinho, Le Cocq, Rocinha, Milícia, Bangu, pistola de ouro...",
            key="v_corpus_search_input"
        )

    with f_col_sort:
        sort_mode = st.selectbox(
            "Ordenar por:",
            ["Ordem do Catálogo", "Título (A–Z)", "Maior Duração", "Menor Duração", "Apenas Transcritos Primeiro"],
            key="v_corpus_sort"
        )

    # Filtros Avançados em 4 Colunas
    c_status, c_fac, c_terr, c_dur = st.columns(4)

    with c_status:
        status_opts = ["Todos os Status", "Certificados com SHA-256", "Transcrições Pendentes"]
        sel_status = st.selectbox("Status de Custódia:", status_opts, key="v_corpus_f_status")

    with c_fac:
        fac_opts = ["Todas as Matrizes"] + list(analytics["factions_coverage"].keys())
        sel_fac = st.selectbox("Facção / Matriz:", fac_opts, key="v_corpus_f_fac")

    with c_terr:
        terr_opts = ["Todos os Territórios"] + sorted(list(analytics["territories_coverage"].keys()))
        sel_terr = st.selectbox("Território / Favela:", terr_opts, key="v_corpus_f_terr")

    with c_dur:
        dur_opts = ["Todas as Durações", "Curtas (<12 min)", "Médias (12–18 min)", "Longas (>18 min)"]
        sel_dur = st.selectbox("Faixa de Duração:", dur_opts, key="v_corpus_f_dur")

    # 3. Execução da Filtragem
    filtered: List[Dict[str, Any]] = []
    norm_q = normalize_string(search_query) if search_query else None

    for v in videos:
        # Filtro de Status
        if sel_status == "Certificados com SHA-256" and not v.get("has_hash"):
            continue
        if sel_status == "Transcrições Pendentes" and v.get("has_hash"):
            continue

        # Filtro de Facção
        if sel_fac != "Todas as Matrizes" and sel_fac not in v.get("detected_factions", []):
            continue

        # Filtro de Território
        if sel_terr != "Todos os Territórios" and sel_terr not in v.get("detected_territories", []):
            continue

        # Filtro de Duração
        if sel_dur != "Todas as Durações":
            bucket = v.get("duration_bucket", "")
            if "Curtas" in sel_dur and "Curta" not in bucket:
                continue
            if "Médias" in sel_dur and "Média" not in bucket:
                continue
            if "Longas" in sel_dur and "Longa" not in bucket:
                continue

        # Busca Textual Inteligente (Título, Personagens, Territórios e Fala)
        if norm_q:
            title_norm = normalize_string(v.get("title", ""))
            id_norm = normalize_string(v.get("id", ""))
            chars_norm = " ".join(normalize_string(c) for c in v.get("detected_characters", []))
            facs_norm = " ".join(normalize_string(f) for f in v.get("detected_factions", []))
            terrs_norm = " ".join(normalize_string(t) for t in v.get("detected_territories", []))

            matched = (
                norm_q in title_norm
                or norm_q in id_norm
                or norm_q in chars_norm
                or norm_q in facs_norm
                or norm_q in terrs_norm
            )

            # Busca também dentro dos snippets da transcrição se disponível
            if not matched and v.get("has_local_snippets"):
                trans_info = transcripts_map.get(v.get("video_id"))
                if trans_info:
                    for snip in trans_info.get("snippets", []):
                        if norm_q in normalize_string(snip.get("text", "")):
                            matched = True
                            v["_search_highlight"] = snip.get("text", "")
                            break

            if not matched:
                continue

        filtered.append(v)

    # 4. Ordenação dos Documentários
    if sort_mode == "Título (A–Z)":
        filtered.sort(key=lambda x: x.get("title", "").lower())
    elif sort_mode == "Maior Duração":
        filtered.sort(key=lambda x: -x.get("duration_seconds", 0))
    elif sort_mode == "Menor Duração":
        filtered.sort(key=lambda x: (x.get("duration_seconds", 0) <= 0, x.get("duration_seconds", 0)))
    elif sort_mode == "Apenas Transcritos Primeiro":
        filtered.sort(key=lambda x: (not x.get("has_hash"), x.get("id", "")))

    # 5. Barra de Resultados e Paginação
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #D8D3C9; padding-bottom:8px; margin: 12px 0 16px 0;">
        <div style="font-size:0.92rem; color:#20201E;">
            Exibindo <b>{len(filtered)}</b> de <b>{len(videos)}</b> documentários documentados
            {f" para '<b>{search_query}</b>'" if search_query else ""}
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#7A2E2E;">
            100% AUDITADO CONTRA YOUTUBE
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not filtered:
        st.info("Nenhum documentário localizado para os critérios e filtros selecionados.")
        return

    # Controles de Paginação
    items_per_page_options = [12, 24, 48, 100]
    col_p1, col_p2 = st.columns([4, 1])
    with col_p2:
        items_per_page = st.selectbox("Itens por página:", items_per_page_options, index=0, key="v_corpus_per_page")

    total_pages = max(1, math.ceil(len(filtered) / items_per_page))
    current_page_key = "v_corpus_page_num"
    if current_page_key not in st.session_state:
        st.session_state[current_page_key] = 1

    if st.session_state[current_page_key] > total_pages:
        st.session_state[current_page_key] = 1

    start_idx = (st.session_state[current_page_key] - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered))
    current_slice = filtered[start_idx:end_idx]

    # 6. Renderização em Grid de Cartões Modernos (3 colunas)
    cols_per_row = 3
    for i in range(0, len(current_slice), cols_per_row):
        row_videos = current_slice[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, vid in zip(cols, row_videos):
            with col:
                render_single_video_card(vid)

    # 7. Rodapé de Paginação
    if total_pages > 1:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        cp_left, cp_center, cp_right = st.columns([1, 2, 1])

        with cp_left:
            if st.button("◀ Anterior", disabled=(st.session_state[current_page_key] <= 1), use_container_width=True, key="btn_prev_page"):
                st.session_state[current_page_key] -= 1
                st.rerun()

        with cp_center:
            st.markdown(
                f"<div style='text-align:center; padding-top:8px; font-family:\"JetBrains Mono\",monospace; font-size:0.85rem;'>"
                f"Página <b>{st.session_state[current_page_key]}</b> de <b>{total_pages}</b> "
                f"({len(filtered)} documentários)"
                f"</div>",
                unsafe_allow_html=True
            )

        with cp_right:
            if st.button("Próxima ▶", disabled=(st.session_state[current_page_key] >= total_pages), use_container_width=True, key="btn_next_page"):
                st.session_state[current_page_key] += 1
                st.rerun()


# =============================================================================
# RENDERIZADOR DE CARTÃO INDIVIDUAL DE DOCUMENTÁRIO
# =============================================================================

def render_single_video_card(video: Dict[str, Any]):
    """Renderiza um cartão moderno para um documentário individual."""
    vid_id = video.get("video_id")
    catalog_id = video.get("id")
    title = video.get("title") or "Título não disponível"
    duration = video.get("duration_display") or "S/D"
    yt_url = video.get("youtube_url") or f"https://www.youtube.com/watch?v={vid_id}"
    has_hash = video.get("has_hash")
    sha_hash = video.get("sha256_hash")
    chars = video.get("detected_characters", [])
    factions = video.get("detected_factions", [])
    territories = video.get("detected_territories", [])
    search_snip = video.get("_search_highlight")

    # Badges de Verificação e Status
    if has_hash:
        badge_custodia = (
            '<span style="background-color: #EAF2E8; color: #1E4620; border: 1px solid #C2DCC0; '
            'padding: 2px 6px; font-size: 0.70rem; font-family: \'JetBrains Mono\', monospace; '
            'font-weight: 600; border-radius: 2px;">🛡️ Transcrição Auditada (SHA-256)</span>'
        )
    else:
        badge_custodia = (
            '<span style="background-color: #FAF8F5; color: #827D72; border: 1px solid #D8D3C9; '
            'padding: 2px 6px; font-size: 0.70rem; font-family: \'JetBrains Mono\', monospace; '
            'font-weight: 600; border-radius: 2px;">⏳ Em Fila de Transcrição</span>'
        )

    dur_badge = (
        f'<span style="background-color: #20201E; color: #FFFFFF; padding: 2px 6px; '
        f'font-size: 0.70rem; font-family: \'JetBrains Mono\', monospace; font-weight: 700; '
        f'border-radius: 2px;">⏱️ {duration}</span>'
    )

    # Miniatura com Fallback
    thumb_url = video.get("thumbnail_url") or f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"

    # Montagem de Pílulas de Facção e Território
    pills_html = []
    for fac in factions[:2]:
        pills_html.append(f'<span style="background:#F7EBEB; color:#7A2E2E; font-size:0.70rem; padding:1px 6px; border-radius:2px; font-weight:600; margin-right:4px;">{fac.split(" (")[0]}</span>')
    for terr in territories[:1]:
        pills_html.append(f'<span style="background:#EBE7DF; color:#3A3833; font-size:0.70rem; padding:1px 6px; border-radius:2px; font-weight:600; margin-right:4px;">📍 {terr}</span>')
    for ch in chars[:2]:
        pills_html.append(f'<span style="background:#FAF8F5; color:#5A564F; font-size:0.70rem; border:1px solid #D8D3C9; padding:1px 6px; border-radius:2px; font-weight:600; margin-right:4px;">👤 {ch}</span>')

    pills_joined = "".join(pills_html) if pills_html else '<span style="color:#827D72; font-size:0.70rem;">Documentário Geral</span>'

    # Trecho de Busca em Destaque se houver
    snip_html = ""
    if search_snip:
        snip_html = f"""
        <div style="background-color: #FEF9EE; border-left: 3px solid #8C580E; padding: 4px 8px; margin: 6px 0; font-size: 0.75rem; color: #4A4740; font-style: italic;">
            "...{search_snip[:110]}..."
        </div>
        """

    # Renderização do Cartão HTML
    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 1px solid #D8D3C9; border-radius: 4px; padding: 12px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); display: flex; flex-direction: column; height: 100%;">
        <!-- Topo: Miniatura + Duração -->
        <div style="position: relative; width: 100%; aspect-ratio: 16/9; background-color: #000000; border-radius: 3px; overflow: hidden; margin-bottom: 10px; border: 1px solid #D8D3C9;">
            <img src="{thumb_url}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null; this.src='https://img.youtube.com/vi/{vid_id}/mqdefault.jpg';" />
            <div style="position: absolute; bottom: 6px; right: 6px;">
                {dur_badge}
            </div>
            <div style="position: absolute; top: 6px; left: 6px;">
                <span style="background: rgba(32,32,30,0.85); color: #FFFFFF; font-family:'JetBrains Mono',monospace; font-size: 0.68rem; padding: 2px 6px; border-radius: 2px;">{catalog_id}</span>
            </div>
        </div>

        <!-- Badges de Custódia -->
        <div style="margin-bottom: 6px;">
            {badge_custodia}
        </div>

        <!-- Título Editorial -->
        <div style="font-family: 'Libre Baskerville', Georgia, serif; font-size: 0.95rem; font-weight: 700; color: #20201E; line-height: 1.35; margin-bottom: 8px; min-height: 48px;">
            {title}
        </div>

        <!-- Tags / Pílulas de Classificação -->
        <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px;">
            {pills_joined}
        </div>

        {snip_html}

        <!-- Link Direto YouTube -->
        <div style="margin-top: auto; padding-top: 8px; border-top: 1px solid #EBE7DF;">
            <a href="{yt_url}" target="_blank" style="display: block; text-align: center; background-color: #7A2E2E; color: #FFFFFF; text-decoration: none; font-size: 0.82rem; font-weight: 600; padding: 6px 12px; border-radius: 3px; margin-bottom: 6px;">
                ▶ Assistir no YouTube
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ferramentas do Pesquisador (Citação ABNT e Transcrição)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        with st.popover("📋 Citar ABNT", use_container_width=True, help="Copiar referência formal em formato ABNT"):
            st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; margin-bottom:4px;'>Referência Bibliográfica (ABNT)</div>", unsafe_allow_html=True)
            st.code(video.get("abnt_citation", ""), language="markdown")
            if sha_hash:
                st.markdown(f"<div style='font-size:0.72rem; color:#6F6B63; font-family:\"JetBrains Mono\",monospace;'>Hash SHA-256: <code>{sha_hash}</code></div>", unsafe_allow_html=True)

    with c_btn2:
        if video.get("is_transcribed"):
            with st.popover("📜 Transcrição", use_container_width=True, help="Abrir transcrição auditada e buscar falas"):
                render_transcript_viewer(video)
        else:
            st.button("⏳ Pendente", disabled=True, use_container_width=True, key=f"btn_pend_{catalog_id}_{vid_id}", help="Transcrição em fila de processamento no pipeline de ingestão.")
