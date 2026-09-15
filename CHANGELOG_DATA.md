# Changelog de Dados e Cartografia

Todas as alterações estruturais no modelo de dados, inclusões de fontes e atualizações de malhas cartográficas são documentadas neste arquivo.

O formato segue as diretrizes do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e versionamento semântico.

---

## [1.0.0] - 2026-09-15

### Adicionado
- **Modelo Espaço-Temporal do Atlas (FASE 1):**
  - Entidades `TerritorialDataset`, `RegionVersion`, `TerritorialRelation`, `EventFootprint`, `InstitutionalFacility` e `MovementFlow`.
  - Migrações completas via Alembic com suporte estrito a batch mode no SQLite (`ae9ba2d3d645_create_spatiotemporal_atlas_tables.py`).
  - Tipo customizado `HistoricalDate` com armazenamento padronizado em strings ISO e conversão para `datetime.date`.
- **Fundações Cartográficas e Datasets Oficiais:**
  - Cadastro de `dadosderiscos` (1.671 polígonos, SHA-256 `c0ea0aed7aab...`).
  - Cadastro de `aisp_batalhoes_pmerj` (39 polígonos, SHA-256 `33f7e28f0ba3...`).
  - Cadastro de `bairros_pcrj` (166 polígonos, SHA-256 `6c7b74046992...`).
  - Criação de 29 versões espaciais de regiões (`RegionVersion`) com sinalização estrita de anacronismo e preservação de coordenadas NULL (regiões 89, 91, 124).
- **Serviço de Atlas e Snapshots Temporais (FASE 2):**
  - `AtlasService.get_world_state` para qualquer ano entre 1958 e 2026 com camadas de territórios, facilities, fluxos, eventos e cobertura.
  - `AtlasService.get_epistemological_record` com rastreabilidade de pixel à citação documental literal.
  - `AtlasService.get_territorial_timeline` para histórico cronológico de transições de domínio por região.
  - Geração de 69 snapshots GeoJSON pré-computados (1958–2026) e `manifest.json` com hashes SHA-256.
- **Componente Cartográfico MapLibre GL 4.x (FASE 3):**
  - Componente Streamlit autônomo com WebGL, suporte a temas Claro/Escuro e hierarquia cartográfica de 10 camadas.
- **Diagnóstico de Cobertura Documental e Lacunas (FASE 4):**
  - `CoverageService` com matriz por (região, década), cálculo de Densidade de Evidências e geração de `docs/research_queue.md`.
- **Guarda Ética e Limites Cartográficos (FASE 5):**
  - `EthicsGuard` com bloqueio obrigatório de 24 meses (agregação municipal de acontecimentos recentes) e filtro anti-inteligência operacional.
  - Documento `docs/metodologia/09_etica_e_limites_do_mapa.md`.
- **Reprodutibilidade Científica (FASE 6):**
  - `CITATION.cff`, `docs/data_paper.md` e `docs/LIMITACOES.md`.

---

## [0.2.0] - 2026-09-13

### Adicionado
- Piloto de 53 eventos históricos reais (1958 a 2026) com proveniência e hashes SHA-256.
- Catálogo de fontes primárias e secundárias com suporte a genealogia de derivação (`SourceDerivation`).
- Regra inegociável ZERO ≠ NULL para ausência de dados empíricos.

---

## [0.1.0] - 2026-09-11

### Adicionado
- Estrutura inicial do projeto, banco de dados SQLite e interface Streamlit básica.
