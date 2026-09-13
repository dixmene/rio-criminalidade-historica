"""
Script auxiliar para cálculo da Matriz Quantitativa de Lacunas Históricas.
12 Dimensões Historiográficas x 8 Recortes Cronológicos.
"""

from collections import defaultdict
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.database import SessionLocal
from app.models import Event

def compute_historical_gaps_matrix():
    db = SessionLocal()
    try:
        events = db.query(Event).filter(Event.is_demo == False).all()

        periods = [
            ('1950–59', 1950, 1959),
            ('1960–69', 1960, 1969),
            ('1970–79', 1970, 1979),
            ('1980–89', 1980, 1989),
            ('1990–99', 1990, 1999),
            ('2000–09', 2000, 2009),
            ('2010–18', 2010, 2018),
            ('2019–26', 2019, 2026),
        ]

        dimensions = [
            'Contexto Social & Urbano',
            'Economia & Desindustrialização',
            'Sistema Penitenciário',
            'Contravenção (Jogo do Bicho)',
            'Gênese de Organizações',
            'Lideranças Documentadas',
            'Conflitos Armados / Facções',
            'Alianças & Cisões',
            'Dinâmica Territorial',
            'Operações Estatais / Policiais',
            'Políticas Públicas de Segurança',
            'Marcos Legais e Judiciais',
        ]

        def map_event_to_dims(e):
            dims = set()
            t = (e.title + ' ' + (e.description or '') + ' ' + (e.historical_context or '')).lower()
            et = (e.event_type or '').lower()
            org_names = ' '.join(o.name.lower() for o in e.organizations)
            reg_names = ' '.join(r.name.lower() for r in e.regions)
            ppl_names = ' '.join(p.name.lower() for p in e.people)

            if len(e.people) > 0:
                dims.add('Lideranças Documentadas')
            if len(e.regions) > 0:
                dims.add('Dinâmica Territorial')
            if any(k in t or k in reg_names or k in org_names for k in ['penitenci', 'presídio', 'prisão', 'cândido mendes', 'ilha grande', 'galeria b', 'dois rios', 'cárcere', 'bangu']):
                dims.add('Sistema Penitenciário')
            if any(k in t or k in org_names or k in ppl_names for k in ['bicho', 'contravenção', 'castor de andrade', 'frossard', 'caça-níquel', 'liesa', 'biscaia', 'guimarães jorge']):
                dims.add('Contravenção (Jogo do Bicho)')
            if any(k in t for k in ['desindustrializ', 'vazio', 'fiscal', 'econôm', 'fusão', 'orçament', 'fabril', 'rendimento', 'mercadoria política', 'caça-níquel']):
                dims.add('Economia & Desindustrialização')
            if any(k in t or k in et for k in ['fundação', 'criação', 'gênese', 'instituição do novo estado']) or et in ['fundacao_organizacao', 'institucionalizacao_contravencao']:
                dims.add('Gênese de Organizações')
            if any(k in t or k in et for k in ['confronto', 'chacina', 'massacre', 'assassinato', 'tiroteio', 'emboscada', 'conflito', 'guerra', 'execução', 'sequestro']) or et in ['conflito_sucessorio_armado', 'confronto_policial', 'execucao_sumaria', 'conflito_armado']:
                dims.add('Conflitos Armados / Facções')
            if any(k in t or k in et for k in ['aliança', 'cisão', 'racha', 'cartel', 'partilha', 'acordo de partilha', 'acordo', 'rompimento', 'conquista']):
                dims.add('Alianças & Cisões')
            if any(k in t for k in ['operação', 'cerco', 'diligências', 'apreensão', 'execução de', 'confronto', 'desaparecimento', 'exceptis', 'calicute']):
                dims.add('Operações Estatais / Policiais')
            if any(k in t for k in ['política', 'programa', 'upp', 'intervenção federal', 'reorganização', 'pacifica', 'nucoe a companhia', 'fusão', 'reforma_institucional']) or et in ['politica_publica_seguranca', 'reforma_institucional_politica']:
                dims.add('Políticas Públicas de Segurança')
            if any(k in t or k in et for k in ['lei', 'decreto', 'sentença', 'adpf', 'stf', 'condena', 'julgamento', 'cpi', 'inquérito']) or any(o.acronym in ['STF', 'ALERJ', 'TJRJ', 'MPRJ'] for o in e.organizations):
                dims.add('Marcos Legais e Judiciais')
            if any(k in t for k in ['social', 'urbano', 'zaluar', 'misse', 'a máquina e a revolta', 'condomínio do diabo', 'vazios urbanos', 'favela', 'desindustrialização', 'adpf 635']):
                dims.add('Contexto Social & Urbano')
            return dims

        matrix = defaultdict(lambda: defaultdict(lambda: {'events': [], 'sources': set()}))

        for e in events:
            p_name = None
            for pname, ymin, ymax in periods:
                if e.year and ymin <= e.year <= ymax:
                    p_name = pname
                    break
            if not p_name:
                continue

            e_dims = map_event_to_dims(e)
            for d in e_dims:
                matrix[d][p_name]['events'].append(e.id)
                for s in e.sources:
                    matrix[d][p_name]['sources'].add(s.id)

        results = {
            'periods': periods,
            'dimensions': dimensions,
            'matrix': matrix,
        }
        return results
    finally:
        db.close()

if __name__ == '__main__':
    res = compute_historical_gaps_matrix()
    matrix = res['matrix']
    periods = res['periods']
    dimensions = res['dimensions']

    dim_hdr = "Dimensão Histórica"
    print(f"{dim_hdr:35s} | " + " | ".join(f"{p[0]:11s}" for p in periods))
    print("-" * 135)
    
    counts = {'coberto': 0, 'parcial': 0, 'vazio': 0}
    for d in dimensions:
        row = [f"{d:35s}"]
        for p_name, _, _ in periods:
            data = matrix[d][p_name]
            nev = len(data['events'])
            nsrc = len(data['sources'])
            if nev >= 3 and nsrc >= 2:
                status = f"cob ({nev}e/{nsrc}s)"
                counts['coberto'] += 1
            elif nev >= 1:
                status = f"par ({nev}e/{nsrc}s)"
                counts['parcial'] += 1
            else:
                status = "vaz (0e/0s)"
                counts['vazio'] += 1
            row.append(f"{status:11s}")
        print(" | ".join(row))
    
    total = sum(counts.values())
    print("-" * 135)
    print(f"Total Células: {total} | Coberto: {counts['coberto']} ({counts['coberto']/total*100:.1f}%) | Parcial: {counts['parcial']} ({counts['parcial']/total*100:.1f}%) | Vazio: {counts['vazio']} ({counts['vazio']/total*100:.1f}%)")
