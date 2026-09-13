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
from src.normalization.rules import (
    normalize_name,
    normalize_location,
    normalize_organization,
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

        # 1. Regiões do Rio de Janeiro
        # Inclui intencionalmente uma região SEM coordenadas para testar que o sistema
        # NÃO força coordenadas falsas quando o local não está cartograficamente delimitado!
        raw_regions = [
            ("Centro", "bairro", "Rio de Janeiro", -22.9035, -43.1824, "exata", "Área central administrativa e comercial"),
            ("Copacabana", "bairro", "Rio de Janeiro", -22.9698, -43.1868, "exata", "Zona Sul litorânea"),
            ("Tijuca", "bairro", "Rio de Janeiro", -22.9242, -43.2328, "exata", "Zona Norte tradicional"),
            ("Maré", "complexo", "Rio de Janeiro", -22.8580, -43.2450, "centroide", "Complexo de comunidades na Zona Norte"),
            ("São Cristóvão", "bairro", "Rio de Janeiro", -22.8988, -43.2215, "exata", "Zona Norte, área histórica"),
            ("Barra da Tijuca", "bairro", "Rio de Janeiro", -23.0003, -43.3659, "exata", "Zona Oeste do RJ"),
            ("Duque de Caxias", "municipio", "Duque de Caxias", -22.7856, -43.3117, "centroide", "Baixada Fluminense"),
            ("Niterói", "municipio", "Niterói", -22.8859, -43.1153, "centroide", "Região Metropolitana Leste"),
            ("Madureira", "bairro", "Rio de Janeiro", -22.8717, -43.3396, "exata", "Polo cultural da Zona Norte"),
            ("[DEMO] Território em Litígio Histórico", "territorio_historico", "Rio de Janeiro", None, None, "desconhecida", "Território de fronteira histórica sem coordenadas exatas mapeadas"),
        ]

        regions_data = []
        for name, r_type, mun, lat, lon, prec, desc in raw_regions:
            norm = normalize_location(name)
            regions_data.append(
                Region(
                    original_name=norm["original_name"],
                    normalized_name=norm["normalized_name"],
                    region_type=r_type,
                    municipality=mun,
                    latitude=lat,
                    longitude=lon,
                    location_precision=prec,
                    description=desc,
                    is_demo=True,
                )
            )
        db.add_all(regions_data)
        db.flush()

        # 2. Organizações [DEMO]
        raw_orgs = [
            ("[DEMO] Ordem dos Advogados Seccional RJ", "OAB-RJ", "sociedade_civil", 1930, None, "Entidade jurídica"),
            ("[DEMO] Delegacia Regional de Ordem Política e Social", "DOPS-RJ", "orgao_estatal", 1922, 1983, "Órgão de repressão e inteligência"),
            ("[DEMO] Batalhão de Polícia Militar da Zona Sul", "19-BPM", "policial", 1975, None, "Comando regional"),
            ("[DEMO] Sindicato dos Metalúrgicos do Rio", "SindMetal-RJ", "sindicato", 1917, None, "Entidade sindical"),
            ("[DEMO] Associação de Moradores Unidos da Baixada", "AMUB", "sociedade_civil", 1983, None, "Coletivo popular"),
            ("[DEMO] Coletivo Cultural e Teatral Carioca", "CCTC", "sociedade_civil", 1980, None, "Grupo artístico"),
        ]
        orgs_data = []
        for name, acr, o_type, f_yr, d_yr, desc in raw_orgs:
            norm = normalize_organization(name)
            orgs_data.append(
                Organization(
                    original_name=norm["original_name"],
                    normalized_name=norm["normalized_name"],
                    acronym=acr,
                    org_type=o_type,
                    foundation_year=f_yr,
                    dissolution_year=d_yr,
                    description=desc,
                    is_demo=True,
                )
            )
        db.add_all(orgs_data)
        db.flush()

        # 3. Pessoas [DEMO]
        raw_people = [
            ("[DEMO] Dra. Helena Vasconcelos", "Helena da OAB", "Advogada e defensora de direitos", 1938, None),
            ("[DEMO] Comissário Roberto Albuquerque", "Beto Investigador", "Agente policial", 1942, 1999),
            ("[DEMO] Mário Santos da Silva", "Mário Naval", "Líder operário do setor naval", 1935, 2005),
            ("[DEMO] Prof.ª Clarice Guimarães", "Prof. Clarice", "Pesquisadora e historiadora", 1945, None),
            ("[DEMO] Sebastião Mendes", "Tião da Associação", "Líder comunitário local", 1940, 2012),
        ]
        people_data = []
        for name, ali, role, by, dy in raw_people:
            norm = normalize_name(name)
            people_data.append(
                Person(
                    original_name=norm["original_name"],
                    normalized_name=norm["normalized_name"],
                    aliases=ali,
                    role_description=role,
                    birth_year=by,
                    death_year=dy,
                    is_demo=True,
                )
            )
        db.add_all(people_data)
        db.flush()

        # 4. Fontes [DEMO] (Separando tipologia de avaliação da evidência)
        sources_data = [
            Source(
                title="[DEMO] Relatório Anual da Comissão Arquivística de 1975",
                citation="COMISSÃO DE PESQUISA. Relatório do Fundo de Documentação Histórica (1975). Rio de Janeiro: Arquivo Público, 1976.",
                author="Comissão Arquivística",
                publisher="Arquivo Público do Estado",
                publication_year=1976,
                source_type="oficial_relatorio",
                archive_ref="Arquivo do Estado, Caixa 14, Documento 88",
                is_demo=True,
            ),
            Source(
                title="[DEMO] Diário de Notícias Carioca - Edição Matutina (Maio 1978)",
                citation="DIÁRIO DE NOTÍCIAS. Cobertura da Paralisação Geral nos Estaleiros. Rio de Janeiro, ano 48, n. 1420, p. 1-3, 14 mai. 1978.",
                author="Redação Diário de Notícias",
                publisher="Diário de Notícias",
                publication_year=1978,
                source_type="jornalismo_hemeroteca",
                archive_ref="Hemeroteca Digital, Microfilme 1978-05",
                is_demo=True,
            ),
            Source(
                title="[DEMO] Livro 'Vozes e Territórios da Guanabara'",
                citation="GUIMARÃES, Clarice. Vozes e Territórios da Guanabara: Conflitos e Memória (1970-1985). Rio de Janeiro: Editora Universitária, 1986.",
                author="Clarice Guimarães",
                publisher="Editora Universitária",
                publication_year=1986,
                source_type="academico_livro",
                archive_ref="Biblioteca Nacional, Acervo Geral, 320.981 G963v",
                is_demo=True,
            ),
            Source(
                title="[DEMO] Boletim Informativo da Ordem dos Advogados (1980)",
                citation="OAB-RJ. Boletim de Defesa das Garantias Fundamentais. Rio de Janeiro: Seccional RJ, n. 12, ago. 1980.",
                author="OAB Seccional RJ",
                publisher="OAB-RJ",
                publication_year=1980,
                source_type="oficial_relatorio",
                archive_ref="Acervo Histórico OAB, Pasta 1980-B",
                is_demo=True,
            ),
            Source(
                title="[DEMO] Inquérito Policial de Ocorrência Especial n. 34/81",
                citation="SECRETARIA DE SEGURANÇA. Inquérito Policial sobre Incidente no Pavilhão de Eventos. Rio de Janeiro: Divisão de Registros, 1981.",
                author="Secretaria de Segurança",
                publisher="Polícia Civil RJ",
                publication_year=1981,
                source_type="documento_judicial",
                archive_ref="Arquivo Público do Estado do RJ, Série Inquéritos, doc 34/81",
                is_demo=True,
            ),
            Source(
                title="[DEMO] Depoimento Oral Registrado de Sebastião Mendes",
                citation="MENDES, Sebastião. Entrevista concedida ao Projeto Memória Popular da Baixada. Gravação em fita magnética, 18 out. 1984.",
                author="Sebastião Mendes / Núcleo de História Oral",
                publisher="Núcleo de História Oral",
                publication_year=1984,
                source_type="historia_oral",
                archive_ref="Arquivo Sonoro Comunitário, Fita 07-B",
                is_demo=True,
            ),
        ]
        db.add_all(sources_data)
        db.flush()

        r = {reg.original_name: reg for reg in regions_data}
        o = {org.acronym: org for org in orgs_data}
        p = {pers.original_name: pers for pers in people_data}
        s = {src.title: src for src in sources_data}

        # 5. Eventos [DEMO] com rigor temporal e proveniência estrita
        events_setup = [
            {
                "title": "[DEMO] Assembleia Sindical e Paralisação dos Operários Navais",
                "date_display": "12 de abril de 1975",
                "date_start": "1975-04-12",
                "year": 1975,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "confirmado",
                "description": "Reunião de trabalhadores do setor naval deliberando pauta salarial e segurança nos estaleiros de Niterói.",
                "historical_context": "Período de recomposição gradual de movimentos sindicais.",
                "region": r["Niterói"],
                "orgs": [(o["SindMetal-RJ"], "organizador")],
                "people": [(p["[DEMO] Mário Santos da Silva"], "lideranca_operaria")],
                "source": s["[DEMO] Relatório Anual da Comissão Arquivística de 1975"],
                "excerpt": "Às 08h30 do dia 12 de abril de 1975, operários concentraram-se na praça do estaleiro em Niterói, votando a paralisação pacífica.",
                "page": "p. 45-47",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Abertura do Congresso Jurídico de Garantias Fundamentais",
                "date_display": "20 de agosto de 1977",
                "date_start": "1977-08-20",
                "year": 1977,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "confirmado",
                "description": "Conferência de juristas no Centro do Rio de Janeiro discutindo restauração de garantias civis.",
                "historical_context": "Articulação de setores da sociedade civil e juristas.",
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
                "date_display": "14 de maio de 1978",
                "date_start": "1978-05-14",
                "year": 1978,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "confirmado",
                "description": "Caminhada de operários e moradores partindo de São Cristóvão em direção ao centro da cidade.",
                "historical_context": "Ano marcado por greves e manifestações de rua.",
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
                "date_display": "30 de abril de 1981",
                "date_start": "1981-04-30",
                "year": 1981,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "conflitante",
                "description": "Explosão de dispositivo nas imediações do pavilhão de convenções na Barra da Tijuca durante comemoração com milhares de pessoas.",
                "historical_context": "Tensões entre setores radicais contrários à abertura política e movimentos populares.",
                "region": r["Barra da Tijuca"],
                "orgs": [(o["DOPS-RJ"], "orgao_investigador"), (o["OAB-RJ"], "comissao_independente")],
                "people": [(p["[DEMO] Dra. Helena Vasconcelos"], "observadora_juridica"), (p["[DEMO] Comissário Roberto Albuquerque"], "perito_policial")],
                "source": s["[DEMO] Inquérito Policial de Ocorrência Especial n. 34/81"],
                "excerpt": "Relatório preliminar sustenta versão de ataque externo, enquanto testemunhas e laudos independentes apontam detonação acidental em veículo oficial.",
                "page": "Folhas 12-28",
                "status": "conflitante",
            },
            {
                "title": "[DEMO] Reunião de Formação da Associação de Moradores na Baixada",
                "date_display": "15 de março de 1983",
                "date_start": "1983-03-15",
                "year": 1983,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "confirmado",
                "description": "Fundação formal da rede de comitês de bairro para reivindicar saneamento e posse de terra.",
                "historical_context": "Movimentos de bairros periféricos na Baixada Fluminense.",
                "region": r["Duque de Caxias"],
                "orgs": [(o["AMUB"], "fundadora")],
                "people": [(p["[DEMO] Sebastião Mendes"], "presidente_eleito")],
                "source": s["[DEMO] Depoimento Oral Registrado de Sebastião Mendes"],
                "excerpt": "Naquele 15 de março de 1983 juntamos delegados de doze loteamentos em Caxias para fundar a entidade e lutar pela água encanada.",
                "page": "Fita 07-B, min 14:30",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Festival Cultural de Rua em Madureira",
                "date_display": "setembro de 1984",
                "date_start": "1984-09-01",
                "year": 1984,
                "exact_date": False,
                "temporal_precision": "mes",
                "confidence_level": "provavel",
                "description": "Exibição ao ar livre de curtas-metragens e apresentações teatrais em praça pública de Madureira.",
                "historical_context": "Efervescência cultural e ocupação dos espaços públicos no período das Diretas Já.",
                "region": r["Madureira"],
                "orgs": [(o["CCTC"], "produtor_cultural")],
                "people": [(p["[DEMO] Prof.ª Clarice Guimarães"], "curadora_historica")],
                "source": s["[DEMO] Livro 'Vozes e Territórios da Guanabara'"],
                "excerpt": "A praça de Madureira transformou-se em palco comunitário acolhendo mais de duas mil pessoas para debates e filmes nacionais.",
                "page": "p. 240",
                "status": "provavel",
            },
            {
                "title": "[DEMO] Denúncia de Monitoramento Ilegal de Advogados e Entidades",
                "date_display": "agosto de 1980",
                "date_start": "1980-08-01",
                "year": 1980,
                "exact_date": False,
                "temporal_precision": "mes",
                "confidence_level": "confirmado",
                "description": "Publicação de dossiê contendo registros de vigilância policial e escutas direcionadas a defensores de direitos humanos.",
                "historical_context": "Fase de transição política.",
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
                "date_display": "18 de junho de 1985",
                "date_start": "1985-06-18",
                "year": 1985,
                "exact_date": True,
                "temporal_precision": "dia",
                "confidence_level": "confirmado",
                "description": "Encontro regional reunindo representantes de várias favelas para elaboração de pauta urbana unificada.",
                "historical_context": "Período da Nova República e reorganização das federações comunitárias.",
                "region": r["Maré"],
                "orgs": [(o["AMUB"], "convidada"), (o["CCTC"], "apoio_cultural")],
                "people": [(p["[DEMO] Sebastião Mendes"], "convidado_intersetorial"), (p["[DEMO] Prof.ª Clarice Guimarães"], "documentarista")],
                "source": s["[DEMO] Livro 'Vozes e Territórios da Guanabara'"],
                "excerpt": "Em junho de 1985, o encontro na Maré sintetizou a aliança entre movimentos da Zona Norte e da Baixada Fluminense.",
                "page": "p. 278",
                "status": "confirmado",
            },
            {
                "title": "[DEMO] Boato de Panfletagem Não Confirmada em Copacabana",
                "date_display": "final de 1979",
                "date_start": "1979-11-01",
                "year": 1979,
                "exact_date": False,
                "temporal_precision": "aproximado",
                "confidence_level": "nao_verificado",
                "description": "Informe anônimo de suposta panfletagem em calçadão litorâneo, sem confirmação em prontuários.",
                "historical_context": "Circulação de informes anônimos e contra-informações.",
                "region": r["Copacabana"],
                "orgs": [(o["19-BPM"], "averiguador")],
                "people": [(p["[DEMO] Comissário Roberto Albuquerque"], "analista_informe")],
                "source": s["[DEMO] Diário de Notícias Carioca - Edição Matutina (Maio 1978)"],
                "excerpt": "Nota curta de coluna de segurança mencionando apuração de chamada anônima sem ocorrência confirmada.",
                "page": "p. 8",
                "status": "nao_verificado",
            },
            {
                "title": "[DEMO] Registro Histórico em Território de Fronteira Não Delimitado",
                "date_display": "c. 1976",
                "date_start": "1976-01-01",
                "year": 1976,
                "exact_date": False,
                "temporal_precision": "aproximado",
                "confidence_level": "provavel",
                "description": "Ocorrência documentada em área de litígio entre distritos, cuja cartografia exata não possui coordenadas mapeadas na fonte.",
                "historical_context": "Incerteza cartográfica e delimitações imprecisas pré-computação gráfica.",
                "region": r["[DEMO] Território em Litígio Histórico"],
                "orgs": [(o["SindMetal-RJ"], "interessado")],
                "people": [(p["[DEMO] Mário Santos da Silva"], "participante")],
                "source": s["[DEMO] Relatório Anual da Comissão Arquivística de 1975"],
                "excerpt": "Disputa de jurisdição sobre área de transição cujos marcos geodésicos exatos não constavam do memorial do município.",
                "page": "p. 89",
                "status": "provavel",
            }
        ]

        for item in events_setup:
            ev = Event(
                title=item["title"],
                date_display=item["date_display"],
                date_start=item["date_start"],
                year=item["year"],
                exact_date=item["exact_date"],
                temporal_precision=item["temporal_precision"],
                confidence_level=item["confidence_level"],
                description=item["description"],
                historical_context=item["historical_context"],
                is_demo=True,
            )
            db.add(ev)
            db.flush()

            # Proveniência estrita
            ev_src = EventSource(
                event_id=ev.id,
                source_id=item["source"].id,
                page_or_section=item["page"],
                excerpt=item["excerpt"],
                claim_assertion=item["title"],
                validation_status=item["status"],
                confidence_notes=f"Registro DEMO de teste ({item['status']}).",
            )
            db.add(ev_src)

            # Região
            ev_reg = EventRegion(
                event_id=ev.id,
                region_id=item["region"].id,
                specific_location_name=item["region"].original_name,
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
        print(f"[OK] Sucesso: {len(events_setup)} eventos DEMO inseridos com rigor temporal, geográfico e proveniência!")

    except Exception as e:
        db.rollback()
        print(f"[ERRO] Falha ao popular banco: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
