"""
Script para popular o banco com dados de teste [DEMO].
Regra: Todos os dados fictícios possuem is_demo=True e tag [DEMO] no título.
Nunca confundir com dados de pesquisa histórica real.
"""
import sys

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


def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Limpa dados DEMO anteriores se existirem
        db.query(Event).filter(Event.is_demo == True).delete()
        db.query(Source).filter(Source.is_demo == True).delete()
        db.query(Person).filter(Person.is_demo == True).delete()
        db.query(Organization).filter(Organization.is_demo == True).delete()
        db.query(Region).filter(Region.is_demo == True).delete()
        db.commit()

        print("Populando dados [DEMO] para validação técnica do MVP...")

        # 1. Regiões do Rio de Janeiro (com coordenadas reais)
        regions_data = [
            Region(name="Centro", region_type="bairro", municipality="Rio de Janeiro", latitude=-22.9035, longitude=-43.1824, description="Área central administrativa e comercial do RJ", is_demo=True),
            Region(name="Copacabana", region_type="bairro", municipality="Rio de Janeiro", latitude=-22.9698, longitude=-43.1868, description="Zona Sul litorânea do RJ", is_demo=True),
            Region(name="Tijuca", region_type="bairro", municipality="Rio de Janeiro", latitude=-22.9242, longitude=-43.2328, description="Zona Norte tradicional", is_demo=True),
            Region(name="Maré", region_type="complexo", municipality="Rio de Janeiro", latitude=-22.8580, longitude=-43.2450, description="Complexo de comunidades na Zona Norte", is_demo=True),
            Region(name="São Cristóvão", region_type="bairro", municipality="Rio de Janeiro", latitude=-22.8988, longitude=-43.2215, description="Zona Norte, área histórica e de pavilhões", is_demo=True),
            Region(name="Barra da Tijuca", region_type="bairro", municipality="Rio de Janeiro", latitude=-23.0003, longitude=-43.3659, description="Zona Oeste do RJ", is_demo=True),
            Region(name="Duque de Caxias", region_type="municipio", municipality="Duque de Caxias", latitude=-22.7856, longitude=-43.3117, description="Baixada Fluminense", is_demo=True),
            Region(name="Niterói", region_type="municipio", municipality="Niterói", latitude=-22.8859, longitude=-43.1153, description="Região Metropolitana Leste", is_demo=True),
            Region(name="Madureira", region_type="bairro", municipality="Rio de Janeiro", latitude=-22.8717, longitude=-43.3396, description="Polo cultural e comercial da Zona Norte", is_demo=True),
        ]
        db.add_all(regions_data)
        db.flush()

        # 2. Organizações [DEMO]
        orgs_data = [
            Organization(name="[DEMO] Ordem dos Advogados Seccional RJ", acronym="OAB-RJ", org_type="sociedade_civil", notes="Entidade representativa dos advogados", is_demo=True),
            Organization(name="[DEMO] Delegacia Regional de Ordem Política e Social", acronym="DOPS-RJ", org_type="orgao_estatal", notes="Órgão de repressão e inteligência política", is_demo=True),
            Organization(name="[DEMO] Batalhão de Polícia Militar da Zona Sul", acronym="19-BPM", org_type="policial", notes="Comando de policiamento regional", is_demo=True),
            Organization(name="[DEMO] Sindicato dos Metalúrgicos do Rio", acronym="SindMetal-RJ", org_type="sindicato", notes="Organização sindical representativa da indústria naval e metalúrgica", is_demo=True),
            Organization(name="[DEMO] Associação de Moradores Unidos da Baixada", acronym="AMUB", org_type="sociedade_civil", notes="Coletivo comunitário popular", is_demo=True),
            Organization(name="[DEMO] Coletivo Cultural e Teatral Carioca", acronym="CCTC", org_type="sociedade_civil", notes="Grupo artístico independente", is_demo=True),
        ]
        db.add_all(orgs_data)
        db.flush()

        # 3. Pessoas / Lideranças [DEMO]
        people_data = [
            Person(name="[DEMO] Dra. Helena Vasconcelos", aliases="Helena da OAB", role_description="Advogada e defensora de direitos", notes="Atuante em habeas corpus", is_demo=True),
            Person(name="[DEMO] Comissário Roberto Albuquerque", aliases="Beto Investigador", role_description="Agente policial de investigações", notes="Lotado na delegacia central", is_demo=True),
            Person(name="[DEMO] Mário Santos da Silva", aliases="Mário Naval", role_description="Líder operário do setor naval", notes="Organizador de assembleias e greves", is_demo=True),
            Person(name="[DEMO] Prof.ª Clarice Guimarães", aliases="Prof. Clarice", role_description="Pesquisadora e historiadora", notes="Cronista documental", is_demo=True),
            Person(name="[DEMO] Sebastião Mendes", aliases="Tião da Associação", role_description="Líder comunitário local", notes="Coordenador de movimentos por saneamento e posse de terra", is_demo=True),
        ]
        db.add_all(people_data)
        db.flush()

        # 4. Fontes Documentadas [DEMO]
        sources_data = [
            Source(
                title="[DEMO] Relatório Anual da Comissão Arquivística de 1975",
                citation="COMISSÃO DE PESQUISA. Relatório do Fundo de Documentação Histórica (1975). Rio de Janeiro: Arquivo Público, 1976.",
                author="Comissão Arquivística",
                publication_year=1976,
                source_type="relatorio_oficial",
                archive_ref="Arquivo do Estado, Caixa 14, Documento 88",
                reliability_rating=5,
                is_demo=True,
            ),
            Source(
                title="[DEMO] Diário de Notícias Carioca - Edição Matutina (Maio 1978)",
                citation="DIÁRIO DE NOTÍCIAS. Cobertura da Paralisação Geral nos Estaleiros. Rio de Janeiro, ano 48, n. 1420, p. 1-3, 14 mai. 1978.",
                author="Redação Diário de Notícias",
                publication_year=1978,
                source_type="jornal",
                archive_ref="Hemeroteca Digital, Microfilme 1978-05",
                reliability_rating=4,
                is_demo=True,
            ),
            Source(
                title="[DEMO] Livro 'Vozes e Territórios da Guanabara'",
                citation="GUIMARÃES, Clarice. Vozes e Territórios da Guanabara: Conflitos e Memória (1970-1985). Rio de Janeiro: Editora Universitária, 1986.",
                author="Clarice Guimarães",
                publication_year=1986,
                source_type="livro",
                archive_ref="Biblioteca Nacional, Acervo Geral, 320.981 G963v",
                reliability_rating=5,
                is_demo=True,
            ),
            Source(
                title="[DEMO] Boletim Informativo da Ordem dos Advogados (1980)",
                citation="OAB-RJ. Boletim de Defesa das Garantias Fundamentais. Rio de Janeiro: Seccional RJ, n. 12, ago. 1980.",
                author="OAB Seccional RJ",
                publication_year=1980,
                source_type="documento_oficial",
                archive_ref="Acervo Histórico OAB, Pasta 1980-B",
                reliability_rating=5,
                is_demo=True,
            ),
            Source(
                title="[DEMO] Inquérito Policial de Ocorrência Especial n. 34/81",
                citation="SECRETARIA DE SEGURANÇA. Inquérito Policial sobre Incidente no Pavilhão de Eventos. Rio de Janeiro: Divisão de Registros, 1981.",
                author="Secretaria de Segurança",
                publication_year=1981,
                source_type="documento_oficial",
                archive_ref="Arquivo Público do Estado do RJ, Série Inquéritos, doc 34/81",
                reliability_rating=3,
                is_demo=True,
            ),
            Source(
                title="[DEMO] Depoimento Oral Registrado de Sebastião Mendes",
                citation="MENDES, Sebastião. Entrevista concedida ao Projeto Memória Popular da Baixada. Gravação em fita magnética, 18 out. 1984.",
                author="Sebastião Mendes / Núcleo de História Oral",
                publication_year=1984,
                source_type="depoimento",
                archive_ref="Arquivo Sonoro Comunitário, Fita 07-B",
                reliability_rating=4,
                is_demo=True,
            ),
        ]
        db.add_all(sources_data)
        db.flush()

        # Mapeamento auxiliar
        r = {reg.name: reg for reg in regions_data}
        o = {org.acronym: org for org in orgs_data}
        p = {pers.name: pers for pers in people_data}
        s = {src.title: src for src in sources_data}

        # 5. Eventos Documentados [DEMO]
        events_setup = [
            {
                "title": "[DEMO] Assembleia Sindical e Paralisação dos Operários Navais",
                "date_start": "1975-04-12",
                "year": 1975,
                "confidence_level": "confirmado",
                "description": "Reunião de trabalhadores do setor naval deliberando pauta de reivindicações salariais e melhores condições de segurança nos estaleiros da Baía de Guanabara.",
                "historical_context": "Período de recomposição gradual de movimentos sindicais e transição política no Rio de Janeiro pós-fusão dos estados.",
                "region": r["Niterói"],
                "orgs": [(o["SindMetal-RJ"], "organizador")],
                "people": [(p["[DEMO] Mário Santos da Silva"], "lideranca_operaria")],
                "source": s["[DEMO] Relatório Anual da Comissão Arquivística de 1975"],
                "excerpt": "Às 08h30 do dia 12 de abril de 1975, operários concentraram-se na praça do estaleiro em Niterói, votando a paralisação pacífica por unanimidade.",
                "page": "p. 45-47",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Abertura do Congresso Jurídico de Garantias Fundamentais",
                "date_start": "1977-08-20",
                "year": 1977,
                "confidence_level": "confirmado",
                "description": "Conferência de juristas no Centro do Rio de Janeiro discutindo a restauração do habeas corpus e garantias civis.",
                "historical_context": "Articulação de setores da sociedade civil e juristas pela anistia e fortalecimento das instituições jurídicas.",
                "region": r["Centro"],
                "orgs": [(o["OAB-RJ"], "organizador")],
                "people": [(p["[DEMO] Dra. Helena Vasconcelos"], "palestrante_defensora")],
                "source": s["[DEMO] Livro 'Vozes e Territórios da Guanabara'"],
                "excerpt": "O auditório da sede no Centro recebeu mais de quinhentos advogados em 20 de agosto de 1977 em defesa expressa das liberdades fundamentais.",
                "page": "p. 112",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Grande Mobilização Operária e Passeata em São Cristóvão",
                "date_start": "1978-05-14",
                "year": 1978,
                "confidence_level": "confirmado",
                "description": "Caminhada de operários e moradores partindo de São Cristóvão em direção ao centro comercial da cidade.",
                "historical_context": "Ano marcado por greves operárias e ressurgimento das manifestações de rua no eixo Rio-São Paulo.",
                "region": r["São Cristóvão"],
                "orgs": [(o["SindMetal-RJ"], "convocante"), (o["DOPS-RJ"], "monitoramento")],
                "people": [(p["[DEMO] Mário Santos da Silva"], "orador_principal"), (p["[DEMO] Comissário Roberto Albuquerque"], "agente_monitoramento")],
                "source": s["[DEMO] Diário de Notícias Carioca - Edição Matutina (Maio 1978)"],
                "excerpt": "A marcha que partiu do bairro de São Cristóvão reuniu cerca de três mil trabalhadores com faixas reivindicando reposição inflacionária.",
                "page": "p. 1",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Incidente e Explosão de Artefato em Evento Comunitário",
                "date_start": "1981-04-30",
                "year": 1981,
                "confidence_level": "conflitante",
                "description": "Explosão de dispositivo explosivo nas imediações do pavilhão de convenções na Barra da Tijuca durante comemoração com milhares de pessoas.",
                "historical_context": "Tensões entre setores radicais contrários à abertura política e movimentos populares durante o processo de redemocratização.",
                "region": r["Barra da Tijuca"],
                "orgs": [(o["DOPS-RJ"], "orgao_investigador"), (o["OAB-RJ"], "comissao_independente")],
                "people": [(p["[DEMO] Dra. Helena Vasconcelos"], "observadora_juridica"), (p["[DEMO] Comissário Roberto Albuquerque"], "perito_policial")],
                "source": s["[DEMO] Inquérito Policial de Ocorrência Especial n. 34/81"],
                "excerpt": "Relatório preliminar sustenta versão de ataque externo, enquanto testemunhas oculares e laudos independentes apontam detonação acidental em veículo oficial.",
                "page": "Folhas 12-28",
                "status": "conflitante",
            },
            {
                "title": "[DEMO] Reunião de Formação da Associação de Moradores na Baixada",
                "date_start": "1983-03-15",
                "year": 1983,
                "confidence_level": "confirmado",
                "description": "Fundação formal da rede de comitês de bairro para reivindicar saneamento básico, eletrificação e regularização fundiária.",
                "historical_context": "Crescimento vigoroso dos movimentos de bairros periféricos na Baixada Fluminense durante a abertura eleitoral estadual.",
                "region": r["Duque de Caxias"],
                "orgs": [(o["AMUB"], "fundadora")],
                "people": [(p["[DEMO] Sebastião Mendes"], "presidente_eleito")],
                "source": s["[DEMO] Depoimento Oral Registrado de Sebastião Mendes"],
                "excerpt": "Naquele 15 de março de 1983 juntamos delegados de doze loteamentos em Caxias para fundar a entidade e lutar pela água encanada.",
                "page": "Fita 07-B, min 14:30",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Festival Cultural de Rua e Mostra de Cinema Independente",
                "date_start": "1984-09-22",
                "year": 1984,
                "confidence_level": "provavel",
                "description": "Exibição ao ar livre de curtas-metragens e apresentações teatrais em praça pública de Madureira.",
                "historical_context": "Efervescência cultural e ocupação dos espaços públicos no período da campanha das Diretas Já.",
                "region": r["Madureira"],
                "orgs": [(o["CCTC"], "produtor_cultural")],
                "people": [(p["[DEMO] Prof.ª Clarice Guimarães"], "curadora_historica")],
                "source": s["[DEMO] Livro 'Vozes e Territórios da Guanabara'"],
                "excerpt": "A praça de Madureira transformou-se em palco comunitário acolhendo mais de duas mil pessoas para debates e projeções de filmes nacionais.",
                "page": "p. 240",
                "status": "provavel",
            },
            {
                "title": "[DEMO] Denúncia de Monitoramento Ilegal de Advogados e Entidades",
                "date_start": "1980-08-10",
                "year": 1980,
                "confidence_level": "confirmado",
                "description": "Publicação de dossiê contendo registros de vigilância policial e escutas telefônicas direcionadas a defensores de direitos humanos.",
                "historical_context": "Fase de transição com resistência de setores dos serviços de informações em encerrar a espionagem política.",
                "region": r["Centro"],
                "orgs": [(o["OAB-RJ"], "denunciante"), (o["DOPS-RJ"], "investigado")],
                "people": [(p["[DEMO] Dra. Helena Vasconcelos"], "relatora_denuncia")],
                "source": s["[DEMO] Boletim Informativo da Ordem dos Advogados (1980)"],
                "excerpt": "Registramos formalmente a existência de relatórios de vigilância sobre as dependências da instituição, violando as prerrogativas legais.",
                "page": "p. 4-6",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Encontro de Lideranças Comunitárias e Coletivos da Maré",
                "date_start": "1985-06-18",
                "year": 1985,
                "confidence_level": "confirmado",
                "description": "Encontro regional reunindo representantes de várias favelas e núcleos para elaboração de pauta urbana unificada.",
                "historical_context": "Período da Nova República e reorganização das federações comunitárias na capital fluminense.",
                "region": r["Maré"],
                "orgs": [(o["AMUB"], "convidada"), (o["CCTC"], "apoio_cultural")],
                "people": [(p["[DEMO] Sebastião Mendes"], "convidado_intersetorial"), (p["[DEMO] Prof.ª Clarice Guimarães"], "documentarista")],
                "source": s["[DEMO] Livro 'Vozes e Territórios da Guanabara'"],
                "excerpt": "Em junho de 1985, o encontro na Maré sintetizou a aliança entre movimentos da Zona Norte e da Baixada Fluminense.",
                "page": "p. 278",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Registro de Ocorrência Policial não Verificada em Copacabana",
                "date_start": "1979-11-05",
                "year": 1979,
                "confidence_level": "nao_verificado",
                "description": "Boato e informe anônimo de suposta panfletagem clandestina e tumulto em calçadão litorâneo, sem confirmação em prontuários formais.",
                "historical_context": "Circulação recorrente de informes anônimos e contra-informações nos arquivos da segurança.",
                "region": r["Copacabana"],
                "orgs": [(o["19-BPM"], "averiguador")],
                "people": [(p["[DEMO] Comissário Roberto Albuquerque"], "analista_informe")],
                "source": s["[DEMO] Diário de Notícias Carioca - Edição Matutina (Maio 1978)"],
                "excerpt": "Nota curta de coluna de segurança mencionando apuração de chamada anônima sem ocorrência confirmada.",
                "page": "p. 8",
                "status": "nao_verificado",
            }
        ]

        for item in events_setup:
            ev = Event(
                title=item["title"],
                date_start=item["date_start"],
                year=item["year"],
                confidence_level=item["confidence_level"],
                description=item["description"],
                historical_context=item["historical_context"],
                is_demo=True,
            )
            db.add(ev)
            db.flush()

            # Relacionamento de proveniência com a fonte
            ev_src = EventSource(
                event_id=ev.id,
                source_id=item["source"].id,
                page_or_section=item["page"],
                excerpt=item["excerpt"],
                claim_assertion=item["title"],
                validation_status=item["status"],
                confidence_notes=f"Registro DEMO de validação do ciclo metodológico ({item['status']}).",
            )
            db.add(ev_src)

            # Região
            ev_reg = EventRegion(
                event_id=ev.id,
                region_id=item["region"].id,
                specific_location_name=item["region"].name,
            )
            db.add(ev_reg)

            # Organizações
            for org_obj, role in item["orgs"]:
                ev_org = EventOrganization(
                    event_id=ev.id,
                    organization_id=org_obj.id,
                    role_in_event=role,
                )
                db.add(ev_org)

            # Pessoas
            for pers_obj, role in item["people"]:
                ev_pers = EventPerson(
                    event_id=ev.id,
                    person_id=pers_obj.id,
                    role_in_event=role,
                )
                db.add(ev_pers)

        db.commit()
        print(f"[OK] Sucesso: {len(events_setup)} eventos DEMO inseridos com proveniencia de fontes, organizacoes, pessoas e regioes!")

    except Exception as e:
        db.rollback()
        print(f"[ERRO] Falha ao popular banco: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
