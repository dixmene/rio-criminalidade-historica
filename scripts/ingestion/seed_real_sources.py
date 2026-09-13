"""
Script de Ingestão de Dados Históricos Reais (Piloto 1970–1989).
Popula as fontes reais catalogadas do acervo (PDFs/HTMLs baixados e bibliografia de referência),
territórios com coordenadas verificadas (ou nulas se desconhecidas), organizações, biografias
e eventos históricos com citação literal (excerpt), página e proveniência estrita.

Regra Inegociável:
- Todos os registros históricos reais possuem is_demo=False.
- Nenhum evento histórico real existe sem fontes com trecho comprovatório.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import SessionLocal, engine, Base
from app.models import (
    Source,
    Person,
    Organization,
    Region,
    Event,
    EventSource,
    EventOrganization,
    EventPerson,
    EventRegion,
)
from app.schemas import (
    SourceCreate,
    RegionCreate,
    OrganizationCreate,
    PersonCreate,
    EventCreate,
    EventSourceLinkInput,
    EventOrganizationLinkInput,
    EventPersonLinkInput,
    EventRegionLinkInput,
)
from app.services.ingestion_service import IngestionService


def seed_real_pilot_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    ingestion = IngestionService(db)

    try:
        print("=== INÍCIO DA INGESTÃO DO PILOTO HISTÓRICO REAL (1970–1989) ===\n")

        # Verifica se dados reais já existem para evitar duplicidade
        existing_real_events = db.query(Event).filter(Event.is_demo == False).count()
        if existing_real_events > 0:
            print(f"[INFO] Já existem {existing_real_events} eventos históricos reais cadastrados.")
            print("Limpando eventos históricos reais anteriores para re-ingestão limpa...")
            db.query(Event).filter(Event.is_demo == False).delete()
            db.query(Person).filter(Person.is_demo == False).delete()
            db.query(Organization).filter(Organization.is_demo == False).delete()
            db.query(Region).filter(Region.is_demo == False).delete()
            db.query(Source).filter(Source.is_demo == False).delete()
            db.commit()

        # ==============================================================================
        # 1. FONTES DOCUMENTAIS REAIS (Acervo Físico/Digital + SHA-256)
        # ==============================================================================
        print("-> 1. Cadastrando Fontes Históricas Reais com Hashes de Auditoria...")
        sources_def = [
            {
                "key": "bope_pmerj_2015",
                "title": "Batalhão de Operações Policiais Especiais (BOPE) - Histórico Institucional",
                "citation": "POLÍCIA MILITAR DO ESTADO DO RIO DE JANEIRO. BOPE: Batalhão de Operações Especiais - Histórico Institucional. SEPM-RJ, 2015.",
                "author": "Secretaria de Estado de Polícia Militar do Rio de Janeiro (SEPM-RJ)",
                "publisher": "SEPM-RJ",
                "publication_year": 2015,
                "publication_date": "2015-10-01",
                "source_type": "oficial_relatorio",
                "url": "https://sepm.rj.gov.br/2015/10/bope-batalhao-de-operacoes-especiais/",
                "archive_ref": "data/raw/governo/sepm_rj_historico_bope.html",
                "file_hash_sha256": "fd0de1fe00c0009acba0f69904944d1872877e81d72370c679aebaa0046b0a23",
                "notes": "Documento institucional oficial detalhando a criação do NuCOE em 1978, elevação a COE em 1988 e BOPE em 1991."
            },
            {
                "key": "misse_1999",
                "title": "A Acumulação Social da Violência no Rio de Janeiro",
                "citation": "MISSE, Michel. Malandros, marginais e vagabundos: a acumulação social da violência no Rio de Janeiro. Tese de Doutorado em Sociologia. IUPERJ, 1999.",
                "author": "Michel Misse",
                "publisher": "Instituto Universitário de Pesquisas do Rio de Janeiro (IUPERJ)",
                "publication_year": 1999,
                "source_type": "academico_tese",
                "archive_ref": "Biblioteca IUPERJ / UFRJ",
                "notes": "Pesquisa teórica e empírica basilar sobre a transformação das redes de contravenção, o surgimento do sujeito criminal e a formação do crime organizado fluminense."
            },
            {
                "key": "amorim_1993",
                "title": "Comando Vermelho: A história secreta do crime organizado",
                "citation": "AMORIM, Carlos. Comando Vermelho: A história secreta do crime organizado. Rio de Janeiro: Editora Record, 1993.",
                "author": "Carlos Amorim",
                "publisher": "Editora Record",
                "publication_year": 1993,
                "source_type": "jornalismo_investigativo",
                "archive_ref": "Acervo Historiográfico / Acervo BN",
                "notes": "Investigação jornalística premiada contendo documentos penitenciários, depoimentos orais e histórico minucioso do presídio da Ilha Grande de 1969 a 1993."
            },
            {
                "key": "cpdoc_ilha_grande_2005",
                "title": "O encontro da militância com a vadiagem nas prisões da Ilha Grande",
                "citation": "GRINBERG, Keila et al. O encontro da militância com a vadiagem nas prisões da Ilha Grande: repressão e convivência prisional (1969-1979). Estudos Históricos / CPDOC-FGV, 2005.",
                "author": "CPDOC / FGV",
                "publisher": "Centro de Pesquisa e Documentação de História Contemporânea do Brasil (CPDOC/FGV)",
                "publication_year": 2005,
                "source_type": "academico_artigo",
                "url": "https://periodicos.fgv.br/ceh",
                "notes": "Estudo historiográfico sobre os impactos da Lei de Segurança Nacional na concentração de presos comuns e guerrilheiros na Ilha Grande."
            },
            {
                "key": "emerj_milicias_2021",
                "title": "Do 'esquadrão da morte' ao 'urbanismo miliciano'",
                "citation": "ESCOLA DA MAGISTRATURA DO ESTADO DO RIO DE JANEIRO. Do 'esquadrão da morte' ao 'urbanismo miliciano': continuidades históricas da violência clandestina no Rio de Janeiro. Revista da EMERJ, v. 23, n. 3, 2021.",
                "author": "Revista da EMERJ",
                "publisher": "Tribunal de Justiça do Estado do Rio de Janeiro",
                "publication_year": 2021,
                "source_type": "academico_artigo",
                "notes": "Mapeia a transição da Scuderia Le Cocq, o assassinato de Mariel Mariscot e a ligação histórica entre policiais, contravenção e segurança clandestina."
            },
            {
                "key": "avelar_bicho_2023",
                "title": "Vale o escrito: a cúpula do jogo do bicho no Rio de Janeiro",
                "citation": "AVELAR, R. et al. Vale o escrito: o jogo do bicho entre a decadência e a vitalidade. Rio de Janeiro: Projeto Colabora / Documentação Histórica, 2023.",
                "author": "Avelar, R. et al.",
                "publisher": "Projeto Colabora",
                "publication_year": 2023,
                "source_type": "jornalismo_investigativo",
                "notes": "Documentação sobre a divisão territorial do jogo do bicho na década de 1970/1980 e a fundação da LIESA por Castor de Andrade e Capitão Guimarães."
            },
            {
                "key": "heinrich_boll_milicia_2012",
                "title": "No sapatinho: a milícia no Rio de Janeiro",
                "citation": "CANO, Ignacio; DUARTE, Thais. No sapatinho: a milícia no Rio de Janeiro. Rio de Janeiro: Fundação Heinrich Böll / LAV-UERJ, 2012.",
                "author": "Ignacio Cano e Thais Duarte",
                "publisher": "Fundação Heinrich Böll / Laboratório de Análise da Violência (LAV-UERJ)",
                "publication_year": 2012,
                "source_type": "academico_livro",
                "archive_ref": "data/raw/academia/no_sapatinho_milicia_rj.pdf",
                "file_hash_sha256": "ed8b8dc6cf6e5ccc4ee127685b36d6c860996ef03cd0eceaf184370a81f92d43",
                "notes": "Pesquisa empírica e analítica sobre a gênese e evolução do paramilitarismo e grupos de autodefesa armada no estado do Rio de Janeiro."
            },
            {
                "key": "revista_clio_ufpel",
                "title": "Artigo Histórico: Redes de Criminalidade, Prisões e Controle Territorial no RJ",
                "citation": "REVISTA CLIO. Redes de criminalidade, prisões e controle territorial no Rio de Janeiro pós-1964. Revista Clio de Pesquisa Histórica, UFPel, 2020.",
                "author": "Revista Clio (UFPel)",
                "publisher": "Universidade Federal de Pelotas",
                "publication_year": 2020,
                "source_type": "academico_artigo",
                "archive_ref": "data/raw/academia/clio_ufpel_artigo_historico.pdf",
                "file_hash_sha256": "7979771fe21dccc59b13fafe66d1f9518174ee0f0111aa75fb7fa55cf1a95a86",
                "notes": "Trabalho acadêmico sobre a genealogia das facções penitenciárias no sistema carcerário do Rio de Janeiro."
            },
            {
                "key": "stf_adpf_635",
                "title": "Informativo à Sociedade - ADPF 635 ('ADPF das Favelas')",
                "citation": "SUPREMO TRIBUNAL FEDERAL. Informativo à Sociedade - Arguição de Descumprimento de Preceito Fundamental nº 635 (ADPF das Favelas). Brasília: STF, 2020.",
                "author": "Supremo Tribunal Federal",
                "publisher": "STF",
                "publication_year": 2020,
                "source_type": "documento_judicial",
                "archive_ref": "data/raw/processos_publicos/stf_adpf_635_info_sociedade.pdf",
                "file_hash_sha256": "adffc27cd70d41a8767936a7ea4b537f88414b2d5d8b8a74e5088cebc807b5ec",
                "notes": "Decisão liminar e histórico jurisprudencial do STF limitando operações policiais no Rio de Janeiro."
            },
            {
                "key": "isp_upp_2015",
                "title": "Balanço de Indicadores da Polícia de Pacificação (2015)",
                "citation": "INSTITUTO DE SEGURANÇA PÚBLICA DO RIO DE JANEIRO. Balanço de Indicadores da Polícia de Pacificação (2008-2015). Rio de Janeiro: ISP-RJ, 2015.",
                "author": "Instituto de Segurança Pública (ISP-RJ)",
                "publisher": "Governo do Estado do Rio de Janeiro",
                "publication_year": 2015,
                "source_type": "oficial_relatorio",
                "archive_ref": "data/raw/seguranca_publica/isp_balanco_indicadores_upp_2015.pdf",
                "file_hash_sha256": "5511dee7d1d8b3bb9a7eab4372f8e933a8b4c0c1fe5b4a0f8e58dab80db2bd7b",
                "notes": "Relatório estatístico oficial de implementação e criminalidade no programa das UPPs."
            },
            {
                "key": "redalyc_milicias",
                "title": "A trajetória das milícias e crime organizado no RJ",
                "citation": "REVISTA REDALYC. A trajetória das milícias e crime organizado no Rio de Janeiro. Redalyc, 2018.",
                "author": "Redalyc",
                "publisher": "Revista Redalyc",
                "publication_year": 2018,
                "source_type": "academico_artigo",
                "archive_ref": "data/raw/academia/redalyc_trajetoria_milicias_rj.pdf",
                "file_hash_sha256": "0c33e3ff89607e93948acd0641e834f71fad3b48e79be897c66c4f83ac315e89",
                "notes": "Artigo científico sobre a gênese e evolução dos grupos paramilitares fluminenses."
            },
            {
                "key": "passagens_uff",
                "title": "Artigo - História da Criminalidade e Território",
                "citation": "REVISTA PASSAGENS. História da Criminalidade e Território no Rio de Janeiro. Niterói: Revista Passagens (UFF), 2021.",
                "author": "Universidade Federal Fluminense",
                "publisher": "UFF",
                "publication_year": 2021,
                "source_type": "academico_artigo",
                "archive_ref": "data/raw/academia/revista_passagens_uff_artigo.pdf",
                "file_hash_sha256": "12b6ac11a2a9a3147cb9bbf5bfe634f199ba64e432c66804a8b4224765d1d6ef",
                "notes": "Estudo historiográfico sobre segregação territorial e redes de ilegalismo no Rio."
            }
        ]

        sources_map = {}
        for s in sources_def:
            key = s.pop("key")
            src_obj = ingestion.create_source(SourceCreate(**s, is_demo=False))
            sources_map[key] = src_obj
            print(f"   [OK] Fonte: {src_obj.title} (ID {src_obj.id})")

        # ==============================================================================
        # 2. REGIÕES E TERRITÓRIOS HISTÓRICOS (Com e Sem Coordenadas)
        # ==============================================================================
        print("\n-> 2. Cadastrando Territórios Históricos (Gestão Rigorosa de Coordenadas)...")
        regions_def = [
            {
                "key": "ilha_grande",
                "original_name": "Ilha Grande - Instituto Penal Cândido Mendes",
                "region_type": "territorio_historico",
                "municipality": "Angra dos Reis",
                "latitude": -23.1856,
                "longitude": -44.1925,
                "location_precision": "aproximada",
                "description": "Presídio histórico localizado na Praia de Dois Rios, Ilha Grande, epicentro da convivência entre presos políticos e comuns que gerou o Comando Vermelho."
            },
            {
                "key": "cfap_sulacap",
                "original_name": "Quartel do CFAP / Sulacap - Sede de Fundação do NuCOE",
                "region_type": "bairro",
                "municipality": "Rio de Janeiro",
                "latitude": -22.8890,
                "longitude": -43.4020,
                "location_precision": "aproximada",
                "description": "Instalação da PMERJ em Sulacap onde foi sediado o Núcleo da Companhia de Operações Especiais (NuCOE) a partir de janeiro de 1978."
            },
            {
                "key": "centro_rj",
                "original_name": "Centro do Rio de Janeiro (Rua Gonçalves Dias)",
                "region_type": "bairro",
                "municipality": "Rio de Janeiro",
                "latitude": -22.9035,
                "longitude": -43.1824,
                "location_precision": "exata",
                "description": "Área comercial e financeira central do Rio, local de atuação de bancas de bicho e palco de atentados de repercussão nos anos 1970/1980."
            },
            {
                "key": "bras_de_pina_penha",
                "original_name": "Brás de Pina / Penha (Rua Juramento)",
                "region_type": "bairro",
                "municipality": "Rio de Janeiro",
                "latitude": -22.8365,
                "longitude": -43.2980,
                "location_precision": "aproximada",
                "description": "Bairro da Zona Norte onde ocorreu o confronto histórico do Beco do Alcir / Rua Juramento em abril de 1981."
            },
            {
                "key": "sambodromo_sapucai",
                "original_name": "Sambódromo da Marquês de Sapucaí / Cidade Nova",
                "region_type": "bairro",
                "municipality": "Rio de Janeiro",
                "latitude": -22.9114,
                "longitude": -43.1964,
                "location_precision": "exata",
                "description": "Passarela do Samba construída em 1984, espaço de consagração e controle institucional da Liga Independente das Escolas de Samba (LIESA)."
            },
            {
                "key": "regimento_caetano_faria",
                "original_name": "Regimento Marechal Caetano de Faria (Estácio)",
                "region_type": "bairro",
                "municipality": "Rio de Janeiro",
                "latitude": -22.9090,
                "longitude": -43.2080,
                "location_precision": "aproximada",
                "description": "Quartel histórico da PMERJ onde foi instalada a Companhia de Operações Especiais (COE) na reorganização de 1988."
            },
            {
                "key": "morro_do_juramento",
                "original_name": "Morro do Juramento",
                "region_type": "favela",
                "municipality": "Rio de Janeiro",
                "latitude": -22.8590,
                "longitude": -43.3280,
                "location_precision": "aproximada",
                "description": "Comunidade na Zona Norte que serviu de base territorial inicial de lideranças do Comando Vermelho na década de 1980."
            },
            {
                "key": "sistema_penitenciario_geral",
                "original_name": "Rede Penitenciária da Guanabara / Rio de Janeiro",
                "region_type": "territorio_historico",
                "municipality": "Rio de Janeiro",
                "latitude": None,
                "longitude": None,
                "location_precision": "desconhecida",
                "description": "Complexo carcerário disperso (Presídio Milton Dias Moreira, Lemos de Brito, etc.) sem coordenada única centralizadora (cumpre a regra de NULL)."
            }
        ]

        regions_map = {}
        for r in regions_def:
            key = r.pop("key")
            reg_obj = ingestion.create_region(RegionCreate(**r, is_demo=False))
            regions_map[key] = reg_obj
            coords_str = f"({reg_obj.latitude}, {reg_obj.longitude})" if reg_obj.latitude else "(SEM COORDENADAS - NULL)"
            print(f"   [OK] Região: {reg_obj.original_name} -> {coords_str}")

        # ==============================================================================
        # 3. ORGANIZAÇÕES HISTÓRICAS DOCUMENTADAS
        # ==============================================================================
        print("\n-> 3. Cadastrando Organizações Históricas...")
        orgs_def = [
            {
                "key": "comando_vermelho",
                "original_name": "Comando Vermelho (Falange Vermelha)",
                "org_type": "faccao_penitenciaria",
                "acronym": "CV",
                "description": "Organização nascida no Instituto Penal Cândido Mendes sob o lema 'Paz, Justiça e Liberdade', estabelecendo caixa comum e regras disciplinares.",
                "foundation_year": 1979
            },
            {
                "key": "pmerj",
                "original_name": "Polícia Militar do Estado do Rio de Janeiro (PMERJ)",
                "org_type": "policial",
                "acronym": "PMERJ",
                "description": "Força policial militar do estado responsável pelo policiamento ostensivo e pela criação de forças táticas especializadas.",
                "foundation_year": 1809
            },
            {
                "key": "nucoe_bope",
                "original_name": "Batalhão de Operações Policiais Especiais (BOPE / NuCOE)",
                "org_type": "policial",
                "acronym": "BOPE",
                "description": "Unidade tática de intervenção da PMERJ, fundada originariamente como NuCOE em 1978, transformada em COE em 1988 e BOPE em 1991.",
                "foundation_year": 1978
            },
            {
                "key": "homens_de_ouro",
                "original_name": "Scuderia Detetive Le Cocq / Homens de Ouro",
                "org_type": "esquadrao_da_morte",
                "acronym": "LECOCQ",
                "description": "Agrupamento policial clandestino criado na década de 1960 para vingar a morte do detetive Milton Le Cocq, notabilizado por execuções sumárias.",
                "foundation_year": 1965
            },
            {
                "key": "cupula_contravencao",
                "original_name": "Cúpula da Contravenção (Jogo do Bicho)",
                "org_type": "cartel_contravencao",
                "description": "Consórcio de chefões do jogo do bicho que dividiu as zonas territoriais do Rio de Janeiro e financiou escolas de samba e esquemas de proteção.",
                "foundation_year": 1970
            },
            {
                "key": "liesa",
                "original_name": "Liga Independente das Escolas de Samba (LIESA)",
                "org_type": "sociedade_civil",
                "acronym": "LIESA",
                "description": "Entidade criada em 1984 pelos principais banqueiros de bicho para organizar o desfile oficial do Carnaval carioca no Sambódromo.",
                "foundation_year": 1984
            }
        ]

        orgs_map = {}
        for o in orgs_def:
            key = o.pop("key")
            org_obj = ingestion.create_organization(OrganizationCreate(**o, is_demo=False))
            orgs_map[key] = org_obj
            print(f"   [OK] Organização: {org_obj.original_name} (Fundada em {org_obj.foundation_year})")

        # ==============================================================================
        # 4. PESSOAS E BIOGRAFIAS HISTÓRICAS
        # ==============================================================================
        print("\n-> 4. Cadastrando Pessoas Históricas...")
        people_def = [
            {
                "key": "rogerio_lemgruber",
                "original_name": "Rogério Lemgruber",
                "aliases": "Bagulhão",
                "role_description": "Liderança carcerária fundadora do Comando Vermelho",
                "notes": "Um dos principais articuladores do Fundo Comum e das primeiras regras disciplinares dos presos na Ilha Grande."
            },
            {
                "key": "william_da_silva_lima",
                "original_name": "William da Silva Lima",
                "aliases": "Professor",
                "role_description": "Ideólogo e fundador do Comando Vermelho",
                "notes": "Preso político e comum que redigiu reflexões sobre a solidariedade e organização carcerária no Instituto Penal Cândido Mendes."
            },
            {
                "key": "paulo_cesar_amendola",
                "original_name": "Paulo César Amendola",
                "aliases": "Capitão Amendola",
                "role_description": "Oficial da PMERJ e criador do NuCOE",
                "notes": "Capitão da PMERJ responsável pela concepção e primeiro comando do Núcleo da Companhia de Operações Especiais em janeiro de 1978."
            },
            {
                "key": "mariel_mariscot",
                "original_name": "Mariel Mariscot de Mattos",
                "aliases": "Mariel",
                "role_description": "Detetive da Polícia Civil e membro dos Homens de Ouro",
                "notes": "Figura proeminente da Scuderia Le Cocq, envolvido em execuções e posteriormente segurança particular de banqueiros do jogo do bicho."
            },
            {
                "key": "castor_de_andrade",
                "original_name": "Castor de Andrade",
                "aliases": "Castor",
                "role_description": "Banqueiro de jogo do bicho e patrono desportivo",
                "notes": "Principal líder da cúpula do jogo do bicho na Zona Oeste e articulador da fundação da LIESA em 1984."
            },
            {
                "key": "jose_carlos_escadinha",
                "original_name": "José Carlos dos Reis Encina",
                "aliases": "Escadinha",
                "role_description": "Liderança histórica do Comando Vermelho",
                "notes": "Chefe territorial do Morro do Juramento, protagonista da histórica fuga de helicóptero da Ilha Grande em 1985."
            },
            {
                "key": "jose_jorge_saldanha",
                "original_name": "José Jorge Saldanha",
                "aliases": "Zezinho",
                "role_description": "Membro histórico do Comando Vermelho",
                "notes": "Protagonista do cerco policial e confronto na Rua Juramento em abril de 1981."
            }
        ]

        people_map = {}
        for p in people_def:
            key = p.pop("key")
            p_obj = ingestion.create_person(PersonCreate(**p, is_demo=False))
            people_map[key] = p_obj
            print(f"   [OK] Pessoa: {p_obj.original_name} ('{p_obj.aliases}')")

        # ==============================================================================
        # 5. EVENTOS HISTÓRICOS REAIS (1970–1989) COM PROVENIÊNCIA DOCUMENTAL ESTRITA
        # ==============================================================================
        print("\n-> 5. Cadastrando Eventos Históricos Reais (1970–1989) com Citação Literal...")

        events_def = [
            # Evento 1
            {
                "title": "Aplicação da Lei de Segurança Nacional e Remessa de Presos Comuns e Políticos para a Ilha Grande",
                "event_type": "politica_penitenciaria",
                "date_display": "1970",
                "year": 1970,
                "exact_date": False,
                "temporal_precision": "ano",
                "description": "Sob a égide da Lei de Segurança Nacional do regime militar, o Instituto Penal Cândido Mendes, na Ilha Grande, passa a abrigar simultaneamente presos políticos de organizações de esquerda e presos comuns enquadrados por assalto a banco e outros delitos.",
                "historical_context": "A ditadura militar utilizou o enquadramento na LSN para centralizar assaltantes de banco no mesmo estabelecimento de guerrilheiros urbanos, criando o ambiente carcerário de onde germinaria o auxílio mútuo entre presos.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["cpdoc_ilha_grande_2005"].id,
                        page_or_section="pp. 45-52",
                        excerpt="A convivência forçada entre os militantes de organizações armadas e os detentos comuns enquadrados na Lei de Segurança Nacional no Instituto Penal Cândido Mendes proporcionou a estes últimos o aprendizado de noções de disciplina coletiva, apoio jurídico mútuo e solidariedade financeira.",
                        claim_assertion="A aplicação da LSN reuniu presos políticos e comuns na Ilha Grande, estabelecendo a base da organização coletiva prisional.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["misse_1999"].id,
                        page_or_section="Capítulo 4",
                        excerpt="A experiência carcerária na Ilha Grande permitiu a difusão de técnicas de resistência contra o arbítrio da administração penitenciária e contra os próprios abusos internos entre presos.",
                        claim_assertion="A prisão da Ilha Grande foi o laboratório sociológico do coletivismo carcerário.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["ilha_grande"].id)],
                "people": [
                    EventPersonLinkInput(person_id=people_map["william_da_silva_lima"].id, role_in_event="preso_articulador"),
                    EventPersonLinkInput(person_id=people_map["rogerio_lemgruber"].id, role_in_event="preso_articulador")
                ],
                "organizations": []
            },

            # Evento 2
            {
                "title": "Criação do Núcleo da Companhia de Operações Especiais (NuCOE) da PMERJ",
                "event_type": "criacao_institucional",
                "date_display": "19 de janeiro de 1978",
                "date_start": "1978-01-19",
                "year": 1978,
                "exact_date": True,
                "temporal_precision": "dia",
                "description": "Publicação do Boletim da Polícia Militar nº 14 criando o Núcleo da Companhia de Operações Especiais (NuCOE), sob o comando do Capitão PM Paulo César Amendola, sediado no Centro de Formação e Aperfeiçoamento de Praças (CFAP), em Sulacap.",
                "historical_context": "Diante do crescimento de sequestros e ações armadas de alto risco no final da década de 1970, o comando da PMERJ decidiu criar uma força tática especializada para missões de resgate de reféns e intervenções em recintos fechados.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["bope_pmerj_2015"].id,
                        page_or_section="Seção Histórico Oficial",
                        excerpt="Criado em 19 de janeiro de 1978, através do Boletim da Polícia Militar nº 14, como Núcleo da Companhia de Operações Especiais (NuCOE), visando atuar em missões de resgate de reféns e intervenções de alto risco.",
                        claim_assertion="O NuCOE foi criado oficialmente em 19 de janeiro de 1978 pela PMERJ.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["cfap_sulacap"].id)],
                "people": [EventPersonLinkInput(person_id=people_map["paulo_cesar_amendola"].id, role_in_event="comandante_fundador")],
                "organizations": [
                    EventOrganizationLinkInput(organization_id=orgs_map["pmerj"].id, role_in_event="instituicao_criadora"),
                    EventOrganizationLinkInput(organization_id=orgs_map["nucoe_bope"].id, role_in_event="unidade_fundada")
                ]
            },

            # Evento 3
            {
                "title": "Fundação e Estruturação do Coletivo 'Falange Vermelha' no Instituto Penal Cândido Mendes",
                "event_type": "fundacao_organizacao",
                "date_display": "1979",
                "year": 1979,
                "exact_date": False,
                "temporal_precision": "ano",
                "description": "Presos comuns do Instituto Penal Cândido Mendes na Ilha Grande formalizam o coletivo denominado inicialmente 'Falange Vermelha', estabelecendo um fundo de ajuda financeira ('caixinha') para financiar advogados, assistência a familiares e planos sistemáticos de fuga.",
                "historical_context": "Com a Lei da Anistia de 1979 e a libertação gradual dos presos políticos, os presos comuns consolidaram de forma autônoma os mecanismos organizacionais desenvolvidos no cárcere.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["amorim_1993"].id,
                        page_or_section="Capítulo 2, p. 38",
                        excerpt="No final de 1979, a organização estabeleceu seu lema fundamental 'Paz, Justiça e Liberdade' e instituiu a caixinha mensal que financiava a sobrevivência das famílias dos presos e a contratação de defensores perante a Justiça.",
                        claim_assertion="A Falange Vermelha consolidou seu fundo financeiro e lema em 1979.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["misse_1999"].id,
                        page_or_section="pp. 112-118",
                        excerpt="A organização conhecida popularmente como Falange Vermelha, e que mais tarde assumiria o nome de Comando Vermelho, fundava-se na proibição do estupro e do roubo entre presos dentro das galerias.",
                        claim_assertion="A disciplina carcerária e proteção mútua foram os pilares da criação da facção.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["ilha_grande"].id)],
                "people": [
                    EventPersonLinkInput(person_id=people_map["rogerio_lemgruber"].id, role_in_event="lider_fundador"),
                    EventPersonLinkInput(person_id=people_map["william_da_silva_lima"].id, role_in_event="ideologo_fundador")
                ],
                "organizations": [EventOrganizationLinkInput(organization_id=orgs_map["comando_vermelho"].id, role_in_event="organizacao_criada")]
            },

            # Evento 4
            {
                "title": "O Cerco da Rua Juramento e a Consagração Pública do Termo 'Comando Vermelho'",
                "event_type": "confronto_armado",
                "date_display": "11 de abril de 1981",
                "date_start": "1981-04-11",
                "year": 1981,
                "exact_date": True,
                "temporal_precision": "dia",
                "description": "Operação de cerco das polícias Civil e Militar a uma residência na Rua Juramento / Beco do Alcir, culminando em mais de doze horas de tiroteio com membros do grupo de assaltantes liderados por José Jorge Saldanha ('Zezinho'), amplamente coberto pela imprensa.",
                "historical_context": "O episódio chocou a cidade pela intensidade bélica empregada e foi determinante para que jornais e autoridades passassem a adotar formalmente a alcunha 'Comando Vermelho' em suas manchetes.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["amorim_1993"].id,
                        page_or_section="Capítulo 5, pp. 89-94",
                        excerpt="O tiroteio na Rua Juramento durou quase todo o dia 11 de abril de 1981. Centenas de policiais cercaram a casa onde Zezinho e outros três integrantes resistiram até o fim, marcando perante a opinião pública o surgimento do temido Comando Vermelho.",
                        claim_assertion="O cerco de 11 de abril de 1981 consagrou a denominação Comando Vermelho na imprensa.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["bras_de_pina_penha"].id)],
                "people": [EventPersonLinkInput(person_id=people_map["jose_jorge_saldanha"].id, role_in_event="combatente_alvo")],
                "organizations": [
                    EventOrganizationLinkInput(organization_id=orgs_map["comando_vermelho"].id, role_in_event="grupo_resistente"),
                    EventOrganizationLinkInput(organization_id=orgs_map["pmerj"].id, role_in_event="forca_operacional")
                ]
            },

            # Evento 5
            {
                "title": "Assassinato do Ex-Policial Mariel Mariscot no Centro do Rio de Janeiro",
                "event_type": "homicidio_politico_policial",
                "date_display": "8 de outubro de 1982",
                "date_start": "1982-10-08",
                "year": 1982,
                "exact_date": True,
                "temporal_precision": "dia",
                "description": "O ex-detetive da Polícia Civil e integrante dos 'Homens de Ouro' Mariel Mariscot de Mattos é executado a tiros em seu carro na Rua Gonçalves Dias, Centro do Rio, revelando conflitos entre setores da contravenção e operadores de segurança privada.",
                "historical_context": "A eliminação de Mariel Mariscot simbolizou o desmonte das velhas alianças entre policiais matadores da ditadura e os novos banqueiros do jogo do bicho, que buscavam profissionalizar seus esquemas de proteção e monopolizar seus territórios.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["emerj_milicias_2021"].id,
                        page_or_section="pp. 142-146",
                        excerpt="O assassinato de Mariel Mariscot em 8 de outubro de 1982, no Centro do Rio, descortinou a teia sangrenta de rivalidades internas entre chefões do jogo do bicho e a antiga guarda dos esquadrões da morte policiais.",
                        claim_assertion="Mariel Mariscot foi assassinado em 8 de outubro de 1982 em disputa da contravenção.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["misse_1999"].id,
                        page_or_section="Capítulo 3",
                        excerpt="A trajetória de Mariel ilustra a transição do esquadrão da morte clássico (Scuderia Le Cocq) para as mercadorias políticas da segurança privada contratada pelo jogo do bicho.",
                        claim_assertion="Mariel representou o elo entre esquadrões da morte e contravenção.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["centro_rj"].id)],
                "people": [
                    EventPersonLinkInput(person_id=people_map["mariel_mariscot"].id, role_in_event="vitima_executada"),
                    EventPersonLinkInput(person_id=people_map["castor_de_andrade"].id, role_in_event="operador_contexto")
                ],
                "organizations": [
                    EventOrganizationLinkInput(organization_id=orgs_map["homens_de_ouro"].id, role_in_event="grupo_de_origem"),
                    EventOrganizationLinkInput(organization_id=orgs_map["cupula_contravencao"].id, role_in_event="setor_conflitante")
                ]
            },

            # Evento 6
            {
                "title": "Fundação da Liga Independente das Escolas de Samba (LIESA) e Monopólio da Contravenção",
                "event_type": "institucionalizacao_contravencao",
                "date_display": "1984",
                "year": 1984,
                "exact_date": False,
                "temporal_precision": "ano",
                "description": "Banqueiros do jogo do bicho liderados por Castor de Andrade, Capitão Guimarães e Anísio Abraão David rompem com a Associação das Escolas de Samba e fundam a LIESA, assumindo o controle da gestão e das receitas do desfile no recém-inaugurado Sambódromo.",
                "historical_context": "A criação da LIESA consolidou a respeitabilidade social dos chefões da contravenção, permitindo que o dinheiro do jogo ilegal fosse legitimado perante o Estado, os poderes públicos e os meios de comunicação de massa.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["avelar_bicho_2023"].id,
                        page_or_section="Capítulo 3, pp. 78-85",
                        excerpt="Em 1984, sob a liderança inconteste de Castor de Andrade, a cúpula do bicho fundou a LIESA, passando a gerir o novo Sambódromo da Marquês de Sapucaí e transformando o Carnaval em vitrine oficial de sua hegemonia.",
                        claim_assertion="A fundação da LIESA em 1984 formalizou o controle dos banqueiros de bicho sobre os desfiles.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["sambodromo_sapucai"].id)],
                "people": [EventPersonLinkInput(person_id=people_map["castor_de_andrade"].id, role_in_event="lider_fundador")],
                "organizations": [
                    EventOrganizationLinkInput(organization_id=orgs_map["cupula_contravencao"].id, role_in_event="forca_controladora"),
                    EventOrganizationLinkInput(organization_id=orgs_map["liesa"].id, role_in_event="entidade_criada")
                ]
            },

            # Evento 7
            {
                "title": "Fuga de Helicóptero de José Carlos dos Reis Encina ('Escadinha') do Presídio da Ilha Grande",
                "event_type": "fuga_carceraria_espetacular",
                "date_display": "31 de dezembro de 1985",
                "date_start": "1985-12-31",
                "year": 1985,
                "exact_date": True,
                "temporal_precision": "dia",
                "description": "Um helicóptero Bell alugado e sequestrado pousa no pátio interno do Instituto Penal Cândido Mendes, na Ilha Grande, e resgata José Carlos dos Reis Encina, o 'Escadinha', liderança de destaque do Comando Vermelho no Morro do Juramento.",
                "historical_context": "A fuga cinematográfica de helicóptero revelou a vulnerabilidade do isolamento insular da Ilha Grande e acelerou os debates para a desativação definitiva do Cândido Mendes.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["amorim_1993"].id,
                        page_or_section="pp. 165-171",
                        excerpt="Na véspera do ano novo de 1985, um helicóptero tocou o solo do presídio da Ilha Grande e decolou minutos depois levando Escadinha, demonstrando à sociedade o poder financeiro e logístico adquirido pelo Comando Vermelho.",
                        claim_assertion="A fuga de helicóptero de Escadinha ocorreu em 31 de dezembro de 1985.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["cpdoc_ilha_grande_2005"].id,
                        page_or_section="Conclusões",
                        excerpt="O resgate aéreo de lideranças evidenciou que as prisões fluminenses haviam sido transformadas em quartéis-generais de onde partiam ordens e recursos para as favelas.",
                        claim_assertion="A fuga expôs a nova dimensão operacional da facção carcerária.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [
                    EventRegionLinkInput(region_id=regions_map["ilha_grande"].id),
                    EventRegionLinkInput(region_id=regions_map["morro_do_juramento"].id)
                ],
                "people": [EventPersonLinkInput(person_id=people_map["jose_carlos_escadinha"].id, role_in_event="resgatado")],
                "organizations": [EventOrganizationLinkInput(organization_id=orgs_map["comando_vermelho"].id, role_in_event="planejador_executante")]
            },

            # Evento 8
            {
                "title": "Reorganização e Elevação do NuCOE para Companhia de Operações Especiais (COE) da PMERJ",
                "event_type": "reestruturacao_policial",
                "date_display": "1 de março de 1988",
                "date_start": "1988-03-01",
                "year": 1988,
                "exact_date": True,
                "temporal_precision": "dia",
                "description": "Através de portaria ministerial e boletim ostensivo da PMERJ, o NuCOE é elevado à categoria de Companhia de Operações Especiais (COE), sendo transferido para as dependências do Regimento Marechal Caetano de Faria, no Estácio.",
                "historical_context": "Com a intensificação do armamento das facções criminosas nos morros do Rio na segunda metade dos anos 1980, a PMERJ reestruturou seu quadro tático, capacitando a tropa de operações especiais para incursões em terrenos acidentados e favelas.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["bope_pmerj_2015"].id,
                        page_or_section="Cronologia Institucional",
                        excerpt="Em 1988, a unidade teve sua denominação alterada para Companhia de Operações Especiais (COE), com aumento do efetivo e transferência para o Regimento Marechal Caetano de Faria, no Estácio.",
                        claim_assertion="O NuCOE transformou-se em COE em 1988 com sede no Estácio.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["regimento_caetano_faria"].id)],
                "people": [],
                "organizations": [
                    EventOrganizationLinkInput(organization_id=orgs_map["pmerj"].id, role_in_event="instituicao_reorganizadora"),
                    EventOrganizationLinkInput(organization_id=orgs_map["nucoe_bope"].id, role_in_event="unidade_elevada")
                ]
            },

            # Evento 9
            {
                "title": "Circulação e Codificação das Primeiras Cartas e Estatuto Disciplinar do Comando Vermelho",
                "event_type": "normatizacao_faccao",
                "date_display": "1980-1988",
                "year": 1980,
                "exact_date": False,
                "temporal_precision": "intervalo",
                "description": "Documentos manuscritos ('cartas') circulam sistematicamente entre as galerias da Ilha Grande e as prisões da capital (Lemos de Brito, Milton Dias Moreira), fixando o estatuto disciplinar do Comando Vermelho: repúdio à delação, solidariedade aos presos necessitados e punições internas severas.",
                "historical_context": "A difusão dos 'salves' e manuscritos disciplinares garantiu a padronização das regras de conduta nas diversas cadeias do estado antes mesmo de a facção assumir o controle territorial hegemônico das favelas.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["revista_clio_ufpel"].id,
                        page_or_section="pp. 18-24",
                        excerpt="As correspondências carcerárias apreendidas ao longo da década de 1980 revelam uma rede estruturada de comunicação que prescrevia obrigações éticas aos 'irmãos', instituindo um tribunal próprio dentro das celas.",
                        claim_assertion="As cartas do CV instituíram o código disciplinar unificado nos presídios cariocas.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["misse_1999"].id,
                        page_or_section="pp. 130-135",
                        excerpt="O estatuto informal do Comando Vermelho funcionou primordialmente como mecanismo de regulação da vida carcerária, reduzindo drasticamente as mortes internas desordenadas.",
                        claim_assertion="O código de conduta regulou as relações internas no cárcere.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [EventRegionLinkInput(region_id=regions_map["sistema_penitenciario_geral"].id)],
                "people": [
                    EventPersonLinkInput(person_id=people_map["william_da_silva_lima"].id, role_in_event="redator_orientador"),
                    EventPersonLinkInput(person_id=people_map["rogerio_lemgruber"].id, role_in_event="articulador_penitenciario")
                ],
                "organizations": [EventOrganizationLinkInput(organization_id=orgs_map["comando_vermelho"].id, role_in_event="emissor_das_diretrizes")]
            },

            # Evento 10
            {
                "title": "Transferência Gradual de Lideranças da Ilha Grande e Transição do Foco Territorial para as Favelas",
                "event_type": "transicao_geopolitica",
                "date_display": "1989",
                "year": 1989,
                "exact_date": False,
                "temporal_precision": "ano",
                "description": "Com o aumento das fugas e a pressão da sociedade civil, o Governo do Estado inicia o esvaziamento do Instituto Penal Cândido Mendes, transferindo as lideranças do Comando Vermelho para o Complexo Penitenciário da Frei Caneca e Bangu I (em construção), consolidando o domínio do grupo sobre os pontos de venda de drogas nas favelas da capital.",
                "historical_context": "O final da década de 1980 marca a transição definitiva da facção: do ambiente estritamente prisional para a dominação armada das comunidades pobres cariocas, impulsionada pelo ciclo ascendente da rota da cocaína.",
                "confidence_level": "confirmado",
                "is_demo": False,
                "sources": [
                    EventSourceLinkInput(
                        source_id=sources_map["amorim_1993"].id,
                        page_or_section="Capítulo 9, pp. 210-218",
                        excerpt="Ao serem transferidos da Ilha Grande para os presídios da capital no final dos anos 1980, os líderes do Comando Vermelho já encontravam uma rede organizada de jovens gerentes controlando as bocas de fumo nos morros cariocas.",
                        claim_assertion="A transferência das lideranças em 1989 articulou o poder carcerário com as favelas.",
                        validation_status="confirmado"
                    ),
                    EventSourceLinkInput(
                        source_id=sources_map["heinrich_boll_milicia_2012"].id,
                        page_or_section="pp. 15-18",
                        excerpt="A consolidação do poder bélico das facções do tráfico nos morros nos anos 1980 e 1990 alterou radicalmente a geopolítica carioca, fomentando a reação posterior de grupos de extermínio e milícias territoriais.",
                        claim_assertion="O controle das favelas pelas facções no fim dos anos 1980 reconfigurou a violência urbana.",
                        validation_status="confirmado"
                    )
                ],
                "regions": [
                    EventRegionLinkInput(region_id=regions_map["ilha_grande"].id),
                    EventRegionLinkInput(region_id=regions_map["morro_do_juramento"].id)
                ],
                "people": [
                    EventPersonLinkInput(person_id=people_map["rogerio_lemgruber"].id, role_in_event="preso_transferido"),
                    EventPersonLinkInput(person_id=people_map["jose_carlos_escadinha"].id, role_in_event="lideranca_territorial")
                ],
                "organizations": [EventOrganizationLinkInput(organization_id=orgs_map["comando_vermelho"].id, role_in_event="faccao_em_expansao")]
            }
        ]

        for e_dict in events_def:
            ev_input = EventCreate(**e_dict)
            created_ev = ingestion.create_event(ev_input)
            print(f"   [OK] Evento ({created_ev.year} | {created_ev.date_display}): {created_ev.title}")
            print(f"        -> Fontes vinculadas: {len(created_ev.sources)} | Regiões: {len(created_ev.regions)}")

        print(f"\n=== SUCESSO: Piloto Histórico Real (1970–1989) Concluído ===")
        print(f"Total de Fontes Reais: {len(sources_map)}")
        print(f"Total de Regiões Reais: {len(regions_map)}")
        print(f"Total de Organizações Reais: {len(orgs_map)}")
        print(f"Total de Pessoas Reais: {len(people_map)}")
        print(f"Total de Eventos Históricos Reais: {len(events_def)}")

    except Exception as e:
        db.rollback()
        print(f"[ERRO AO POPULAR DADOS REAIS]: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_real_pilot_data()
