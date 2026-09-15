# Mapa Histórico, Territorial e Antropológico da Criminalidade no Rio de Janeiro

Projeto de pesquisa científica, histórica, sociológica, antropológica e geoespacial sobre a evolução da criminalidade organizada e das dinâmicas territoriais no estado do Rio de Janeiro.

O objetivo não é produzir um dashboard de ocorrências, mas uma **infraestrutura de pesquisa auditável**: cada afirmação deve poder ser rastreada até a evidência documental que a sustenta, contesta ou contextualiza.

## O que o projeto pretende responder

- Como organizações e formas de organização armada surgiram, se transformaram, se fragmentaram ou desapareceram?
- Como disputas, alianças e transformações territoriais ocorreram ao longo do tempo?
- Como Estado, sistema penitenciário, economia, política urbana e transformações sociais interagiram com essas dinâmicas?
- Como diferentes fontes descrevem os mesmos acontecimentos e por que suas versões divergem?
- O que sabemos, o que inferimos e o que permanece desconhecido?

## Princípio central

A unidade de conhecimento do projeto é a **afirmação (claim)**. Um evento histórico pode conter diversas afirmações, e cada uma delas pode possuir evidência, contestação e limitações diferentes.

O sistema preserva:

- grafia original e forma normalizada das entidades;
- expressão temporal original da fonte;
- limites temporais derivados e sua precisão;
- localização e incerteza geográfica;
- fontes primárias e secundárias;
- trecho comprobatório, página/seção e avaliação crítica;
- versões conflitantes quando existirem;
- distinção estrita entre `0` e `NULL`;
- separação entre dados históricos e dados técnicos `[DEMO]`.

## Limites éticos

O projeto possui finalidade exclusivamente acadêmica, historiográfica e sociológica. Não é ferramenta de inteligência operacional, não faz predição, não identifica alvos e não deve ser usado para planejamento de atividade ilícita.

Informações sobre pessoas e organizações devem ser apresentadas com contexto, proveniência e distinção entre alegação, registro documental e fato judicialmente estabelecido.

## Metodologia

O protocolo completo está em [`docs/metodologia/00_protocolo_de_pesquisa.md`](docs/metodologia/00_protocolo_de_pesquisa.md).

O catálogo de proveniência e custódia digital está em [`docs/metodologia/08_catalogo_de_proveniencia.md`](docs/metodologia/08_catalogo_de_proveniencia.md).

As regras metodológicas devem ser consideradas parte do próprio dataset: uma mudança na regra de normalização ou na interpretação de uma fonte pode alterar os resultados e, portanto, deve ser versionada.

## Arquitetura conceitual

```text
FONTE
  │
  ├── documento / dataset / arquivo
  │
  ▼
EVIDÊNCIA
  │  página / seção / trecho / identificador
  ▼
CLAIM (afirmação atômica)
  │
  ├── apoia
  ├── contesta
  ├── matiza
  └── menciona
  │
  ▼
EVENTO / ENTIDADE / RELAÇÃO
  │
  ├── temporalidade
  ├── território
  ├── organizações
  └── pessoas
  │
  ▼
ANÁLISE
  │
  ▼
VISUALIZAÇÃO / MAPA / LINHA DO TEMPO
```

## Temporalidade

A expressão original nunca deve ser apagada. Por exemplo, `1978` não é armazenado como se o fato tivesse ocorrido em `01/01/1978`: ele representa o intervalo de 01/01/1978 a 31/12/1978 com precisão `ano`.

A aplicação distingue `dia`, `mes`, `ano`, `decada`, `aproximado` e `desconhecido`.

## Geografia

Coordenadas não documentadas não são inventadas. Centroides de polígonos são representações cartográficas e não devem ser interpretados como local exato de um evento.

Qualquer camada territorial externa deve possuir fonte, período de referência, versão e metadados suficientes para reconstrução.

## Estrutura

```text
app/                 Aplicação e interface
app/models/          Modelo relacional e entidades
app/schemas/         Contratos e validações Pydantic
app/services/        Regras de domínio e consultas
src/                 Normalização e utilitários reutilizáveis
data/               Dados brutos, derivados e geoespaciais
docs/                Metodologia, arquitetura e documentação
research/            Perguntas, fichamentos e cadernos de pesquisa
tests/               Testes automatizados
```

## Execução

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
streamlit run app/ui/app.py
```

## Critério de qualidade científica

O projeto deve privilegiar **auditabilidade sobre aparência**. Antes de publicar uma conclusão, deve ser possível responder:

1. Qual é exatamente a afirmação?
2. Qual documento sustenta essa afirmação?
3. Onde no documento está a evidência?
4. A fonte é independente ou reproduz outra?
5. Existem fontes que contestam ou matizam a afirmação?
6. Qual é a precisão temporal e espacial real?
7. Quais limitações e lacunas permanecem?
8. Outra pessoa consegue reproduzir a transformação que levou da fonte ao resultado?

## Status

O projeto está em fase de construção. A arquitetura atual já contém entidades de eventos, claims, fontes, pessoas, organizações e regiões, mas a prioridade das próximas fases é transformar esses campos em um **protocolo de pesquisa executável e verificável**, e não apenas em metadados decorativos.
