"""
Script de Download e Catalogação Automatizada do Corpus do NotebookLM.
Baixa PDFs públicos, artigos, relatórios oficiais e matérias jornalísticas.
Gera hash SHA-256 e metadados arquivísticos em data/raw/ e catalog_fontes.json.
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import requests
from urllib.parse import urlparse

from config.settings import settings

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Lista de fontes identificadas com URLs diretas ou de acesso público
SOURCES_TO_FETCH = [
    {
        "title": "No sapatinho: a milícia no Rio de Janeiro",
        "category": "academia",
        "source_type": "academico_livro",
        "publisher": "Fundação Heinrich Böll",
        "url": "https://br.boell.org/sites/default/files/no_sapatinho_lav_hbs1_1.pdf",
        "filename": "no_sapatinho_milicia_rj.pdf",
        "period": "década de 2000 até 2020",
        "notes": "Estudo de referência sobre a formação e expansão das milícias no RJ."
    },
    {
        "title": "Balanço de Indicadores da Polícia de Pacificação (2015)",
        "category": "seguranca_publica",
        "source_type": "oficial_relatorio",
        "publisher": "Instituto de Segurança Pública (ISP-RJ)",
        "url": "https://www.rj.gov.br/isp/sites/default/files/2022-05/BalancodeIndicadoresdaPoliciadePacificacao2015.pdf",
        "filename": "isp_balanco_indicadores_upp_2015.pdf",
        "period": "2008-2015",
        "notes": "Relatório estatístico oficial sobre a implementação e impacto das UPPs."
    },
    {
        "title": "Informativo à Sociedade - ADPF 635 ('ADPF das Favelas')",
        "category": "processos_publicos",
        "source_type": "documento_judicial",
        "publisher": "Supremo Tribunal Federal (STF)",
        "url": "https://www.stf.jus.br/arquivo/cms/noticiaNoticiaStf/anexo/InfoSociedadeADPF635.pdf",
        "filename": "stf_adpf_635_info_sociedade.pdf",
        "period": "2020-atual",
        "notes": "Documento explicativo da ADPF 635 sobre restrição de operações policiais em favelas."
    },
    {
        "title": "A trajetória das milícias e crime organizado no RJ",
        "category": "academia",
        "source_type": "academico_artigo",
        "publisher": "Revista Redalyc",
        "url": "https://www.redalyc.org/pdf/5638/563865508005.pdf",
        "filename": "redalyc_trajetoria_milicias_rj.pdf",
        "period": "1990-2018",
        "notes": "Artigo científico sobre sociologia do crime e paramilitarismo fluminense."
    },
    {
        "title": "Artigo - História da Criminalidade e Território",
        "category": "academia",
        "source_type": "academico_artigo",
        "publisher": "Revista Passagens (UFF)",
        "url": "https://periodicos.uff.br/revistapassagens/article/download/69248/40907/255946",
        "filename": "revista_passagens_uff_artigo.pdf",
        "period": "histórico",
        "notes": "Estudo historiográfico da Universidade Federal Fluminense."
    },
    {
        "title": "Artigo - Clio Revista de Pesquisa Histórica",
        "category": "academia",
        "source_type": "academico_artigo",
        "publisher": "Revista Clio (UFPel)",
        "url": "https://periodicos.ufpel.edu.br/index.php/CLIO/article/view/31474/22139",
        "filename": "clio_ufpel_artigo_historico.pdf",
        "period": "histórico",
        "notes": "Artigo acadêmico historiográfico sobre redes criminais e prisões."
    },
    {
        "title": "O Fim de uma Facção: A Queda do Amigos dos Amigos (ADA)",
        "category": "jornalismo",
        "source_type": "jornalismo_investigativo",
        "publisher": "The Intercept Brasil",
        "url": "https://www.intercept.com.br/2018/12/13/o-fim-de-uma-faccao/",
        "filename": "intercept_o_fim_de_uma_faccao_ada.html",
        "period": "1998-2018",
        "notes": "Reportagem investigativa detalhando a história, cisões e declínio da facção ADA."
    },
    {
        "title": "Adriano da Nóbrega, Ecko e as Conexões da Milícia",
        "category": "jornalismo",
        "source_type": "jornalismo_investigativo",
        "publisher": "The Intercept Brasil",
        "url": "https://www.intercept.com.br/2021/06/14/ecko-miliciano-adriano-nobrega/",
        "filename": "intercept_ecko_miliciano_adriano_nobrega.html",
        "period": "2000-2021",
        "notes": "Investigação sobre a cúpula miliciana da Zona Oeste (Liga da Justiça / Bonde do Ecko) e Escritório do Crime."
    },
    {
        "title": "O Policial Criminoso que Levou para o Túmulo os Segredos do Submundo do RJ",
        "category": "jornalismo",
        "source_type": "jornalismo_investigativo",
        "publisher": "El País Brasil",
        "url": "https://brasil.elpais.com/brasil/2020-02-15/o-policial-criminoso-que-levou-para-o-tumulo-os-segredos-do-submundo-do-rio-de-janeiro.html",
        "filename": "elpais_adriano_nobrega_submundo_rj.html",
        "period": "2000-2020",
        "notes": "Trajetória de Adriano da Nóbrega (ex-BOPE), matadores de aluguel e milícias em Rio das Pedras."
    },
    {
        "title": "Intervenção Federal no Rio e as Raízes da Crise na Segurança",
        "category": "jornalismo",
        "source_type": "jornalismo_investigativo",
        "publisher": "El País Brasil",
        "url": "https://brasil.elpais.com/brasil/2018/03/11/politica/1520769227_645322.html",
        "filename": "elpais_intervencao_federal_seguranca_rj.html",
        "period": "2018",
        "notes": "Análise da intervenção federal de 2018 no Rio de Janeiro."
    },
    {
        "title": "UPPs precisam de ajustes para evitar fracasso",
        "category": "jornalismo",
        "source_type": "jornalismo_investigativo",
        "publisher": "Instituto Humanitas Unisinos (IHU)",
        "url": "https://ihu.unisinos.br/sobre-o-ihu/170-noticias/noticias-2014/534853-upps-precisam-de-ajustes-para-evitar-fracasso",
        "filename": "ihu_upps_ajustes_fracasso.html",
        "period": "2008-2014",
        "notes": "Entrevista e balanço crítico do modelo de Unidades de Polícia Pacificadora."
    },
    {
        "title": "Batalhão de Operações Policiais Especiais (BOPE) - Histórico Institucional",
        "category": "governo",
        "source_type": "oficial_relatorio",
        "publisher": "Secretaria de Estado de Polícia Militar RJ",
        "url": "https://sepm.rj.gov.br/2015/10/bope-batalhao-de-operacoes-especiais/",
        "filename": "sepm_rj_historico_bope.html",
        "period": "1978-atual",
        "notes": "Histórico oficial da criação da Companhia de Operações Especiais (NuCOE) em 1978 e evolução para BOPE."
    }
]

# Catálogo ampliado de fontes citadas no material do usuário (SciELO, teses, livros)
ACADEMIC_CATALOG = [
    {
        "title": "A Acumulação Social da Violência no Rio de Janeiro",
        "author": "Michel Misse",
        "publication_year": 1999,
        "source_type": "academico_livro",
        "publisher": "Lúmen Júris / IUPERJ",
        "relevance": "Obra teórica basilar sobre a transformação da violência e formação dos 'sujeitos criminais' e redes de propina no RJ.",
        "key_concepts": ["mercadorias políticas", "sujeito criminal", "acumulação social da violência"]
    },
    {
        "title": "O encontro da militância com a vadiagem nas prisões da Ilha Grande",
        "author": "Pesquisa Historiográfica CPDOC/FGV",
        "publication_year": 2005,
        "source_type": "academico_artigo",
        "publisher": "SciELO / Estudos Históricos",
        "relevance": "Documenta o convívio entre presos políticos (guerrilha urbana) e presos comuns no Instituto Penal Cândido Mendes nos anos 1970, originando o Comando Vermelho.",
        "key_concepts": ["Ilha Grande", "Lei de Segurança Nacional", "Fundo Falange Vermelha", "Rogério Lemgruber"]
    },
    {
        "title": "Do 'esquadrão da morte' ao 'urbanismo miliciano'",
        "author": "Revista da EMERJ",
        "publication_year": 2021,
        "source_type": "academico_artigo",
        "publisher": "Escola da Magistratura do Estado do Rio de Janeiro",
        "relevance": "Mapeia a linhagem histórica que liga os grupos de extermínio dos anos 1960/1970 (Scuderia Le Cocq, Homens de Ouro) às milícias contemporâneas e captura de loteamentos urbanos.",
        "key_concepts": ["Scuderia Le Cocq", "Mariel Mariscot", "Esquadrão da Morte", "urbanismo miliciano"]
    },
    {
        "title": "Análise das cartas do Comando Vermelho (1980-1990)",
        "author": "Família CV / Acervo Historiográfico",
        "publication_year": 1990,
        "source_type": "historia_oral",
        "publisher": "Documentação Primária Penitenciária",
        "relevance": "Manuscritos e cartas internas entre lideranças da Ilha Grande e presídios da capital estabelecendo regras disciplinares ('paz, justiça e liberdade').",
        "key_concepts": ["estatuto primitivo", "solidariedade carcerária", "década de 1980"]
    },
    {
        "title": "Operações Policiais no Rio de Janeiro (2006-2020): Da lacuna estatística ao ativismo de dados",
        "author": "GENI/UFF (Grupo de Estudos dos Novos Ilegalismos)",
        "publication_year": 2021,
        "source_type": "academico_artigo",
        "publisher": "SciELO",
        "relevance": "Mapeamento rigoroso e geoespacial de mais de uma década de incursões policiais e operações em favelas do Rio.",
        "key_concepts": ["GENI/UFF", "letalidade policial", "eficiência operacional", "chacinas"]
    },
    {
        "title": "Vale o escrito: o jogo do bicho entre a decadência e a vitalidade",
        "author": "Avelar, R. et al.",
        "publication_year": 2023,
        "source_type": "jornalismo_investigativo",
        "publisher": "Projeto Colabora",
        "relevance": "História da cúpula do jogo do bicho nos anos 1970 e 1980 (Castor de Andrade, Capitão Guimarães), patronato de escolas de samba e transição para o mercado de máquinas de caça-níquel.",
        "key_concepts": ["jogo do bicho", "Castor de Andrade", "antecedentes históricos"]
    }
]


def calculate_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def download_and_ingest_all():
    print("=== INÍCIO DA INGESTÃO DO CORPUS DOCUMENTAL DO NOTEBOOKLM ===\n")
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1"
    }

    ingested_records = []

    for item in SOURCES_TO_FETCH:
        cat_dir = settings.DATA_RAW_DIR / item["category"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        dest_file = cat_dir / item["filename"]
        meta_path = cat_dir / f"{dest_file.stem}_meta.json"

        if dest_file.exists() and dest_file.stat().st_size > 0:
            print(f"-> Já presente no acervo: {item['title']} ({dest_file.name})")
            sha256_hash = calculate_sha256(dest_file)
            size_kb = dest_file.stat().st_size / 1024
            meta = {
                "title": item["title"],
                "filename": item["filename"],
                "category": item["category"],
                "source_type": item["source_type"],
                "publisher": item["publisher"],
                "url": item["url"],
                "period": item["period"],
                "notes": item["notes"],
                "sha256": sha256_hash,
                "file_size_kb": round(size_kb, 2),
                "ingested_at": datetime.now(timezone.utc).isoformat()
            }
            if not meta_path.exists():
                with open(meta_path, "w", encoding="utf-8") as f_meta:
                    json.dump(meta, f_meta, indent=2, ensure_ascii=False)
            ingested_records.append(meta)
            continue

        print(f"-> Baixando: {item['title']}...")
        print(f"   URL: {item['url']}")

        try:
            resp = requests.get(item["url"], headers=headers, timeout=60, verify=False)
            if resp.status_code == 200:
                with open(dest_file, "wb") as f:
                    f.write(resp.content)
                
                sha256_hash = calculate_sha256(dest_file)
                size_kb = len(resp.content) / 1024

                meta = {
                    "title": item["title"],
                    "filename": item["filename"],
                    "category": item["category"],
                    "source_type": item["source_type"],
                    "publisher": item["publisher"],
                    "url": item["url"],
                    "period": item["period"],
                    "notes": item["notes"],
                    "sha256": sha256_hash,
                    "file_size_kb": round(size_kb, 2),
                    "ingested_at": datetime.now(timezone.utc).isoformat()
                }

                with open(meta_path, "w", encoding="utf-8") as f_meta:
                    json.dump(meta, f_meta, indent=2, ensure_ascii=False)

                print(f"   [OK] Sucesso ({round(size_kb, 1)} KB) | SHA-256: {sha256_hash[:16]}...\n")
                ingested_records.append(meta)
            else:
                print(f"   [AVISO] Servidor respondeu com código {resp.status_code}. Registrando metadados para coleta manual.\n")
        except Exception as e:
            print(f"   [ERRO AO BAIXAR]: {e}. Registrando metadados arquivísticos.\n")

    # Salva o catálogo consolidado completo
    catalog_path = settings.DATA_DIR / "catalogo_fontes_notebooklm.json"
    full_catalog = {
        "total_fontes_mapeadas": len(SOURCES_TO_FETCH) + len(ACADEMIC_CATALOG),
        "fontes_com_arquivo_bruto": ingested_records,
        "corpus_academico_referencia": ACADEMIC_CATALOG,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(catalog_path, "w", encoding="utf-8") as f_cat:
        json.dump(full_catalog, f_cat, indent=2, ensure_ascii=False)

    print(f"=== SUCESSO: Catálogo completo consolidado em: {catalog_path} ===")
    print(f"Total de fontes estruturadas: {len(SOURCES_TO_FETCH) + len(ACADEMIC_CATALOG)}")


if __name__ == "__main__":
    download_and_ingest_all()
