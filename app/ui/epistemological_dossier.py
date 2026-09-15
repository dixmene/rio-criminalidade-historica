# -*- coding: utf-8 -*-
"""
Componente de UI: Ficha Epistemológica do Acontecimento Histórico
=================================================================

Substitui a lógica de dashboard convencional por um dossiê de auditoria
científica, permitindo a pesquisadores examinar a proveniência de cada afirmação,
a genealogia das fontes, o status de verificação e as limitações empíricas.
"""

import streamlit as st
from typing import Optional, Any
from app.services.genealogy_service import GenealogyService
from app.services.verification_service import VerificationService, PRIMARY_SOURCE_TYPES
from app.map.builder import _infer_evidence_level, EVIDENCE_LEVELS


def render_epistemological_dossier(event: Any, service: Optional[Any] = None) -> None:
    """
    Renderiza a Ficha Epistemológica completa de um acontecimento histórico selecionado.
    """
    if not event:
        st.info("Nenhum acontecimento selecionado.")
        return

    # 1. Metadados de Nível de Evidência
    ev_lvl = _infer_evidence_level(event)
    ev_info = EVIDENCE_LEVELS.get(ev_lvl, EVIDENCE_LEVELS["C"])

    # Metadados de Intervalo Temporal
    dt_display = event.date_display or "S/D"
    precisao = getattr(event, "temporal_precision", "ano") or "ano"
    dt_start = getattr(event, "date_start", None)
    dt_end = getattr(event, "date_end", None)
    is_estimada = getattr(event, "date_is_estimated", False)

    intervalo_str = ""
    if dt_start and dt_end:
        intervalo_str = f"{dt_start.isoformat()} a {dt_end.isoformat()}"
    elif dt_start:
        intervalo_str = f"A partir de {dt_start.isoformat()}"

    # Cabeçalho do Dossiê
    st.markdown(f"""
    <div class="archive-dossier" style="border-top: 3px solid #7A2E2E; margin-bottom: 1.2rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="badge-editorial" style="background:{ev_info['color']}; color:#fff; border:none; padding:3px 8px; font-weight:700;">{ev_info['label']}</span>
            <span class="archive-tag">{dt_display} · {'[DEMO]' if event.is_demo else 'ACERVO REAL'}</span>
        </div>
        <div class="archive-title" style="font-size: 1.35rem; margin-bottom: 6px;">{event.title}</div>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom: 10px;">
            <span class="badge-editorial badge-real">Status: {(event.confidence_level or 'Indefinido').upper()}</span>
            <span class="badge-editorial">Precisão Temporal: {precisao.upper()}</span>
            {'<span class="badge-editorial badge-demo">DATA ESTIMADA</span>' if is_estimada else ''}
        </div>
        {f"<div style='font-size:0.8rem; color:#5A564F; font-family:\"JetBrains Mono\", monospace; margin-bottom:10px;'>Intervalo Formal: {intervalo_str}</div>" if intervalo_str else ""}
        <div style="font-size: 0.94rem; color: #20201E; line-height: 1.6; margin-bottom: 10px;">
            {event.description}
        </div>
        {f"<div style='font-size: 0.88rem; color: #4A4740; font-style: italic; border-left: 2px solid #7A2E2E; padding-left: 10px; margin-bottom: 12px; background:#FAF8F5; padding-top:4px; padding-bottom:4px;'><b>Contexto Historiográfico:</b> {event.historical_context}</div>" if event.historical_context else ""}
        <div style="font-size: 0.82rem; color: #4A4740; border-top: 1px solid #E5E0D8; padding-top: 8px;">
            <b>Território(s):</b> {', '.join(r.original_name for r in getattr(event, 'regions', [])) or 'Difuso / Não delimitado pontualmente'}<br>
            <b>Organização(ões):</b> {', '.join(o.original_name for o in getattr(event, 'organizations', [])) or 'Nenhuma organização citada'}<br>
            <b>Atores / Lideranças:</b> {', '.join(p.original_name for p in getattr(event, 'people', [])) or 'Nenhuma pessoa identificada'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Abas da Ficha Epistemológica
    tab_claims, tab_genealogia, tab_fontes, tab_lacunas = st.tabs([
        "📜 Proposições & Discurso (Claims)",
        "🌳 Genealogia & Anti-Falsa Triangulação",
        "📚 Fontes & Custódia Digital (SHA-256)",
        "🔍 Auditoria & Lacunas Documentais"
    ])

    # -------------------------------------------------------------
    # ABA 1: CLAIMS & TIPOLOGIA DE DISCURSO
    # -------------------------------------------------------------
    with tab_claims:
        claims = getattr(event, "claims", [])
        if not claims:
            st.info("Nenhuma claim atômica isolada para este acontecimento. O registro apoia-se em fontes sumárias.")
        else:
            st.markdown(f"**{len(claims)} afirmação(ões) atômica(s) extraída(s) com rastreamento documental:**")
            for idx, cl in enumerate(claims, 1):
                disputada_badge = '<span class="badge-editorial badge-conflitante">CONTROVÉRSIA HISTORIOGRÁFICA</span>' if cl.is_disputed else ''
                st.markdown(f"""
                <div class="claim-box" style="margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; font-weight:700; color:#7A2E2E;">CLAIM #{cl.id} · TIPO: {(cl.claim_type or 'fato').upper()}</span>
                        <span class="badge-editorial">{cl.confidence_level.upper()}</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight:600; color:#1C1B18; margin-bottom: 6px;">
                        {cl.statement} {disputada_badge}
                    </div>
                    {f"<div style='font-size:0.82rem; color:#5A564F; font-style:italic; margin-bottom:6px;'><b>Nota Epistemológica:</b> {cl.epistemological_notes}</div>" if cl.epistemological_notes else ""}
                </div>
                """, unsafe_allow_html=True)

                # Evidências e citações literais da claim
                for csl in cl.source_links:
                    src = csl.source
                    stance_css = f"stance-{csl.stance.lower()}"
                    discurso = getattr(csl, "source_assessment", "narracao_documental") or "narracao_documental"
                    timestamp = getattr(csl, "section", "") or getattr(csl, "page", "") or "N/A"

                    st.markdown(f"""
                    <div style="margin-left: 18px; margin-bottom: 10px; padding: 8px 12px; background: #FFFFFF; border-left: 3px solid #D8D3C9; border-radius: 2px;">
                        <div style="display:flex; justify-content:space-between; font-size: 0.8rem; margin-bottom: 4px;">
                            <span><span class="{stance_css}">[{csl.stance.upper()}]</span> <b>{src.title}</b> ({src.author or src.publisher or 'Acervo'})</span>
                            <span style="font-family:'JetBrains Mono', monospace; color:#6F6B63;">{timestamp}</span>
                        </div>
                        <div style="font-size: 0.76rem; color: #7A2E2E; font-family:'JetBrains Mono', monospace; margin-bottom: 4px;">
                            TIPOLOGIA DE DISCURSO: {discurso.upper()}
                        </div>
                        <div class="source-excerpt" style="margin: 0; font-size: 0.86rem;">
                            \"{csl.excerpt}\"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ABA 2: GENEALOGIA & ANTI-FALSA TRIANGULAÇÃO
    # -------------------------------------------------------------
    with tab_genealogia:
        st.markdown("### Análise Genealógica e Independência das Fontes")
        st.caption("Apoiar uma afirmação em múltiplos vídeos ou matérias que derivam da mesma obra original NÃO constitui confirmação independente.")

        claims = getattr(event, "claims", [])
        if not claims:
            st.info("Sem claims cadastradas para avaliação genealógica.")
        else:
            for cl in claims:
                report = GenealogyService.evaluate_claim_epistemology(cl)
                ev_count = report["evidence_count"]
                root_count = report["independent_root_count"]
                has_shared = report["has_shared_roots"]

                st.markdown(f"**Proposição #{cl.id}:** *\"{cl.statement[:65]}...\"*")

                c_g1, c_g2, c_g3 = st.columns(3)
                with c_g1:
                    st.metric("Total de Fontes", ev_count)
                with c_g2:
                    st.metric("Raízes Independentes", root_count)
                with c_g3:
                    if has_shared:
                        st.markdown("<div style='color:#8C2D2D; font-weight:700; font-size:0.9rem; padding-top:14px;'>⚠️ Falsa Triangulação Detectada</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color:#2D5A27; font-weight:700; font-size:0.9rem; padding-top:14px;'>✓ Triangulação Válida</div>", unsafe_allow_html=True)

                if has_shared:
                    for sr in report["shared_roots"]:
                        st.warning(f"As seguintes fontes derivam da mesma raiz original **'{sr['root_title']}'**: {', '.join(sr['derived_titles'])}.")

                st.markdown("<hr style='margin: 8px 0; border-color:#E5E0D8;'>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ABA 3: FONTES DOCUMENTAIS & CUSTÓDIA DIGITAL (SHA-256)
    # -------------------------------------------------------------
    with tab_fontes:
        st.markdown("### Cadeia de Custódia Digital e Fontes Primárias/Secundárias")
        all_sources = list(getattr(event, "sources", []))
        for cl in getattr(event, "claims", []):
            for s in getattr(cl, "sources", []):
                if s not in all_sources:
                    all_sources.append(s)

        if not all_sources:
            st.error("Alerta: Registro sem sustentação documental no banco.")
        else:
            for idx, src in enumerate(all_sources, 1):
                is_primary = src.source_type in PRIMARY_SOURCE_TYPES
                tipo_badge = '<span class="badge-editorial badge-real">FONTE PRIMÁRIA</span>' if is_primary else '<span class="badge-editorial">FONTE SECUNDÁRIA</span>'
                hash_val = src.file_hash_sha256 or "Remoto / Sem arquivo binário local"

                st.markdown(f"""
                <div class="source-citation-block" style="margin-bottom: 10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <b>{idx:02d}. {src.title}</b>
                        {tipo_badge}
                    </div>
                    <div class="source-meta">
                        <b>Citação:</b> {src.citation}<br>
                        <b>Tipologia:</b> {src.source_type} · <b>Autor/Veículo:</b> {src.author or src.publisher or 'N/A'}<br>
                        {f"<b>URL:</b> <a href='{src.url}' target='_blank'>{src.url}</a><br>" if src.url else ""}
                        <b>Hash SHA-256 de Custódia:</b> <code>{hash_val[:32]}...</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ABA 4: AUDITORIA & LACUNAS DOCUMENTAIS
    # -------------------------------------------------------------
    with tab_lacunas:
        st.markdown("### Auditoria de Rigor e Fila de Verificação (Verification Queue)")
        claims = getattr(event, "claims", [])
        if not claims:
            st.info("Nenhuma claim pendente de auditoria.")
        else:
            for cl in claims:
                audit = VerificationService.audit_claim(cl)
                prio = audit["priority"]
                prio_color = {"CRITICA": "#8C2D2D", "ALTA": "#B45309", "MEDIA": "#D97706", "BAIXA": "#2D5A27"}.get(prio, "#6F6B63")

                st.markdown(f"""
                <div style="padding:10px 14px; background:#FAF9F5; border:1px solid #E5E0D8; border-left:4px solid {prio_color}; margin-bottom:10px; border-radius:2px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                        <span style="font-weight:700; color:{prio_color};">PRIORIDADE NA FILA: {prio}</span>
                        <span style="font-family:'JetBrains Mono', monospace;">Fontes Primárias: {audit['primary_source_count']}</span>
                    </div>
                    <div style="font-size:0.9rem; font-weight:600; color:#20201E; margin-bottom:6px;">
                        \"{cl.statement}\"
                    </div>
                    <div style="font-size:0.82rem; color:#4A4740;">
                        <b>Diagnóstico Epistemológico:</b> {'; '.join(audit['reasons'])}<br>
                        <b>Ação Recomendada para o Pesquisador:</b> {audit['recommended_action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
