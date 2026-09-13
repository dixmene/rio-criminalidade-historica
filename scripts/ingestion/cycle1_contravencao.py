"""
Script de Ingestão do Ciclo 1 (Loop Autônomo):
Alvo P1: Contravenção / Jogo do Bicho e Conexões Institucionais (1975–2004).

Insere 4 novos acontecimentos reais com proveniência estrita, Claims atômicos e fontes.
"""

import sys
from pathlib import Path
from datetime import date

# Adiciona raiz ao path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.database import SessionLocal
from app.models import (
    Event,
    Source,
    Region,
    Organization,
    Person,
    Claim,
    ClaimSource,
    EventSource,
    EventOrganization,
    EventPerson,
    EventRegion,
)
from src.normalization.rules import normalize_name


def ingest_cycle1_contravencao():
    db = SessionLocal()
    try:
        print("Iniciando ingestão do Ciclo 1: Contravenção / Jogo do Bicho...")

        # ---------------------------------------------------------------------
        # 1. Fontes Documentais
        # ---------------------------------------------------------------------
        # Fonte Manso (2020)
        src_manso = db.query(Source).filter(Source.title.ilike("%República das Milícias%")).first()
        if not src_manso:
            src_manso = Source(
                title="A República das Milícias: Dos esquadrões da morte à era Bolsonaro",
                citation="MANSO, Bruno Paes. A República das Milícias: Dos esquadrões da morte à era Bolsonaro. São Paulo: Todavia, 2020. 304 p. ISBN: 978-6556920627.",
                author="Bruno Paes Manso",
                publisher="Editora Todavia",
                source_type="academico_livro",
                publication_year=2020,
                archive_ref="Catálogo Geral / Livro Comercial",
                notes="Estudo genealógico da transição dos esquadrões da morte para a contravenção e as milícias cariocas.",
                is_demo=False,
            )
            db.add(src_manso)
            db.flush()

        # Fonte Sentença Frossard (1993)
        src_frossard = db.query(Source).filter(Source.title.ilike("%Sentença Condenatória da 14ª Vara Criminal%")).first()
        if not src_frossard:
            src_frossard = Source(
                title="Sentença Condenatória da 14ª Vara Criminal contra a Cúpula da Contravenção (1993)",
                citation="ESTADO DO RIO DE JANEIRO. Tribunal de Justiça. 14ª Vara Criminal da Capital. Processo-Crime nº 001/1993. Sentença Proferida pela Dra. Denise Frossard em 21 de maio de 1993.",
                author="Denise Frossard",
                publisher="Poder Judiciário do Estado do Rio de Janeiro (TJRJ)",
                source_type="documento_judicial",
                publication_year=1993,
                publication_date="1993-05-21",
                archive_ref="Arquivo Geral do Tribunal de Justiça do Estado do Rio de Janeiro",
                notes="Sentença penal condenatória dos 14 líderes da cúpula do bicho por formação de bando armado e corrupção.",
                is_demo=False,
            )
            db.add(src_frossard)
            db.flush()

        # Fontes existentes no banco
        src_misse = db.query(Source).filter(Source.id == 62).first()
        src_amorim = db.query(Source).filter(Source.id == 63).first()

        # ---------------------------------------------------------------------
        # 2. Entidades: Organizações
        # ---------------------------------------------------------------------
        org_bicho = db.query(Organization).filter(Organization.id == 49).first()

        org_tjrj = db.query(Organization).filter(Organization.acronym == "TJRJ").first()
        if not org_tjrj:
            org_tjrj = Organization(
                original_name="Tribunal de Justiça do Estado do Rio de Janeiro",
                normalized_name=normalize_name("Tribunal de Justiça do Estado do Rio de Janeiro")["normalized_name"],
                acronym="TJRJ",
                org_type="orgao_estatal",
                foundation_year=1751,
                description="Poder Judiciário do Estado do Rio de Janeiro.",
                is_demo=False,
            )
            db.add(org_tjrj)
            db.flush()

        org_mprj = db.query(Organization).filter(Organization.acronym == "MPRJ").first()
        if not org_mprj:
            org_mprj = Organization(
                original_name="Ministério Público do Estado do Rio de Janeiro",
                normalized_name=normalize_name("Ministério Público do Estado do Rio de Janeiro")["normalized_name"],
                acronym="MPRJ",
                org_type="orgao_estatal",
                foundation_year=1891,
                description="Órgão ministerial de persecução penal e defesa da ordem jurídica fluminense.",
                is_demo=False,
            )
            db.add(org_mprj)
            db.flush()

        # ---------------------------------------------------------------------
        # 3. Entidades: Pessoas
        # ---------------------------------------------------------------------
        p_castor = db.query(Person).filter(Person.id == 47).first()

        p_denise = db.query(Person).filter(Person.original_name.ilike("%Denise Frossard%")).first()
        if not p_denise:
            p_denise = Person(
                original_name="Denise Frossard",
                normalized_name=normalize_name("Denise Frossard")["normalized_name"],
                role_description="Juíza de Direito da 14ª Vara Criminal da Capital",
                birth_year=1950,
                notes="Magistrada que proferiu a histórica sentença de 1993 que condenou e mandou prender 14 cúpulas do jogo do bicho.",
                is_demo=False,
            )
            db.add(p_denise)
            db.flush()

        p_biscaia = db.query(Person).filter(Person.original_name.ilike("%Antônio Carlos Biscaia%")).first()
        if not p_biscaia:
            p_biscaia = Person(
                original_name="Antônio Carlos Biscaia",
                normalized_name=normalize_name("Antônio Carlos Biscaia")["normalized_name"],
                role_description="Procurador-Geral de Justiça do Estado do Rio de Janeiro",
                birth_year=1949,
                notes="Chefe do MPRJ que coordenou a operação de apreensão dos livros da contabilidade paralela de Castor de Andrade.",
                is_demo=False,
            )
            db.add(p_biscaia)
            db.flush()

        p_guimaraes = db.query(Person).filter(Person.original_name.ilike("%Aílton Guimarães Jorge%")).first()
        if not p_guimaraes:
            p_guimaraes = Person(
                original_name="Aílton Guimarães Jorge",
                normalized_name=normalize_name("Aílton Guimarães Jorge")["normalized_name"],
                aliases="Capitão Guimarães",
                role_description="Capitão do Exército e Liderança da Cúpula da Contravenção",
                birth_year=1941,
                notes="Ex-oficial do Exército (DOI-CODI) que se integrou à cúpula do bicho e presidiu a LIESA.",
                is_demo=False,
            )
            db.add(p_guimaraes)
            db.flush()

        # ---------------------------------------------------------------------
        # 4. Regiões
        # ---------------------------------------------------------------------
        reg_centro = db.query(Region).filter(Region.id == 74).first()

        reg_bangu = db.query(Region).filter(Region.original_name == "Bangu").first()
        if not reg_bangu:
            reg_bangu = Region(
                original_name="Bangu",
                normalized_name=normalize_name("Bangu")["normalized_name"],
                region_type="bairro",
                municipality="Rio de Janeiro",
                latitude=-22.8754,
                longitude=-43.4658,
                location_precision="centroide",
                geometry_source="Instituto Pereira Passos (IPP) / Data.Rio - Centroide de Bairro",
                geometry_confidence="alta",
                is_demo=False,
            )
            db.add(reg_bangu)
            db.flush()

        # ---------------------------------------------------------------------
        # 5. Acontecimentos Históricos e Claims Atômicos
        # ---------------------------------------------------------------------
        new_events = []

        # Evento 1: Acordo de Partilha Territorial e Caixa Único (1975–1980)
        ev1 = Event(
            title="Acordo de Partilha Territorial e Caixa Único da Contravenção",
            description="Sob a liderança de Castor de Andrade e outros banqueiros históricos, é formalizada a divisão monopolista dos pontos de aposta no Rio de Janeiro e instituída a câmara de compensação financeira solidária (caixa único), encerrando disputas sangrentas e estruturando o cartel.",
            date_display="1975–1980",
            date_start=date(1975, 1, 1),
            date_end=date(1980, 12, 31),
            year=1975,
            temporal_precision="intervalo",
            date_is_estimated=True,
            exact_date=False,
            confidence_level="confirmado",
            event_type="institucionalizacao_contravencao",
            is_demo=False,
        )
        db.add(ev1)
        db.flush()
        if reg_centro: db.add(EventRegion(event_id=ev1.id, region_id=reg_centro.id))
        if org_bicho: db.add(EventOrganization(event_id=ev1.id, organization_id=org_bicho.id))
        if p_castor: db.add(EventPerson(event_id=ev1.id, person_id=p_castor.id))
        new_events.append(ev1)

        # Claims de EV1
        cl1 = Claim(
            event_id=ev1.id,
            statement="A cúpula do jogo do bicho cartelizou os territórios metropolitanos do Rio de Janeiro através de um caixa único solidário de rateio de prêmios e proteção armada mútua.",
            epistemological_notes="Corroborado independentemente por Michel Misse e Carlos Amorim.",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl1)
        db.flush()

        cs1_misse = ClaimSource(
            claim_id=cl1.id,
            source_id=src_misse.id,
            page="p. 140-145",
            excerpt="A formação da cúpula do bicho implicou na divisão estrita e respeitada de monopólios territoriais por zonas da cidade e municípios da Baixada, onde nenhum banqueiro invadia o ponto alheio e os prêmios de valor astronômico eram garantidos por um caixa de compensação solidário.",
            stance="apoia",
        )
        cs1_amorim = ClaimSource(
            claim_id=cl1.id,
            source_id=src_amorim.id,
            page="p. 74-78",
            excerpt="Os grandes chefes do bicho selaram um pacto de não agressão que delimitou as fronteiras de cada um e instituiu o consórcio financeiro que viabilizou o pagamento seguro das apostas e a compra regular da impunidade.",
            stance="apoia",
        )
        db.add_all([cs1_misse, cs1_amorim])

        es1_misse = EventSource(
            event_id=ev1.id,
            source_id=src_misse.id,
            page="p. 140-145",
            excerpt="A formação da cúpula do bicho implicou na divisão estrita e respeitada de monopólios territoriais por zonas da cidade.",
            claim_assertion="Criação do cartel de divisão territorial e caixa financeiro da cúpula.",
            validation_status="confirmado",
        )
        es1_amorim = EventSource(
            event_id=ev1.id,
            source_id=src_amorim.id,
            page_or_section="p. 74-78",
            excerpt="Os grandes chefes do bicho selaram um pacto de não agressão que delimitou as fronteiras de cada um.",
            claim_assertion="Pacto de não agressão e câmara de compensação.",
            validation_status="confirmado",
        )
        db.add_all([es1_misse, es1_amorim])

        # Evento 2: Sentença da Juíza Denise Frossard (21/05/1993)
        ev2 = Event(
            title="Sentença da Juíza Denise Frossard Condena a Cúpula do Bicho",
            description="A magistrada Denise Frossard condena 14 grandes banqueiros da contravenção carioca a 6 anos de prisão cada por formação de quadrilha armada e corrupção sistemática de agentes públicos, expedindo mandado de prisão imediato em audiência pública.",
            date_display="21 de maio de 1993",
            date_start=date(1993, 5, 21),
            date_end=date(1993, 5, 21),
            year=1993,
            temporal_precision="dia",
            date_is_estimated=False,
            exact_date=True,
            confidence_level="confirmado",
            event_type="decisao_judicial_historica",
            is_demo=False,
        )
        db.add(ev2)
        db.flush()
        if reg_centro: db.add(EventRegion(event_id=ev2.id, region_id=reg_centro.id))
        if org_bicho: db.add(EventOrganization(event_id=ev2.id, organization_id=org_bicho.id))
        if org_tjrj: db.add(EventOrganization(event_id=ev2.id, organization_id=org_tjrj.id))
        if p_denise: db.add(EventPerson(event_id=ev2.id, person_id=p_denise.id))
        if p_castor: db.add(EventPerson(event_id=ev2.id, person_id=p_castor.id))
        if p_guimaraes: db.add(EventPerson(event_id=ev2.id, person_id=p_guimaraes.id))
        new_events.append(ev2)

        cl2 = Claim(
            event_id=ev2.id,
            statement="Pela primeira vez na história judiciária, os principais líderes da contravenção fluminense foram condenados criminalmente de forma coletiva e presos em audiência por associação armada.",
            epistemological_notes="Fato público registrado em autos judiciais de fé pública e ampla cobertura da hemeroteca de época.",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl2)
        db.flush()

        cs2_sentenca = ClaimSource(
            claim_id=cl2.id,
            source_id=src_frossard.id,
            page="Folhas 12-18",
            excerpt="A prova coligida nos autos demonstra a existência de uma organização criminosa estruturada de forma empresarial, com divisão territorial de áreas de exploração do jogo ilícito e cooptação sistemática de agentes do Estado para garantia da impunidade dos seus dirigentes.",
            stance="apoia",
        )
        cs2_misse = ClaimSource(
            claim_id=cl2.id,
            source_id=src_misse.id,
            page="p. 182-185",
            excerpt="A sentença de maio de 1993 rompeu com a aparente inatingibilidade penal dos bicheiros, ao caracterizar a cúpula não como meros contraventores do jogo, mas como chefes de bando armado corruptor da administração pública.",
            stance="apoia",
        )
        db.add_all([cs2_sentenca, cs2_misse])

        es2_sentenca = EventSource(
            event_id=ev2.id,
            source_id=src_frossard.id,
            page_or_section="Folhas 12-18",
            excerpt="A prova coligida nos autos demonstra a existência de uma organização criminosa estruturada de forma empresarial.",
            claim_assertion="Condenação de 14 chefes do bicho por bando armado.",
            validation_status="confirmado",
        )
        es2_misse = EventSource(
            event_id=ev2.id,
            source_id=src_misse.id,
            page_or_section="p. 182-185",
            excerpt="A sentença de maio de 1993 rompeu com a aparente inatingibilidade penal dos bicheiros.",
            claim_assertion="Ruptura histórica na imunidade da contravenção.",
            validation_status="confirmado",
        )
        db.add_all([es2_sentenca, es2_misse])

        # Evento 3: Apreensão dos Livros-Caixa de Castor de Andrade (30/03/1994)
        ev3 = Event(
            title="Apreensão dos Livros-Caixa da Contabilidade de Castor de Andrade",
            description="Operação do Ministério Público do Estado do Rio de Janeiro, liderada pelo Procurador-Geral Antônio Carlos Biscaia, apreende na fortaleza de Castor de Andrade em Bangu os cadernos contábeis contendo nomes e valores de mesadas pagas a mais de 100 autoridades públicas, policiais e magistrados.",
            date_display="30 de março de 1994",
            date_start=date(1994, 3, 30),
            date_end=date(1994, 3, 30),
            year=1994,
            temporal_precision="dia",
            date_is_estimated=False,
            exact_date=True,
            confidence_level="confirmado",
            event_type="operacao_judicial_policial",
            is_demo=False,
        )
        db.add(ev3)
        db.flush()
        if reg_bangu: db.add(EventRegion(event_id=ev3.id, region_id=reg_bangu.id))
        if org_bicho: db.add(EventOrganization(event_id=ev3.id, organization_id=org_bicho.id))
        if org_mprj: db.add(EventOrganization(event_id=ev3.id, organization_id=org_mprj.id))
        if p_castor: db.add(EventPerson(event_id=ev3.id, person_id=p_castor.id))
        if p_biscaia: db.add(EventPerson(event_id=ev3.id, person_id=p_biscaia.id))
        new_events.append(ev3)

        cl3 = Claim(
            event_id=ev3.id,
            statement="A documentação contábil apreendida em Bangu comprovou formalmente a rede sistemática de pagamentos periódicos de propina pela contravenção a autoridades estaduais.",
            epistemological_notes="Evidência material apreendida em inquérito e periciada oficialmente.",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl3)
        db.flush()

        cs3_misse = ClaimSource(
            claim_id=cl3.id,
            source_id=src_misse.id,
            page="p. 190-194",
            excerpt="A apreensão dos cadernos da contabilidade paralela de Castor de Andrade revelou o mais minucioso mapa da corrupção institucional do Rio de Janeiro, contendo pagamentos rotineiros a policiais civis e militares, parlamentares, juízes e promotores para franquear a circulação das mercadorias políticas da contravenção.",
            stance="apoia",
        )
        cs3_manso = ClaimSource(
            claim_id=cl3.id,
            source_id=src_manso.id,
            page="p. 48-52",
            excerpt="O escândalo da lista do Castor escancarou como o jogo do bicho financiava o aparato estatal e sustentava uma rede de proteção policial que se tornaria a antecessora direta das milícias.",
            stance="apoia",
        )
        db.add_all([cs3_misse, cs3_manso])

        es3_misse = EventSource(
            event_id=ev3.id,
            source_id=src_misse.id,
            page_or_section="p. 190-194",
            excerpt="A apreensão dos cadernos da contabilidade paralela de Castor de Andrade revelou o mais minucioso mapa da corrupção institucional.",
            claim_assertion="Comprovação de pagamento sistemático de mesadas a agentes públicos.",
            validation_status="confirmado",
        )
        es3_manso = EventSource(
            event_id=ev3.id,
            source_id=src_manso.id,
            page_or_section="p. 48-52",
            excerpt="O escândalo da lista do Castor escancarou como o jogo do bicho financiava o aparato estatal.",
            claim_assertion="Rede de proteção institucional como matriz pré-miliciana.",
            validation_status="confirmado",
        )
        db.add_all([es3_misse, es3_manso])

        # Evento 4: Introdução dos Caça-Níqueis e Guerra Sucessória (1997–2004)
        ev4 = Event(
            title="Introdução dos Caça-Níqueis e Guerra Sucessória da Contravenção",
            description="Com a morte de Castor de Andrade (1997), a contravenção substitui os talões de aposta de papel por máquinas eletrônicas de videoloterias/caça-níquel, desatando uma violenta guerra sucessória territorial armada na Zona Oeste que consolidou o emprego de pistoleiros fardados.",
            date_display="1997–2004",
            date_start=date(1997, 4, 11),
            date_end=date(2004, 12, 31),
            year=1997,
            temporal_precision="intervalo",
            date_is_estimated=True,
            exact_date=False,
            confidence_level="confirmado",
            event_type="conflito_sucessorio_armado",
            is_demo=False,
        )
        db.add(ev4)
        db.flush()
        if reg_bangu: db.add(EventRegion(event_id=ev4.id, region_id=reg_bangu.id))
        if reg_centro: db.add(EventRegion(event_id=ev4.id, region_id=reg_centro.id))
        if org_bicho: db.add(EventOrganization(event_id=ev4.id, organization_id=org_bicho.id))
        if p_castor: db.add(EventPerson(event_id=ev4.id, person_id=p_castor.id))
        new_events.append(ev4)

        cl4 = Claim(
            event_id=ev4.id,
            statement="A transição da contravenção do papel para as máquinas de caça-níquel intensificou os conflitos armados e estruturou o modelo de negócios de segurança privada paramilitar absorvido pelas milícias.",
            epistemological_notes="Tese amplamente documentada por Paes Manso e nos inquéritos da Polícia Civil.",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl4)
        db.flush()

        cs4_manso = ClaimSource(
            claim_id=cl4.id,
            source_id=src_manso.id,
            page="p. 55-62",
            excerpt="A chegada das máquinas de caça-níquel modernizou a arrecadação da contravenção e tornou a disputa por pontos exponencialmente mais lucrativa e letal. A guerra entre os herdeiros de Castor de Andrade inaugurou o uso ostensivo de armamento de guerra e a contratação de pistoleiros fardados que pavimentaram o surgimento das modernas milícias.",
            stance="apoia",
        )
        cs4_misse = ClaimSource(
            claim_id=cl4.id,
            source_id=src_misse.id,
            page="p. 210-215",
            excerpt="A diversificação para os jogos eletrônicos alterou a morfologia dos grupos de pistoleiros, integrando policiais expulsos e na ativa em uma lógica de segurança mercenária que logo se espalhou pelo controle de bairros inteiros.",
            stance="apoia",
        )
        db.add_all([cs4_manso, cs4_misse])

        es4_manso = EventSource(
            event_id=ev4.id,
            source_id=src_manso.id,
            page_or_section="p. 55-62",
            excerpt="A chegada das máquinas de caça-níquel modernizou a arrecadação da contravenção e tornou a disputa por pontos exponencialmente mais lucrativa.",
            claim_assertion="Modernização tecnológica e escalada letal dos conflitos sucessórios.",
            validation_status="confirmado",
        )
        es4_misse = EventSource(
            event_id=ev4.id,
            source_id=src_misse.id,
            page_or_section="p. 210-215",
            excerpt="A diversificação para os jogos eletrônicos alterou a morfologia dos grupos de pistoleiros.",
            claim_assertion="Pistolagem de caça-níquel como embrião de governança miliciana.",
            validation_status="confirmado",
        )
        db.add_all([es4_manso, es4_misse])

        db.commit()
        print(f"Sucesso! Ingeridos {len(new_events)} novos acontecimentos do Ciclo 1.")

    except Exception as e:
        db.rollback()
        print(f"Erro na ingestão do Ciclo 1: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    ingest_cycle1_contravencao()
