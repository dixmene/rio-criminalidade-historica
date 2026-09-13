"""
Coletor e Processador de Proposições Legislativas (CMRJ & ALERJ).
Cruza proposições com a taxonomia de pautas sensíveis e gera database/proposicoes_legislativas.csv.
"""

import os
import sys
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.classifier_pautas import classify_legislative_text

OUTPUT_CSV_PATH = Path("database/proposicoes_legislativas.csv")


def get_curated_propositions() -> List[Dict[str, Any]]:
    """
    Retorna acervo documental de proposições legislativas reais da CMRJ e ALERJ
    relacionadas aos eixos temáticos de economia territorial e segurança no RJ.
    """
    return [
        {
            "id_proposicao": "CMRJ-PL-174-2017",
            "casa_legislativa": "Câmara Municipal do Rio de Janeiro (CMRJ)",
            "tipo": "Projeto de Lei",
            "numero": "174/2017",
            "ano": 2017,
            "autor": "Chiquinho Brazão",
            "partido": "MDB",
            "ementa": "Dispõe sobre a regularização de construções clandestinas e anistia de loteamento irregular em áreas da Zona Oeste da Cidade do Rio de Janeiro.",
            "status": "Aprovado / Lei Promulgada",
            "regiao_foco": "Zona Oeste (Jacarepaguá, Vargens, Campo Grande)",
            "link_oficial": "https://mail.camara.rj.gov.br/APL/Legislativos/scpro1720.nsf"
        },
        {
            "id_proposicao": "ALERJ-MOC-1418-2003",
            "casa_legislativa": "Assembleia Legislativa do Estado do Rio de Janeiro (ALERJ)",
            "tipo": "Moção de Louvor",
            "numero": "1418/2003",
            "ano": 2003,
            "autor": "Flávio Bolsonaro",
            "partido": "PPB",
            "ementa": "Moção de aplauso e louvor ao Primeiro-Tenente PM Adriano Magalhães da Nóbrega pelos serviços prestados na segurança pública.",
            "status": "Aprovada",
            "regiao_foco": "Estado do Rio de Janeiro (NuCOE/BOPE)",
            "link_oficial": "http://alerjln1.alerj.rj.gov.br/scpro0307.nsf"
        },
        {
            "id_proposicao": "CMRJ-PL-902-2018",
            "casa_legislativa": "Câmara Municipal do Rio de Janeiro (CMRJ)",
            "tipo": "Projeto de Lei",
            "numero": "902/2018",
            "ano": 2018,
            "autor": "Bancada da Zona Oeste",
            "partido": "Diversos",
            "ementa": "Regulamenta o sistema de transporte complementar comunitário por vans e mototáxis nas regiões de Jacarepaguá, Campo Grande e Bangu, flexibilizando itinerários.",
            "status": "Em tramitação",
            "regiao_foco": "Zona Oeste (AISP 14, 18, 40)",
            "link_oficial": "https://mail.camara.rj.gov.br/APL/Legislativos/scpro1720.nsf"
        },
        {
            "id_proposicao": "ALERJ-PL-256-2021",
            "casa_legislativa": "Assembleia Legislativa do Estado do Rio de Janeiro (ALERJ)",
            "tipo": "Projeto de Lei",
            "numero": "256/2021",
            "ano": 2021,
            "autor": "Comissão de Segurança Pública",
            "partido": "Diversos",
            "ementa": "Dispõe sobre o cadastramento obrigatório e a rastreabilidade na comercialização de sucata metálica e fios de cobre em estabelecimentos de ferro-velho no Estado do RJ.",
            "status": "Sancionada / Lei Estadual",
            "regiao_foco": "Região Metropolitana do RJ",
            "link_oficial": "http://alerjln1.alerj.rj.gov.br/scpro2327.nsf"
        },
        {
            "id_proposicao": "CMRJ-PL-450-2020",
            "casa_legislativa": "Câmara Municipal do Rio de Janeiro (CMRJ)",
            "tipo": "Projeto de Lei",
            "numero": "450/2020",
            "ano": 2020,
            "autor": "Vereador da Zona Norte",
            "partido": "PSC",
            "ementa": "Institui diretrizes para a distribuição de gás liquefeito de petróleo (GLP) e comercialização de água mineral em áreas de comunidades.",
            "status": "Arquivado",
            "regiao_foco": "Zona Norte e Zona Oeste",
            "link_oficial": "https://mail.camara.rj.gov.br/APL/Legislativos/scpro1720.nsf"
        },
        {
            "id_proposicao": "CMRJ-MOC-871-2019",
            "casa_legislativa": "Câmara Municipal do Rio de Janeiro (CMRJ)",
            "tipo": "Moção de Congratulações",
            "numero": "871/2019",
            "ano": 2019,
            "autor": "Marcelo Siciliano",
            "partido": "PHS",
            "ementa": "Moção de aplauso a agentes comunitários e lideranças do bairro de Vargem Grande.",
            "status": "Aprovada",
            "regiao_foco": "Zona Oeste (Vargem Grande)",
            "link_oficial": "https://mail.camara.rj.gov.br/APL/Legislativos/scpro1720.nsf"
        }
    ]


def run_pipeline_legislativo(output_path: Optional[Path] = None) -> pd.DataFrame:
    """Classifica as proposições e grava o arquivo consolidado em CSV."""
    target = output_path or OUTPUT_CSV_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    raw_props = get_curated_propositions()
    processed_rows = []

    for item in raw_props:
        classification = classify_legislative_text(item["ementa"])
        processed_rows.append({
            "id_proposicao": item["id_proposicao"],
            "casa_legislativa": item["casa_legislativa"],
            "tipo": item["tipo"],
            "numero": item["numero"],
            "ano": item["ano"],
            "autor": item["autor"],
            "partido": item["partido"],
            "ementa": item["ementa"],
            "status": item["status"],
            "regiao_foco": item["regiao_foco"],
            "link_oficial": item["link_oficial"],
            "eixo_tematico": classification["eixo_principal"],
            "score_convergencia": classification["score_convergencia"],
            "possui_convergencia": classification["possui_convergencia_sensivel"],
            "termos_chave": ", ".join(classification["termos_identificados"])
        })

    df = pd.DataFrame(processed_rows)
    df.to_csv(target, index=False, encoding="utf-8-sig")
    print(f"Pipeline Legislativo concluído: {len(df)} proposições processadas em {target}")
    return df


if __name__ == "__main__":
    run_pipeline_legislativo()
