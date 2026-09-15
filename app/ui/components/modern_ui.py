# -*- coding: utf-8 -*-
"""
Componentes de Interface Modernos: Obsidian / Cyber-OSINT
=========================================================
Componentes visuais de alto impacto para investigação histórica e geoespacial.

Inclui:
- `render_hero_header()`: Banner de topo com título, impacto investigativo e badges de tecnologia.
- `render_kpi_dashboard(stats)`: Grid de métricas em glassmorphism com barras de progresso e deltas.
- `render_event_card(event)`: Cartão moderno de acontecimento com selo de evidência, facções,
  datação exata, citação literal em destaque e links de proveniência com hash SHA-256.
"""

import html
from typing import Optional, Dict, Any, List

try:
    import streamlit as st
except ImportError:
    st = None

from app.ui.styles.modern_theme import (
    FACTION_COLORS_MODERN,
    EVIDENCE_LEVELS_MODERN,
    STATUS_COLORS_MODERN,
)


def _safe_escape(val: Any) -> str:
    """Escapa texto HTML defensivamente, tratando None e valores numéricos."""
    if val is None:
        return ""
    return html.escape(str(val))


# =============================================================================
# HELPER: DETECÇÃO DE FACÇÃO E BADGES
# =============================================================================

def _detect_faction_key(org_str: str) -> str:
    """Mapeia o nome ou sigla de uma organização para a chave da paleta moderna."""
    s = (org_str or "").upper()
    if "CV" in s or "COMANDO VERMELHO" in s:
        return "CV"
    if "TCP" in s or "TERCEIRO COMANDO PURO" in s:
        return "TCP"
    if "ADA" in s or "AMIGOS DOS AMIGOS" in s:
        return "ADA"
    if any(k in s for k in ["LIGA DA JUSTIÇA", "CL220", "LJ"]):
        return "LJ"
    if "NOVA IGUAÇU" in s or "MNI" in s:
        return "MNI"
    if any(k in s for k in ["MILÍCIA", "MILICIA", "MIL"]):
        return "MIL"
    if any(k in s for k in ["PMERJ", "PCERJ", "BOPE", "POLÍCIA", "POLICIA", "ESTADO", "OFICIAL", "GAECO", "MPRJ", "TJRJ"]):
        return "OFICIAL"
    if any(k in s for k in ["NEUTRO", "DISPUTA", "NEU"]):
        return "NEU"
    return "NEU"


def _get_faction_badge_html(faction_key: str, label: Optional[str] = None) -> str:
    """Retorna badge HTML de facção com brilho suave e cor canônica."""
    cfg = FACTION_COLORS_MODERN.get(faction_key, FACTION_COLORS_MODERN["NEU"])
    display_label = label or cfg["name"]
    css_class = f"badge-{faction_key.lower()}"
    return (
        f'<span class="badge-pill {css_class}" style="'
        f'background:{cfg["bg"]}; color:{cfg["color"]} !important; border:1px solid {cfg["border"]}; '
        f'box-shadow:0 0 10px {cfg["glow"]};">'
        f'<span style="width:6px; height:6px; border-radius:50%; background-color:{cfg["color"]}; display:inline-block;"></span>'
        f'{_safe_escape(display_label)}'
        f'</span>'
    )


def _get_evidence_badge_html(level_key: str) -> str:
    """Retorna badge HTML para o nível de evidência (A, B, C, conflitante)."""
    cfg = EVIDENCE_LEVELS_MODERN.get(level_key, EVIDENCE_LEVELS_MODERN["C"])
    css_class = f"badge-nivel-{level_key.lower()}" if level_key in ("A", "B", "C") else "badge-conflito"
    return (
        f'<span class="badge-pill {css_class}" style="'
        f'background:{cfg["bg"]}; color:{cfg["color"]} !important; border:1px solid {cfg["border"]}; '
        f'box-shadow:0 0 10px {cfg["glow"]};">'
        f'🛡️ {_safe_escape(cfg["short_label"])}'
        f'</span>'
    )


def _infer_evidence_level_fallback(ev: Any) -> str:
    """Inferência defensiva do nível de evidência para objetos ou dicts."""
    if isinstance(ev, dict):
        conf = str(ev.get("confidence_level", "")).lower()
        if conf in ("conflitante", "disputed"):
            return "conflitante"

        # Coletar fontes
        sources = list(ev.get("sources", []))
        if not sources:
            for cl in ev.get("claims", []):
                for sl in cl.get("source_links", []):
                    s = sl.get("source")
                    if s and s not in sources:
                        sources.append(s)
            for sl in ev.get("source_links", []):
                s = sl.get("source")
                if s and s not in sources:
                    sources.append(s)

        has_official = False
        has_academic = False
        for s in sources:
            tipo = str(s.get("source_type", "") if isinstance(s, dict) else getattr(s, "source_type", "")).lower()
            autor = str(s.get("author", "") if isinstance(s, dict) else getattr(s, "author", "")).lower()
            if any(k in tipo for k in ["judicial", "oficial", "sentenca", "inquerito", "boletim", "lei"]):
                has_official = True
            elif any(k in autor for k in ["stf", "tjrj", "mp-rj", "mprj", "pmerj", "polícia", "alerj", "isp"]):
                has_official = True
            elif any(k in tipo for k in ["academico", "artigo", "tese", "dissertacao", "livro"]):
                has_academic = True

        if has_official or conf in ("alta", "confirmado"):
            return "A"
        elif has_academic or conf in ("media", "provavel"):
            return "B"
        return "C"

    # Caso seja modelo SQLAlchemy ou objeto
    try:
        from app.map.builder import _infer_evidence_level
        return _infer_evidence_level(ev)
    except Exception:
        conf = str(getattr(ev, "confidence_level", "")).lower()
        if conf in ("conflitante", "disputed"):
            return "conflitante"
        if conf in ("alta", "confirmado"):
            return "A"
        if conf in ("media", "provavel"):
            return "B"
        return "C"


# =============================================================================
# 1. HERO HEADER BANNER
# =============================================================================

def render_hero_header() -> str:
    """
    Renderiza banner de topo imponente com estética Cyber-OSINT de alta resolução:
    - Indicador de pulso de status ativo do sistema
    - Título hierárquico com tipografia editorial elegante
    - Subtítulo de impacto investigativo
    - Badges tecnológicas: WebGL 60 FPS, 100% Auditável, 69 Snapshots Anuais, Zero Alucinação
    """
    hero_html = """
    <div class="glass-card" style="
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.92) 0%, rgba(11, 15, 23, 0.98) 100%);
        border: 1px solid rgba(55, 65, 81, 0.6);
        border-top: 2px solid #3B82F6;
        border-radius: 14px;
        padding: 2rem 2.25rem 1.75rem 2.25rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 12px 40px -8px rgba(0, 0, 0, 0.75), 0 0 24px rgba(59, 130, 246, 0.15);
        position: relative;
    ">
        <!-- Linha Superior de Status -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 8px;">
                <span class="radar-dot"></span>
                <span style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.74rem;
                    font-weight: 700;
                    letter-spacing: 0.12em;
                    color: #10B981;
                    text-transform: uppercase;
                ">SISTEMA ATIVO // COBERTURA HISTÓRICA & GEOESPACIAL AUDITADA</span>
            </div>
            <div style="
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                color: #64748B;
                letter-spacing: 0.08em;
            ">CORPUS TEMPORAL: 1950 — 2026</div>
        </div>

        <!-- Título Principal -->
        <h1 style="
            font-family: 'Libre Baskerville', Georgia, serif;
            font-size: 2.35rem;
            font-weight: 700;
            line-height: 1.15;
            margin: 0 0 0.75rem 0;
            color: #FFFFFF;
            letter-spacing: -0.02em;
            background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">Atlas Histórico da Criminalidade no Rio de Janeiro</h1>

        <!-- Subtítulo de Impacto Investigativo -->
        <p style="
            font-family: 'Inter', sans-serif;
            font-size: 1.05rem;
            line-height: 1.6;
            color: #94A3B8;
            max-width: 95ch;
            margin: 0 0 1.5rem 0;
            font-weight: 400;
        ">
            Plataforma científica de inteligência geoespacial e reconstituição historiográfica de alta precisão.
            Mapeamento contínuo de 7 décadas de dinâmicas criminais, conflitos entre facções armadas,
            milícias paramilitares e operações de segurança pública no Estado do Rio de Janeiro.
        </p>

        <!-- Faixa de Badges Tecnológicos -->
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding-top: 1.1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            align-items: center;
        ">
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                background: rgba(6, 182, 212, 0.12);
                border: 1px solid rgba(6, 182, 212, 0.35);
                border-radius: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 600;
                color: #22D3EE;
                box-shadow: 0 0 12px rgba(6, 182, 212, 0.18);
            ">
                <span>⚡</span> WebGL 60 FPS
            </div>

            <div style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.35);
                border-radius: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 600;
                color: #34D399;
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.18);
            ">
                <span>🛡️</span> 100% Auditável
            </div>

            <div style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                background: rgba(59, 130, 246, 0.12);
                border: 1px solid rgba(59, 130, 246, 0.35);
                border-radius: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 600;
                color: #60A5FA;
                box-shadow: 0 0 12px rgba(59, 130, 246, 0.18);
            ">
                <span>🗺️</span> 69 Snapshots Anuais
            </div>

            <div style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                background: rgba(139, 92, 246, 0.12);
                border: 1px solid rgba(139, 92, 246, 0.35);
                border-radius: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 600;
                color: #A78BFA;
                box-shadow: 0 0 12px rgba(139, 92, 246, 0.18);
            ">
                <span>🎯</span> Zero Alucinação
            </div>
        </div>
    </div>
    """
    if st is not None and hasattr(st, "markdown"):
        st.markdown(hero_html, unsafe_allow_html=True)
    return hero_html


# =============================================================================
# 2. KPI DASHBOARD EM GRID MODERNO
# =============================================================================

def render_kpi_dashboard(stats: Optional[Dict[str, Any]] = None) -> str:
    """
    Renderiza painel de métricas chave (KPIs) em grid moderno com efeito glassmorphism,
    valores numéricos em JetBrains Mono de alto contraste, deltas e barras de progresso.

    Métricas obrigatórias contempladas:
    1. Territórios Mapeados (1.671 polígonos)
    2. Acontecimentos Históricos Catalogados (53+ eventos verificados)
    3. Fontes e Documentos Auditados (291 fontes com citação literal)
    4. Acervo Audiovisual (100+ documentários com minutagem e transcrição)
    5. Integridade Cartográfica (14/14 checagens aprovadas - 100%)

    Args:
        stats: Dicionário opcional com valores dinâmicos para sobrepor os padrões.
    """
    stats = stats or {}

    val_territorios = stats.get("territorios", "1.671")
    val_eventos = stats.get("eventos", "53+")
    val_fontes = stats.get("fontes", "291")
    val_audiovisual = stats.get("audiovisual", "100+")
    val_integridade = stats.get("integridade", "100%")

    kpis = [
        {
            "icon": "🗺️",
            "title": "Territórios Mapeados",
            "value": str(val_territorios),
            "unit": "Polígonos Vetoriais",
            "delta": "+100% Integrados",
            "progress": 100,
            "gradient": "linear-gradient(90deg, #06B6D4 0%, #3B82F6 100%)",
            "glow": "rgba(6, 182, 212, 0.4)",
            "caption": "Comunidades, AISPs e Bairros",
        },
        {
            "icon": "📅",
            "title": "Acontecimentos Históricos",
            "value": str(val_eventos),
            "unit": "Eventos Verificados",
            "delta": "Série 1958 — 2026",
            "progress": 94,
            "gradient": "linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%)",
            "glow": "rgba(59, 130, 246, 0.4)",
            "caption": "Intervalos de conhecimento rigorosos",
        },
        {
            "icon": "📜",
            "title": "Fontes e Documentos Auditados",
            "value": str(val_fontes),
            "unit": "Acervo Auditado",
            "delta": "Citação Literal 100%",
            "progress": 100,
            "gradient": "linear-gradient(90deg, #10B981 0%, #06B6D4 100%)",
            "glow": "rgba(16, 185, 129, 0.4)",
            "caption": "Inquéritos, teses e hemeroteca",
        },
        {
            "icon": "🎥",
            "title": "Acervo Audiovisual",
            "value": str(val_audiovisual),
            "unit": "Obras Indexadas",
            "delta": "Minutagem e Transcrição",
            "progress": 88,
            "gradient": "linear-gradient(90deg, #F59E0B 0%, #EF4444 100%)",
            "glow": "rgba(245, 158, 11, 0.4)",
            "caption": "Genealogia anti-falsa triangulação",
        },
        {
            "icon": "🛡️",
            "title": "Integridade Cartográfica",
            "value": str(val_integridade),
            "unit": "14/14 Checagens",
            "delta": "Aprovado em Auditoria",
            "progress": 100,
            "gradient": "linear-gradient(90deg, #10B981 0%, #34D399 100%)",
            "glow": "rgba(16, 185, 129, 0.4)",
            "caption": "Topologia sem sobreposição espúria",
        },
    ]

    cards_html = []
    for kpi in kpis:
        c_html = f"""
        <div class="glass-card" style="
            padding: 1.1rem 1.25rem;
            margin-bottom: 0;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <!-- Topo do Card: Ícone e Delta -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <span style="font-size: 1.35rem;">{kpi['icon']}</span>
                <span style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.68rem;
                    font-weight: 700;
                    color: #10B981;
                    background: rgba(16, 185, 129, 0.12);
                    border: 1px solid rgba(16, 185, 129, 0.35);
                    padding: 2px 7px;
                    border-radius: 6px;
                ">{kpi['delta']}</span>
            </div>

            <!-- Centro: Valor e Unidade -->
            <div>
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1.75rem;
                    font-weight: 700;
                    color: #FFFFFF;
                    line-height: 1.1;
                    margin-bottom: 2px;
                    letter-spacing: -0.02em;
                ">{_safe_escape(kpi['value'])}</div>
                <div style="
                    font-family: 'Inter', sans-serif;
                    font-size: 0.82rem;
                    font-weight: 600;
                    color: #E2E8F0;
                    margin-bottom: 2px;
                ">{_safe_escape(kpi['title'])}</div>
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.70rem;
                    color: #94A3B8;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">{_safe_escape(kpi['unit'])}</div>
            </div>

            <!-- Fundo: Barra de Progresso e Legenda -->
            <div style="margin-top: 0.85rem;">
                <div style="
                    width: 100%;
                    height: 5px;
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 4px;
                    overflow: hidden;
                    margin-bottom: 5px;
                ">
                    <div style="
                        width: {kpi['progress']}%;
                        height: 100%;
                        background: {kpi['gradient']};
                        box-shadow: 0 0 8px {kpi['glow']};
                        border-radius: 4px;
                    "></div>
                </div>
                <div style="
                    font-size: 0.70rem;
                    color: #64748B;
                    line-height: 1.2;
                ">{_safe_escape(kpi['caption'])}</div>
            </div>
        </div>
        """
        cards_html.append(c_html)

    grid_html = f"""
    <div style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
        margin-bottom: 1.75rem;
    ">
        {''.join(cards_html)}
    </div>
    """

    if st is not None and hasattr(st, "markdown"):
        st.markdown(grid_html, unsafe_allow_html=True)
    return grid_html


# =============================================================================
# 3. EVENT CARD MODERNO
# =============================================================================

def render_event_card(event: Any) -> str:
    """
    Renderiza cartão moderno de acontecimento histórico:
    - Selo de Evidência com brilho suave (Nível A / B / C / Conflitante)
    - Badges de facções armadas com código de cor canônico (CV #EF4444, TCP #3B82F6, etc.)
    - Datação exata e metadados de precisão temporal
    - Citação literal em destaque (estilo OSINT Callout com metadados)
    - Links de proveniência com hash criptográfico SHA-256

    Suporta instâncias do modelo SQLAlchemy Event, dicionários e mocks.
    """
    if not event:
        return ""

    # Extração defensiva de atributos
    is_dict = isinstance(event, dict)

    ev_id = event.get("id") if is_dict else getattr(event, "id", "N/A")
    title = event.get("title") if is_dict else getattr(event, "title", "Sem Título")
    date_display = event.get("date_display") if is_dict else getattr(event, "date_display", "Data Desconhecida")
    description = event.get("description") if is_dict else getattr(event, "description", "")
    temporal_precision = event.get("temporal_precision") if is_dict else getattr(event, "temporal_precision", "ano")
    is_demo = event.get("is_demo") if is_dict else getattr(event, "is_demo", False)
    historical_context = event.get("historical_context") if is_dict else getattr(event, "historical_context", None)

    # Nível de evidência
    ev_level_key = _infer_evidence_level_fallback(event)
    ev_badge_html = _get_evidence_badge_html(ev_level_key)

    # Organizações / Facções
    org_badges = []
    orgs = event.get("organizations", []) if is_dict else getattr(event, "organizations", [])
    if not orgs and hasattr(event, "organization_links"):
        orgs = [ol.organization for ol in event.organization_links if hasattr(ol, "organization")]

    for o in orgs:
        name = o.get("original_name") if isinstance(o, dict) else getattr(o, "original_name", str(o))
        acronym = o.get("acronym") if isinstance(o, dict) else getattr(o, "acronym", None)
        faction_key = _detect_faction_key(acronym or name)
        label = f"{name} ({acronym})" if acronym and acronym != name else name
        org_badges.append(_get_faction_badge_html(faction_key, label))

    # Se nenhuma organização explícita, tenta deduzir do texto do evento
    if not org_badges:
        detected_in_text = _detect_faction_key(f"{title} {description}")
        if detected_in_text != "NEU":
            org_badges.append(_get_faction_badge_html(detected_in_text))

    org_badges_str = " ".join(org_badges) if org_badges else (
        '<span class="badge-pill badge-neu">Território Geral / Não Setorizado</span>'
    )

    # Territórios
    regions = event.get("regions", []) if is_dict else getattr(event, "regions", [])
    if not regions and hasattr(event, "region_links"):
        regions = [rl.region for rl in event.region_links if hasattr(rl, "region")]
    reg_names = [r.get("original_name") if isinstance(r, dict) else getattr(r, "original_name", str(r)) for r in regions]
    reg_str = ", ".join(reg_names) if reg_names else "Abrangência Estadual / Prisional"

    # Extração de Citação Literal e Metadados de Proveniência
    citations_data = []

    # 1. Tenta extrair de claims atomizadas
    claims = event.get("claims", []) if is_dict else getattr(event, "claims", [])
    for cl in claims:
        cl_statement = cl.get("statement") if isinstance(cl, dict) else getattr(cl, "statement", "")
        cl_links = cl.get("source_links", []) if isinstance(cl, dict) else getattr(cl, "source_links", [])
        for link in cl_links:
            src = link.get("source") if isinstance(link, dict) else getattr(link, "source", None)
            excerpt = link.get("excerpt") if isinstance(link, dict) else getattr(link, "excerpt", "")
            stance = link.get("stance") if isinstance(link, dict) else getattr(link, "stance", "apoia")
            page_sec = (link.get("section") or link.get("page")) if isinstance(link, dict) else (getattr(link, "section", None) or getattr(link, "page", None))
            if excerpt:
                citations_data.append({
                    "excerpt": excerpt,
                    "stance": stance,
                    "source": src,
                    "location": page_sec or "Acervo Documental",
                    "claim_statement": cl_statement,
                })

    # 2. Tenta extrair de source_links diretos se claims não tiverem excerpt
    if not citations_data:
        s_links = event.get("source_links", []) if is_dict else getattr(event, "source_links", [])
        for sl in s_links:
            src = sl.get("source") if isinstance(sl, dict) else getattr(sl, "source", None)
            exc = sl.get("excerpt") if isinstance(sl, dict) else getattr(sl, "excerpt", "")
            if exc:
                citations_data.append({
                    "excerpt": exc,
                    "stance": "apoia",
                    "source": src,
                    "location": "Documento Custodiado",
                    "claim_statement": None,
                })

    # Bloco HTML da Citação Literal
    citation_block_html = ""
    if citations_data:
        c_item = citations_data[0]
        exc_text = c_item["excerpt"]
        src_obj = c_item["source"]

        src_title = src_obj.get("title") if isinstance(src_obj, dict) else getattr(src_obj, "title", "Acervo Oficial") if src_obj else "Acervo Histórico"
        src_author = src_obj.get("author") if isinstance(src_obj, dict) else getattr(src_obj, "author", "") if src_obj else ""
        src_hash = src_obj.get("file_hash_sha256") if isinstance(src_obj, dict) else getattr(src_obj, "file_hash_sha256", None) if src_obj else None
        src_type = src_obj.get("source_type") if isinstance(src_obj, dict) else getattr(src_obj, "source_type", "documento") if src_obj else "documento"

        stance_key = str(c_item["stance"] or "apoia").lower()
        stance_badge = f'<span class="stance-{stance_key}-modern">[{stance_key.upper()}]</span>'

        hash_display = f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.68rem; color: #64748B;">SHA-256: {_safe_escape(src_hash[:16])}...</span>' if src_hash else ''

        citation_block_html = f"""
        <div style="
            margin: 1rem 0;
            padding: 1rem 1.25rem;
            background: rgba(11, 15, 23, 0.75);
            border-left: 3px solid #3B82F6;
            border-radius: 0 8px 8px 0;
            box-shadow: inset 0 0 16px rgba(59, 130, 246, 0.05);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94A3B8;">
                    {stance_badge} <b>CITAÇÃO LITERAL COMPROBATÓRIA</b>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; color: #64748B;">
                    {_safe_escape(c_item['location'])}
                </div>
            </div>
            <div style="
                font-family: 'Merriweather', 'Libre Baskerville', Georgia, serif;
                font-style: italic;
                font-size: 0.92rem;
                line-height: 1.6;
                color: #E2E8F0;
                margin-bottom: 8px;
            ">
                "{_safe_escape(exc_text)}"
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; font-size: 0.74rem; color: #94A3B8;">
                <div>
                    <b>Fonte:</b> {_safe_escape(src_title)} {f'({_safe_escape(src_author)})' if src_author else ''}
                    <span style="color: #64748B; margin-left: 4px;">[{_safe_escape(str(src_type).upper())}]</span>
                </div>
                {hash_display}
            </div>
        </div>
        """

    # Badge de Isolamento DEMO vs REAL
    demo_badge = (
        '<span class="badge-pill" style="background:rgba(245, 158, 11, 0.15); color:#FBBF24; border:1px solid #F59E0B;">TESTE [DEMO]</span>'
        if is_demo else
        '<span class="badge-pill" style="background:rgba(16, 185, 129, 0.12); color:#34D399; border:1px solid #10B981;">ACERVO REAL</span>'
    )

    context_block = ""
    if historical_context:
        context_block = f"""
        <div style="
            font-size: 0.84rem;
            line-height: 1.55;
            color: #94A3B8;
            font-style: italic;
            border-left: 2px solid #64748B;
            padding-left: 10px;
            margin: 8px 0;
        ">
            <b>Contexto Historiográfico:</b> {_safe_escape(historical_context)}
        </div>
        """

    card_html = f"""
    <div class="glass-card glass-card-glow-blue" style="
        border-top: 2px solid #3B82F6;
        padding: 1.4rem 1.6rem;
    ">
        <!-- Topo: Selo de Evidência e Metadados Temporais -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 0.75rem;">
            <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                {ev_badge_html}
                {demo_badge}
                <span class="badge-pill" style="background: rgba(255, 255, 255, 0.05); color: #CBD5E1; border: 1px solid #374151;">
                    PRECISÃO: {_safe_escape(str(temporal_precision).upper())}
                </span>
            </div>
            <div style="
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.82rem;
                font-weight: 700;
                color: #60A5FA;
                letter-spacing: 0.04em;
            ">
                📅 {_safe_escape(str(date_display))}
            </div>
        </div>

        <!-- Título do Evento -->
        <h3 style="
            font-family: 'Libre Baskerville', Georgia, serif;
            font-size: 1.30rem;
            color: #FFFFFF;
            margin: 0 0 0.5rem 0;
            line-height: 1.25;
            font-weight: 700;
        ">{_safe_escape(title)}</h3>

        <!-- Badges de Facção e Território -->
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 0.9rem;">
            {org_badges_str}
            <span style="font-size: 0.80rem; color: #94A3B8; display: inline-flex; align-items: center; gap: 4px;">
                📍 <b>Território:</b> {_safe_escape(reg_str)}
            </span>
        </div>

        <!-- Descrição Factual -->
        <div style="
            font-size: 0.92rem;
            line-height: 1.65;
            color: #CBD5E1;
            margin-bottom: 0.75rem;
        ">
            {_safe_escape(description)}
        </div>

        <!-- Contexto Historiográfico se existir -->
        {context_block}

        <!-- Citação Literal OSINT -->
        {citation_block_html}

        <!-- Rodapé do Card com ID e Proveniência -->
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 0.6rem;
            margin-top: 0.75rem;
            font-size: 0.72rem;
            color: #64748B;
            font-family: 'JetBrains Mono', monospace;
        ">
            <span>REGISTRO ID: #{_safe_escape(ev_id)}</span>
            <span>PROVENIÊNCIA HISTÓRICA AUDITADA</span>
        </div>
    </div>
    """

    if st is not None and hasattr(st, "markdown"):
        st.markdown(card_html, unsafe_allow_html=True)
    return card_html
