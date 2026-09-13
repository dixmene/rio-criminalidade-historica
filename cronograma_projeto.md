# CRONOGRAMA DE DESENVOLVIMENTO DO PROJETO
## Mapa Histórico, Territorial e Antropológico da Criminalidade no Rio de Janeiro

---

## 📌 Status Geral do Projeto

> **Fase Atual**: `FASE 1 — Preparação do Ambiente e Infraestrutura Inicial`  
> **Próxima Fase**: `FASE 2 — Arquitetura de Pesquisa e Modelo de Dados Definitivo`

---

## FASE 0 — Planejamento e Princípios Epistemológicos
* **Objetivo**: Estabelecer os limites conceituais, objetivos acadêmicos e princípios éticos do projeto.
* **Tarefas**:
  - [x] Definir escopo estritamente histórico e antropológico (não operacional)
  - [x] Estabelecer o princípio inegociável da rastreabilidade e proveniência de fontes
  - [x] Definir política de neutralidade e registro de narrativas conflitantes
  - [x] Definir REGRA 1 (ZERO vs. DESCONHECIDO/NULL)
  - [x] Criar `CONTRIBUTING.md` com protocolos éticos
* **Critério de Conclusão**: Documentos fundamentais aprovados e integrados.

---

## FASE 1 — Ambiente e Infraestrutura Inicial
* **Objetivo**: Preparar a estrutura de diretórios profissional, ambiente Python, dependências e testes fundamentais.
* **Tarefas**:
  - [x] Criar estrutura completa de diretórios (`data/`, `docs/`, `research/`, `scripts/`, `database/`, `src/`, `tests/`, `app/`)
  - [x] Configurar ambiente Python (`.venv`, `requirements.txt`, `pyproject.toml`)
  - [x] Configurar `.gitignore` e `.env.example`
  - [x] Criar `config/settings.py` com suporte a variáveis de ambiente e caminhos
  - [x] Elaborar documentação metodológica (`docs/metodologia/`):
    - [x] `metodologia_pesquisa.md`
    - [x] `metodologia_fontes.md`
    - [x] `metodologia_geografica.md`
    - [x] `metodologia_normalizacao.md`
    - [x] `metodologia_confiabilidade.md`
  - [x] Configurar conexão com o banco de dados (`src/database/connection.py`)
  - [x] Desenvolver módulo de normalização de Unicode e REGRA 1 (`src/normalization/rules.py`)
  - [x] Criar esqueletos de scripts de ingestão, extração e normalização
  - [x] Implementar testes automatizados para normalização, regra do zero e conexão
* **Critério de Conclusão**: Todos os testes unitários passando (`pytest -v`) e banco conectável.

---

## FASE 2 — Arquitetura de Pesquisa e Modelagem Relacional Proposta
* **Objetivo**: Detalhar a arquitetura da pesquisa histórica e o ERD relacional completo.
* **Tarefas**:
  - [x] Elaborar proposta de ERD e dicionário de dados (`docs/arquitetura/erd_proposta.md`)
  - [x] Escrever DDL SQL PostgreSQL/PostGIS (`database/schema/schema.sql`)
  - [x] Implementar modelos ORM SQLAlchemy 2.0 (`database/schema/models.py`)
  - [ ] Validar ERD com requisitos de temporalidade e territorialidade
* **Dependências**: Fase 1 concluída.

---

## FASE 3 — Estratégia e Metodologia de Coleta de Fontes
* **Objetivo**: Mapear acervos, bibliotecas digitais e estruturar queries de pesquisa.
* **Tarefas**:
  - [ ] Mapear repositórios acadêmicos (Teses UFRJ, UERJ, UFF, FGV/CPDOC)
  - [ ] Mapear acervos jornalísticos (Hemeroteca Digital da BN, arquivos públicos)
  - [ ] Mapear relatórios oficiais e comissões (CPI das Milícias, Relatórios de Direitos Humanos)
  - [ ] Estruturar banco de queries de pesquisa por entidade, período e território (`research/questions/`)
* **Critério de Conclusão**: Catálogo de fontes candidatas registrado em `docs/fontes/`.

---

## FASE 4 — Piloto Histórico Controlado: Antecedentes e Década de 1970
* **Objetivo**: Realizar a primeira coleta empírica controlada para os antecedentes históricos e a década de 1970.
* **Tarefas**:
  - [ ] Ingestão de 10 a 20 documentos qualificados do período
  - [ ] Extração de texto e arquivamento bruto em `data/raw/` com hash SHA-256
  - [ ] Identificação de atores, primeiros grupos, presídios (ex: Ilha Grande) e eventos
  - [ ] Normalização e validação humana dos fatos
  - [ ] Inserção com proveniência estrita no banco
* **Critério de Conclusão**: 10–30 eventos catalogados com fontes primárias/secundárias associadas.

---

## FASE 5 — Pesquisa Histórica: Década de 1980
* **Objetivo**: Mapear a transição política, comércio atacadista de drogas, expansão territorial e surgimento das facções estruturadas.
* **Tarefas**:
  - [ ] Levantamento de fontes historiográficas sobre o período 1980–1989
  - [ ] Mapeamento das disputas territoriais iniciais e armamentos
  - [ ] Registro de lideranças documentadas da década
  - [ ] Validação cruzada e identificação de narrativas conflitantes
* **Critério de Conclusão**: Linha do tempo de 1980–1989 integrada ao banco.

---

## FASE 6 — Pesquisa Histórica: Década de 1990
* **Objetivo**: Mapear a consolidação das facções rivais (CV, TC, ADA), chacinas e intervenções estaduais.
* **Tarefas**:
  - [ ] Coleta de teses e reportagens investigativas da década de 1990
  - [ ] Mapeamento de cisões e alianças inter-organizacionais
  - [ ] Registro de territórios conflagrados e grandes operações
* **Critério de Conclusão**: Linha do tempo de 1990–1999 catalogada.

---

## FASE 7 — Pesquisa Histórica: Década de 2000
* **Objetivo**: Documentar a gênese e expansão das milícias, CPI das Milícias e início das UPPs.
* **Tarefas**:
  - [ ] Análise documental do Relatório da CPI das Milícias (2008)
  - [ ] Mapeamento da expansão paramilitar na Zona Oeste e Baixada
  - [ ] Mapeamento territorial das primeiras UPPs
* **Critério de Conclusão**: Década de 2000 completamente mapeada com proveniência.

---

## FASE 8 — Pesquisa Histórica: Década de 2010
* **Objetivo**: Mapear a crise do projeto UPP, expansão das milícias, novas cisões (TCP) e intervenção federal de 2018.
* **Tarefas**:
  - [ ] Ingestão de bases de dados de observatórios (GENI/UFF, ISP)
  - [ ] Catalogação dos conflitos territoriais na Zona Norte, Oeste e Baixada
  - [ ] Registro de operações policiais de grande impacto
* **Critério de Conclusão**: Década de 2010 documentada.

---

## FASE 9 — Pesquisa Contemporânea: Década de 2020 e Cenário Atual
* **Objetivo**: Mapear o quadro contemporâneo de narcomilícias e complexas coalizões territoriais.
* **Tarefas**:
  - [ ] Levantamento de dados recentes de institutos de pesquisa
  - [ ] Mapeamento de disputas territoriais em andamento
  - [ ] Atualização do catálogo de fontes
* **Critério de Conclusão**: Cenário contemporâneo registrado.

---

## FASE 10 — Geoprocessamento e Cartografia Histórica
* **Objetivo**: Estruturar as bases cartográficas (polígonos de bairros, complexos e municípios do RJ).
* **Tarefas**:
  - [ ] Ingestão de malhas oficiais do IBGE e IPP/Data.Rio em `data/geospatial/`
  - [ ] Delimitação de limites territoriais de comunidades e complexos históricos
  - [ ] Associação de geometrias com atributos temporais de presença/disputa
* **Critério de Conclusão**: Base geoespacial validada e integrada ao PostGIS / SQLite.

---

## FASE 11 — Pipeline Automatizado de Extração e Validação
* **Objetivo**: Refinar os módulos de parsing e identificação de entidades.
* **Tarefas**:
  - [ ] Implementar extratores especializados para diários oficiais e acervos hemerográficos
  - [ ] Criar rotinas de auditoria de duplicatas e desambiguação de nomes
  - [ ] Validador de integridade de citações
* **Critério de Conclusão**: Pipeline de ingestão robusto e testado.

---

## FASE 12 — Camada de Serviços e API de Consulta
* **Objetivo**: Desenvolver camada de acesso a dados com filtros temporais, geográficos e temáticos.
* **Tarefas**:
  - [ ] Endpoints / queries para consulta de eventos por intervalo de datas
  - [ ] Consulta de evolução territorial por grupo/facção
  - [ ] Consulta de histórico de uma região específica
  - [ ] Consulta de fontes e trechos comprobatórios
* **Critério de Conclusão**: Serviços de consulta com 100% de cobertura de testes.

---

## FASE 13 — Interface Interativa: Linha do Tempo e Mapa Geoespacial
* **Objetivo**: Construir a aplicação de exploração visual (Streamlit + Folium/Deck.gl).
* **Tarefas**:
  - [ ] Painel de controle com slider temporal contínuo (1970–Atual)
  - [ ] Mapa interativo com camadas de territórios, facções e eventos
  - [ ] Painel lateral com biografia documental de lideranças e histórico de grupos
  - [ ] Inspetor de fontes e citações literais
* **Critério de Conclusão**: Interface responsiva e funcional com renderização temporal fluida.

---

## FASE 14 — Auditoria Global de Fontes e Qualidade
* **Objetivo**: Revisar a integridade de todas as asserções e proveniências cadastradas.
* **Tarefas**:
  - [ ] Verificação de 100% dos eventos sem fonte (regra zero tolerância)
  - [ ] Auditoria de links e referências físicas
  - [ ] Revisão de relatos conflitantes
* **Critério de Conclusão**: Relatório de auditoria limpo.

---

## FASE 15 — Documentação Final, Artigos e Publicação
* **Objetivo**: Consolidar a documentação acadêmica e disponibilizar o projeto para a comunidade científica.
* **Tarefas**:
  - [ ] Elaborar artigo metodológico sobre a cartografia histórica da criminalidade
  - [ ] Publicar documentação de APIs e dicionário de dados
  - [ ] Release final da aplicação
