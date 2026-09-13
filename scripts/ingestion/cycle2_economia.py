"""
Script de Ingestão do Ciclo 2 (Loop Autônomo):
Alvo P1: Economia & Desindustrialização Metropolitana (1975–1990).

Insere 3 novos acontecimentos reais de alta relevância histórico-estrutural:
1. Fusão dos Estados da Guanabara e do Rio de Janeiro (15/03/1975);
2. Desindustrialização e Proliferação de Vazios Urbanos na AP3 (1980–1986);
3. Crise Fiscal das Finanças Estaduais e Sucateamento da Segurança Pública (1987–1989).
"""

import sys
from pathlib import Path
from datetime import date

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.database import SessionLocal
from app.models import (
    Event,
    Source,
    Region,
    Organization,
    Claim,
    ClaimSource,
    EventSource,
    EventOrganization,
    EventRegion,
)
from src.normalization.rules import normalize_name


def ingest_cycle2_economia():
    db = SessionLocal()
    try:
        print("Iniciando ingestão do Ciclo 2: Economia e Desindustrialização...")

        # ---------------------------------------------------------------------
        # 1. Fontes Primárias & Bibliográficas
        # ---------------------------------------------------------------------
        # Fonte LC 20/1974 (Fusão)
        src_lc20 = db.query(Source).filter(Source.title.ilike("%Lei Complementar Federal nº 20%")).first()
        if not src_lc20:
            src_lc20 = Source(
                title="Lei Complementar Federal nº 20 de 1º de julho de 1974 (Fusão dos Estados da Guanabara e do Rio de Janeiro)",
                citation="BRASIL. Presidência da República. Lei Complementar nº 20, de 1º de julho de 1974. Dispõe sobre a criação de Estados e Territórios e dá outras providências (Fusão Guanabara-Rio de Janeiro). Brasília, DF: Diário Oficial da União, 2 jul. 1974.",
                author="Presidência da República",
                publisher="Imprensa Nacional / Diário Oficial da União",
                source_type="oficial_relatorio",
                publication_year=1974,
                publication_date="1974-07-02",
                archive_ref="Arquivo Nacional / Diário Oficial da União - Edição Histórica",
                notes="Lei que determinou a fusão compulsória dos estados da Guanabara e do Rio de Janeiro a partir de 15 de março de 1975.",
                is_demo=False,
            )
            db.add(src_lc20)
            db.flush()

        # Fontes existentes no banco
        src_sobral = db.query(Source).filter(Source.id == 73).first()
        src_misse = db.query(Source).filter(Source.id == 62).first()
        src_zaluar = db.query(Source).filter(Source.id == 64).first()

        # ---------------------------------------------------------------------
        # 2. Entidades: Organizações
        # ---------------------------------------------------------------------
        org_govrj = db.query(Organization).filter(Organization.acronym == "GOVRJ").first()
        if not org_govrj:
            org_govrj = Organization(
                original_name="Governo do Estado do Rio de Janeiro",
                normalized_name=normalize_name("Governo do Estado do Rio de Janeiro")["normalized_name"],
                acronym="GOVRJ",
                org_type="orgao_estatal",
                foundation_year=1975,
                description="Poder Executivo do Estado unificado do Rio de Janeiro instituído pela Lei Complementar 20/1974.",
                is_demo=False,
            )
            db.add(org_govrj)
            db.flush()

        org_alerj = db.query(Organization).filter(Organization.id == 57).first()
        org_pmerj = db.query(Organization).filter(Organization.id == 53).first()
        org_pcerj = db.query(Organization).filter(Organization.id == 55).first()

        # ---------------------------------------------------------------------
        # 3. Entidades: Regiões
        # ---------------------------------------------------------------------
        reg_centro = db.query(Region).filter(Region.id == 74).first()
        reg_ap3 = db.query(Region).filter(Region.id == 89).first()

        new_events = []

        # ---------------------------------------------------------------------
        # Evento 1: Fusão dos Estados da Guanabara e do Rio de Janeiro (15/03/1975)
        # ---------------------------------------------------------------------
        ev1 = Event(
            title="Instalação do Novo Estado do Rio de Janeiro Pós-Fusão",
            description="Entra formalmente em vigor a unificação compulsória entre o Estado da Guanabara (antigo Distrito Federal) e o antigo Estado do Rio de Janeiro, unificando duas máquinas administrativas e policiais distintas em meio a um choque orçamentário que fragilizou os serviços urbanos metropolitanos.",
            date_display="15 de março de 1975",
            date_start=date(1975, 3, 15),
            date_end=date(1975, 3, 15),
            year=1975,
            temporal_precision="dia",
            date_is_estimated=False,
            exact_date=True,
            confidence_level="confirmado",
            event_type="reforma_institucional_politica",
            is_demo=False,
        )
        db.add(ev1)
        if reg_centro: db.add(EventRegion(event_id=ev1.id, region_id=reg_centro.id))
        if org_govrj: db.add(EventOrganization(event_id=ev1.id, organization_id=org_govrj.id))
        if org_alerj: db.add(EventOrganization(event_id=ev1.id, organization_id=org_alerj.id))
        if org_pmerj: db.add(EventOrganization(event_id=ev1.id, organization_id=org_pmerj.id))
        new_events.append(ev1)

        cl1 = Claim(
            event_id=ev1.id,
            statement="A fusão compulsória de 1975 extinguiu a estabilidade fiscal da Guanabara e unificou de forma conflituosa polícias com quadros, remunerações e doutrinas discrepantes, gerando uma persistente crise orçamentária e institucional no território metropolitano.",
            epistemological_notes="Comprovado pelo texto legal da LC 20/74 e pela literatura de economia política fluminense (Sobral 2020).",
            confidence_level="confirmado",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl1)
        db.flush()

        cs1_lc20 = ClaimSource(
            claim_id=cl1.id,
            source_id=src_lc20.id,
            page="Artigo 1º ao Artigo 10",
            excerpt="A 15 de março de 1975, os atuais Estados da Guanabara e do Rio de Janeiro passarão a constituir um único Estado, sob a denominação de Estado do Rio de Janeiro, com a Capital na Cidade do Rio de Janeiro.",
            stance="apoia",
            confidence_level="confirmado",
        )
        cs1_sobral = ClaimSource(
            claim_id=cl1.id,
            source_id=src_sobral.id,
            page="p. 18-22",
            excerpt="A fusão de 1975 desarticulou o arranjo orçamentário que sustentava o funcionalismo e os investimentos na antiga capital federal, herdando a defasagem fiscal e de infraestrutura do antigo estado fluminense sem contrapartida perene da União.",
            stance="apoia",
            confidence_level="confirmado",
        )
        db.add_all([cs1_lc20, cs1_sobral])

        es1_lc20 = EventSource(
            event_id=ev1.id,
            source_id=src_lc20.id,
            page="Artigo 1º ao Artigo 10",
            excerpt="A 15 de março de 1975, os atuais Estados da Guanabara e do Rio de Janeiro passarão a constituir um único Estado.",
            claim="Unificação compulsória e instalação do Estado unificado.",
            validation_status="confirmado",
        )
        es1_sobral = EventSource(
            event_id=ev1.id,
            source_id=src_sobral.id,
            page="p. 18-22",
            excerpt="A fusão de 1975 desarticulou o arranjo orçamentário que sustentava o funcionalismo e os investimentos na antiga capital federal.",
            claim="Desarticulação fiscal e crise institucional decorrente da unificação.",
            validation_status="confirmado",
        )
        db.add_all([es1_lc20, es1_sobral])

        # ---------------------------------------------------------------------
        # Evento 2: Desindustrialização e Vazios Urbanos na AP3 (1980–1986)
        # ---------------------------------------------------------------------
        ev2 = Event(
            title="Desindustrialização do Corredor Ferroviário e Proliferação de Vazios Urbanos na AP3",
            description="Fechamento e deslocalização de dezenas de indústrias têxteis, químicas e metalúrgicas instaladas ao longo dos ramais da Central e Leopoldina (Del Castilho, Ramos, Bonsucesso e Inhaúma), gerando desemprego em massa para populações faveladas periféricas e convertendo áreas fabris abandonadas em vetores de moradia precária e informalidade.",
            date_display="1980–1986",
            date_start=date(1980, 1, 1),
            date_end=date(1986, 12, 31),
            year=1980,
            temporal_precision="intervalo",
            date_is_estimated=True,
            exact_date=False,
            confidence_level="provavel",
            event_type="transformacao_socioeconomica",
            is_demo=False,
        )
        db.add(ev2)
        if reg_ap3: db.add(EventRegion(event_id=ev2.id, region_id=reg_ap3.id))
        new_events.append(ev2)

        cl2 = Claim(
            event_id=ev2.id,
            statement="A retração do parque industrial no subúrbio ferroviário destruiu o mercado formal de trabalho da classe trabalhadora local, forçando o confinamento de jovens da periferia na economia informal e criando as condições estruturais de recrutamento pelo varejo de drogas ilícitas.",
            epistemological_notes="Sustentado empiricamente pelas pesquisas etnográficas de Alba Zaluar e diagnósticos econômicos regionais de Bruno Sobral.",
            confidence_level="provavel",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl2)
        db.flush()

        cs2_sobral = ClaimSource(
            claim_id=cl2.id,
            source_id=src_sobral.id,
            page="p. 34-39",
            excerpt="O esvaziamento fabril do eixo da Linha Auxiliar e da Zona Norte metropolitana gerou uma estrutura produtiva oca, multiplicando grandes galpões abandonados e desestruturando as fontes de rendimento do operariado tradicional fluminense.",
            stance="apoia",
            confidence_level="provavel",
        )
        cs2_zaluar = ClaimSource(
            claim_id=cl2.id,
            source_id=src_zaluar.id,
            page="p. 62-68",
            excerpt="Com a escassez de empregos industriais registrados e o arrocho salarial que atingiu o subúrbio, a juventude pobre encontrou no comércio das drogas uma fonte imediata de ganho econômico, prestígio e afirmação de masculinidade perante a falta de horizontes.",
            stance="apoia",
            confidence_level="provavel",
        )
        db.add_all([cs2_sobral, cs2_zaluar])

        es2_sobral = EventSource(
            event_id=ev2.id,
            source_id=src_sobral.id,
            page="p. 34-39",
            excerpt="O esvaziamento fabril do eixo da Linha Auxiliar e da Zona Norte metropolitana gerou uma estrutura produtiva oca.",
            claim="Esvaziamento do parque produtivo do subúrbio e vazios urbanos.",
            validation_status="provavel",
        )
        es2_zaluar = EventSource(
            event_id=ev2.id,
            source_id=src_zaluar.id,
            page="p. 62-68",
            excerpt="Com a escassez de empregos industriais registrados e o arrocho salarial que atingiu o subúrbio, a juventude pobre encontrou no comércio das drogas uma fonte imediata de ganho.",
            claim="Impacto do desemprego industrial sobre a inserção de jovens em redes ilícitas.",
            validation_status="provavel",
        )
        db.add_all([es2_sobral, es2_zaluar])

        # ---------------------------------------------------------------------
        # Evento 3: Crise Fiscal Estadual e Sucateamento Policial (1987–1989)
        # ---------------------------------------------------------------------
        ev3 = Event(
            title="Crise Fiscal do Estado e Sucateamento da Infraestrutura de Segurança Pública",
            description="O colapso da arrecadação e o endividamento do Estado do Rio culminam em atrasos recorrentes no pagamento dos servidores policiais, sucateamento de frotas e instalações de delegacias e batalhões, aprofundando o incentivo à mercantilização da função policial e cobrança de 'arrego'.",
            date_display="1987–1989",
            date_start=date(1987, 1, 1),
            date_end=date(1989, 12, 31),
            year=1987,
            temporal_precision="intervalo",
            date_is_estimated=True,
            exact_date=False,
            confidence_level="provavel",
            event_type="crise_fiscal_institucional",
            is_demo=False,
        )
        db.add(ev3)
        if reg_centro: db.add(EventRegion(event_id=ev3.id, region_id=reg_centro.id))
        if reg_ap3: db.add(EventRegion(event_id=ev3.id, region_id=reg_ap3.id))
        if org_govrj: db.add(EventOrganization(event_id=ev3.id, organization_id=org_govrj.id))
        if org_pmerj: db.add(EventOrganization(event_id=ev3.id, organization_id=org_pmerj.id))
        if org_pcerj: db.add(EventOrganization(event_id=ev3.id, organization_id=org_pcerj.id))
        new_events.append(ev3)

        cl3 = Claim(
            event_id=ev3.id,
            statement="A asfixia financeira do Estado do Rio no final dos anos 1980 degradou os vencimentos policiais a níveis históricos, funcionando como elemento impulsionador da privatização espúria da segurança e consolidação do 'arrego' com pontos de drogas e contravenção.",
            epistemological_notes="Tese central de Michel Misse sobre a acumulação social da violência e a conversão de bens estatais em mercadoria política.",
            confidence_level="provavel",
            is_disputed=False,
            is_demo=False,
        )
        db.add(cl3)
        db.flush()

        cs3_misse = ClaimSource(
            claim_id=cl3.id,
            source_id=src_misse.id,
            page="p. 158-164",
            excerpt="O aviltamento salarial e a precariedade material dos órgãos policiais na década de 1980 aceleraram a normalização das 'mercadorias políticas', em que o poder de polícia estatal deixou de atuar exclusivamente pela via legal para operar como instrumento regular de extração de renda ilícita.",
            stance="apoia",
            confidence_level="provavel",
        )
        cs3_sobral = ClaimSource(
            claim_id=cl3.id,
            source_id=src_sobral.id,
            page="p. 45-48",
            excerpt="A crise das finanças fluminenses durante a segunda metade dos anos 1980 asfixiou a prestação de serviços básicos e congelou investimentos nos órgãos de segurança, acelerando a perda de controle sobre as corporações armadas.",
            stance="apoia",
            confidence_level="provavel",
        )
        db.add_all([cs3_misse, cs3_sobral])

        es3_misse = EventSource(
            event_id=ev3.id,
            source_id=src_misse.id,
            page="p. 158-164",
            excerpt="O aviltamento salarial e a precariedade material dos órgãos policiais na década de 1980 aceleraram a normalização das 'mercadorias políticas'.",
            claim="Asfixia salarial como indutora da mercantilização e cobrança de 'arrego'.",
            validation_status="provavel",
        )
        es3_sobral = EventSource(
            event_id=ev3.id,
            source_id=src_sobral.id,
            page="p. 45-48",
            excerpt="A crise das finanças fluminenses durante a segunda metade dos anos 1980 asfixiou a prestação de serviços básicos e congelou investimentos nos órgãos de segurança.",
            claim="Perda de capacidade de investimento do Estado na infraestrutura de segurança.",
            validation_status="provavel",
        )
        db.add_all([es3_misse, es3_sobral])

        db.commit()
        print(f"Sucesso! Ingeridos {len(new_events)} novos acontecimentos do Ciclo 2.")

    except Exception as e:
        db.rollback()
        print(f"Erro na ingestão do Ciclo 2: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    ingest_cycle2_economia()
