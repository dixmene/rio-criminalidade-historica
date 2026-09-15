"""
Testes de Linhagem Documental e Derivação entre Fontes (SourceDerivation).

Verifica a modelagem do grafo de proveniência para impedir que fontes que
reproduzem ou derivam de uma mesma raiz documental sejam falsamente
contabilizadas como evidências independentes de confirmação histórica.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models.source import Source
from app.models.associations import SourceDerivation


@pytest.fixture
def db_session():
    """Cria uma sessão de banco em memória SQLite para isolamento dos testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_source_derivation_genealogy_graph(db_session):
    """
    Cenário:
    Um livro de pesquisa investigativa (ex: Carlos Amorim, 1993) serve de fonte
    primária/secundária para um vídeo do YouTube do canal Iconografia da História.
    O vídeo deriva abertamente do livro (derivation_type='reproduz', is_independent=False).
    """
    # 1. Cria fonte raiz (Livro)
    src_livro = Source(
        title="Comando Vermelho: A história do crime organizado",
        citation="AMORIM, Carlos. Comando Vermelho: A história secreta do crime organizado. Rio de Janeiro: Record, 1993.",
        author="Carlos Amorim",
        publisher="Editora Record",
        source_type="academico_livro",
        publication_year=1993,
        is_demo=True
    )
    db_session.add(src_livro)
    db_session.flush()

    # 2. Cria fonte derivada (Vídeo do YouTube)
    src_video = Source(
        title="A Traição de Uê e a Vingança mais Famosa da História do Rio de Janeiro",
        citation="ICONOGRAFIA DA HISTÓRIA. A Traição de Uê e a Vingança mais Famosa. YouTube, 2023.",
        author="Iconografia da História",
        source_type="audiovisual_youtube",
        publication_year=2023,
        url="https://www.youtube.com/watch?v=z-6FAKUvUUc",
        is_demo=True
    )
    db_session.add(src_video)
    db_session.flush()

    # 3. Cria vínculo de derivação documental
    deriv = SourceDerivation(
        parent_source_id=src_livro.id,
        derived_source_id=src_video.id,
        derivation_type="reproduz",
        is_independent=False,
        notes="O roteiro do vídeo reproduz a reconstituição factual detalhada por Carlos Amorim (1993)."
    )
    db_session.add(deriv)
    db_session.commit()

    # 4. Asserções de navegação do grafo relacional
    assert len(src_livro.derived_sources) == 1
    assert src_livro.derived_sources[0].derived_source_id == src_video.id
    assert src_livro.derived_sources[0].is_independent is False
    assert src_livro.derived_sources[0].derivation_type == "reproduz"

    assert len(src_video.source_derivations) == 1
    assert src_video.source_derivations[0].parent_source_id == src_livro.id
    assert src_video.source_derivations[0].parent_source.author == "Carlos Amorim"


def test_source_derivation_unique_constraint(db_session):
    """Garante que o mesmo par (parent, derived) não possa ser duplicado."""
    src1 = Source(title="Relatório Policial DESIPE 1979", citation="DESIPE, 1979", source_type="oficial_relatorio", is_demo=True)
    src2 = Source(title="Jornal do Brasil - Edição de 18/09/1979", citation="JB, 1979", source_type="jornalismo_hemeroteca", is_demo=True)
    db_session.add_all([src1, src2])
    db_session.flush()

    d1 = SourceDerivation(parent_source_id=src1.id, derived_source_id=src2.id, derivation_type="cita", is_independent=False)
    db_session.add(d1)
    db_session.commit()

    d2 = SourceDerivation(parent_source_id=src1.id, derived_source_id=src2.id, derivation_type="reproduz", is_independent=False)
    db_session.add(d2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_derivation_types_coverage(db_session):
    """Testa a diversidade de tipologias de derivação admitidas pelo protocolo."""
    valid_types = ["reproduz", "resume", "cita", "deriva_dado", "adapta", "compila", "desconhecida"]
    src_parent = Source(title="Inquérito Policial Central", citation="PCERJ, 1994", source_type="documento_judicial", is_demo=True)
    db_session.add(src_parent)
    db_session.flush()

    for idx, dt in enumerate(valid_types):
        src_child = Source(title=f"Veículo Informativo {idx}", citation=f"Ref {idx}", source_type="jornalismo_investigativo", is_demo=True)
        db_session.add(src_child)
        db_session.flush()

        deriv = SourceDerivation(
            parent_source_id=src_parent.id,
            derived_source_id=src_child.id,
            derivation_type=dt,
            is_independent=(dt == "cita")
        )
        db_session.add(deriv)

    db_session.commit()
    assert len(src_parent.derived_sources) == len(valid_types)


def test_chain_derivation_finds_root_source(db_session):
    """
    Cenário em cadeia:
    Inquérito Policial (A) -> Livro Historiográfico (B) -> Vídeo YouTube (C)
    C deriva de B, B deriva de A.
    Ao chamar C.get_root_source(), o retorno DEVE ser A.
    """
    src_a = Source(title="Inquérito Policial 1979", citation="PCERJ, 1979", source_type="documento_judicial", is_demo=True)
    src_b = Source(title="Livro História das Prisões", citation="Autor X, 1990", source_type="academico_livro", is_demo=True)
    src_c = Source(title="Vídeo YouTube Ilha Grande", citation="Canal Y, 2023", source_type="audiovisual_youtube", is_demo=True)
    db_session.add_all([src_a, src_b, src_c])
    db_session.flush()

    # B deriva de A
    d_ba = SourceDerivation(parent_source_id=src_a.id, derived_source_id=src_b.id, derivation_type="deriva_dado", is_independent=False)
    # C deriva de B
    d_cb = SourceDerivation(parent_source_id=src_b.id, derived_source_id=src_c.id, derivation_type="reproduz", is_independent=False)
    db_session.add_all([d_ba, d_cb])
    db_session.commit()

    # Verifica se a raiz de C é A
    root_of_c = src_c.get_root_source()
    assert root_of_c.id == src_a.id
    assert root_of_c.title == "Inquérito Policial 1979"
    assert src_a.is_root is True
    assert src_b.is_root is False
    assert src_c.is_root is False


def test_genealogy_service_evaluates_claim_independence(db_session):
    """
    Testa a regra anti-falsa triangulação via GenealogyService:
    Se 3 vídeos do YouTube apoiam uma claim, mas todos os 3 derivam do mesmo livro A,
    o independent_root_count DEVE ser 1, impedindo status 'confirmado'.
    """
    from app.services.genealogy_service import GenealogyService
    from app.models.event import Event
    from app.models.claim import Claim, ClaimSource

    # Cria Evento
    ev = Event(title="Evento Teste", date_display="1980", description="Descrição do teste", is_demo=True)
    db_session.add(ev)
    db_session.flush()

    # Cria Raiz e 3 Vídeos Derivados
    root_book = Source(title="Livro Fundamental", citation="Livro, 1985", source_type="academico_livro", is_demo=True)
    v1 = Source(title="Vídeo 1", citation="V1, 2020", source_type="audiovisual_youtube", is_demo=True)
    v2 = Source(title="Vídeo 2", citation="V2, 2021", source_type="audiovisual_youtube", is_demo=True)
    v3 = Source(title="Vídeo 3", citation="V3, 2022", source_type="audiovisual_youtube", is_demo=True)
    db_session.add_all([root_book, v1, v2, v3])
    db_session.flush()

    # Vincula derivações: V1, V2, V3 derivam de root_book
    for v in [v1, v2, v3]:
        deriv = SourceDerivation(parent_source_id=root_book.id, derived_source_id=v.id, derivation_type="reproduz", is_independent=False)
        db_session.add(deriv)

    # Cria Claim apoiada pelos 3 vídeos
    cl = Claim(event_id=ev.id, statement="Afirmação apoiada por 3 vídeos dependentes", confidence_level="provavel", is_demo=True)
    db_session.add(cl)
    db_session.flush()

    for v in [v1, v2, v3]:
        cs = ClaimSource(claim_id=cl.id, source_id=v.id, stance="apoia", excerpt="Trecho literal...", confidence_level="provavel")
        db_session.add(cs)
    db_session.commit()

    # Avaliação Epistemológica
    report = GenealogyService.evaluate_claim_epistemology(cl)
    assert report["evidence_count"] == 3
    assert report["independent_root_count"] == 1  # Falsa triangulação prevenida!
    assert report["suggested_status"] == "provavel"  # Não é confirmado pois só há 1 raiz independente
    assert report["has_shared_roots"] is True
    assert len(report["shared_roots"]) == 1
    assert report["shared_roots"][0]["derived_count"] == 3

