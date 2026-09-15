# Relatório de Entrega: Missão Atlas Histórico Espaço-Temporal (`claude-atlas-v1`)

**Data de Conclusão:** 15 de setembro de 2026  
**Branch:** `claude-atlas-v1`  
**Repositório:** [https://github.com/dixmene/rio-criminalidade-historica](https://github.com/dixmene/rio-criminalidade-historica)  
**Status dos Testes:** 112/112 aprovados (100% de sucesso)  
**Auditoria de Integridade da Pesquisa:** 13/13 pilares aprovados (100.0%)  
**Auditoria de Integridade Cartográfica:** 14/14 pilares aprovados (100.0%)  

---

## 1. Resumo Executivo e Cumprimento dos Critérios de Sucesso

A presente missão transformou o repositório `rio-criminalidade-historica` em uma **infraestrutura digital de pesquisa cartográfica espaço-temporal auditável e reprodutível**, orientada pelo princípio **Pixel-to-Literal-Quote** (rastreabilidade ininterrupta do polígono/ponto renderizado na tela até a citação documental probatória).

O mapa deixou de ser um componente estático ou meramente ilustrativo para se tornar a **interface primária de leitura da pesquisa historiográfica**.

### Critérios de Sucesso Atingidos:
1. **Zero Dados Inventados:** Nenhuma geometria, data, ator ou coordenada foi gerada artificialmente. Regiões sem coordenadas comprovadas (IDs 89, 91 e 124) permanecem estritamente `NULL` (cumprimento da regra inegociável `NULL ≠ 0`).
2. **Proveniência de Camadas e Hashes Criptográficos:** Todo polígono ou ponto renderizado aponta para um `dataset_id` registrado formalmente, com órgão custodiante, licença de uso, sistema de referência (CRS) e hash SHA-256.
3. **Sinalização Visual de Anacronismo Cartográfico:** Malhas contemporâneas (como os 166 bairros do IPP de 2022 ou 1.671 polígonos de comunidades de 2024) aplicadas a períodos pretéritos recebem hachurado cinza diagonal e nota metodológica explícita: *"Malha de 2022/2024 aplicada a período anterior — fronteira ilustrativa, não histórica"*.
4. **Semântica Estrita de Domínio:** Separação conceitual estrita entre `controle`, `presenca`, `influencia`, `disputa` e `presenca_estatal`. É vedada a presunção automática de controle a partir de mera presença episódica.
5. **Ciclo de Vida Institucional do Estado:** Presídios e batalhões possuem datação explícita de abertura e encerramento/implosão (`opened_at` e `closed_at`), como a desativação da Ilha Grande em 1994 ou a inauguração de Bangu 1 em 1988.
6. **Fluxos Espaço-Temporais:** Representação vetorial de fugas e transferências prisionais em massa através de arcos de deslocamento (`MovementFlow`).
7. **Embargo Ético de 24 Meses (Bloqueante):** Acontecimentos dos últimos dois anos têm coordenadas pontuais a nível de rua suprimidas, agregando-se ao centroide do município ou AISP para salvaguarda de pessoas vivas e bloqueio de inteligência tático-operacional.
8. **Substituição do Folium por MapLibre GL 4.x:** Navegação fluida com aceleração por GPU (WebGL) a 60 FPS e suporte a 69 snapshots anuais pré-computados (1958–2026).

---

## 2. Detalhamento das Fases Implementadas

### FASE 0 — Auditoria Cartográfica Inicial
- Identificação de 32 regiões cadastradas: 29 com coordenadas e 3 rigorosamente nulas (ID 89: *Subúrbios AP3*, ID 91: *Rede Penitenciária Guanabara*, ID 124: *Território Demo*).
- Análise de 1.671 polígonos faccionais, 39 AISPs da PMERJ e 166 bairros da PCRJ.
- Diagnóstico de gargalo no Folium monolítico e geração do relatório `reports/auditoria_cartografica_inicial.md` (commit `ded64a2`).

### FASE 1 — Modelos Espaço-Temporais & Migrações Alembic
- Criação dos 6 modelos em `app/models/atlas.py`:
  - `TerritorialDataset`: Metadados arquivísticos, custódia, licença, CRS e SHA-256.
  - `RegionVersion`: Versionamento com vigência temporal (`valid_from`/`valid_to`) e flag `is_anachronistic`.
  - `TerritorialRelation`: Relações com semântica estrita, `independent_root_count` e `is_contested`.
  - `EventFootprint`: Geometrias com raio de incerteza em metros (`buffer_meters`).
  - `InstitutionalFacility`: Equipamentos do Estado com ciclo de vida (`opened_at`, `closed_at`, `capacity`).
  - `MovementFlow`: Arcos de transferências carcerárias e deslocamento de lideranças.
- Implementação do tipo `HistoricalDate` com compatibilidade bidirecional entre strings ISO no SQLite e objetos `datetime.date` no Python, eliminando truncamentos numéricos.
- Migração automatizada via Alembic (`ae9ba2d3d645_create_spatiotemporal_atlas_tables.py`) em modo batch SQLite.
- Script de backfill inicial (`scripts/geospatial/backfill_atlas_foundations.py`) cadastrando os 3 datasets oficiais, 29 versões espaciais, 4 instalações institucionais e 2 fluxos iniciais.

### FASE 2 — Serviço do Atlas (`AtlasService`) & Snapshots Pré-computados
- Implementação de `app/services/atlas_service.py`:
  - `get_world_state(year, month)`: Retorna o dataclass `WorldState` com todas as camadas ativas no ano especificado, índice de densidade de evidências e metadados.
  - `get_epistemological_record(feature_id)`: Retorna a ficha documental com fontes primárias, citações literais, claims e anacronismo.
  - `get_territorial_timeline(region_id)`: Cronologia de domínio de qualquer território.
- Script `scripts/geospatial/build_temporal_snapshots.py`:
  - Geração de 69 arquivos GeoJSON pré-computados (`snapshot_1958.geojson` até `snapshot_2026.geojson`) em `data/exports/snapshots/`.
  - `manifest.json` com hash SHA-256 de cada ano e estatísticas de feições.

### FASE 3 — Componente MapLibre GL 4.x & 9 Cruzamentos Analíticos
- Criação do pacote `app/ui/components/atlas_map/` com o componente autônomo MapLibre GL 4.7.1 WebGL:
  - Basemaps Dark Matter e Positron com fallbacks resilientes.
  - Hierarquia de 10 camadas cartográficas (preenchimentos, bordas, hachuras no Canvas, círculos de instalações, pontos com buffer e arcos de fluxo).
  - Popups informativos com metadados de auditoria.
- Suporte aos 9 Modos de Cruzamento Historiográfico no Streamlit:
  1. *Tempo:* Navegação temporal contínua de 1958 a 2026.
  2. *Timeline Sincronizada:* Interação bidirecional evento $\leftrightarrow$ mapa.
  3. *Evidência:* Inspeção da Ficha Epistemológica lateral.
  4. *Organizações:* Filtro por facção armada, milícia ou presença estatal.
  5. *Pessoas:* Trajetórias biográficas e fugas de lideranças.
  6. *Instituições:* Ciclo de vida e implosão de equipamentos públicos.
  7. *Estatística:* Cruzamento com taxas de letalidade violenta por AISP.
  8. *Conflito Documental:* Destaque de áreas em disputa e afirmações divergentes.
  9. *Comparação Temporal:* Modo de comparação entre dois anos selecionados.

### FASE 4 — Diagnóstico de Cobertura Documental & Fila de Pesquisa
- Implementação de `app/services/coverage_service.py`:
  - Matriz de pares `(região, década)` calculando o Índice de Densidade de Evidências (0.0 a 1.0).
  - Categorização em *bem documentado*, *parcial*, *lacunar* e *sem documentação*.
  - Detecção de vazios históricos para direcionamento arquivístico.
- Geração automatizada de `docs/research_queue.md` com as 20 maiores prioridades de catalogação via `scripts/generate_research_queue.py`.

### FASE 5 — Guarda Ética e Filtro de Salvaguarda (`EthicsGuard` — Bloqueante)
- Implementação de `app/services/ethics_guard.py`:
  - **Embargo Temporal de 24 Meses:** Eventos de 2025 e 2026 têm coordenadas pontuais suprimidas e agregadas ao centroide municipal/AISP, sinalizando: *"Dado recente protegido por embargo ético de 24 meses"*.
  - **Filtro Anti-Inteligência Operacional:** Proibição e sanitização automática de termos como "boca de fumo", "rota de fuga ativa" e endereços particulares de pessoas vivas.
  - Capítulo metodológico formal: `docs/metodologia/09_etica_e_limites_do_mapa.md`.

### FASE 6 — Nível Acadêmico & Reprodutibilidade
- `CITATION.cff`: Citação científica padronizada no formato Citation File Format.
- `docs/data_paper.md`: Data Paper acadêmico completo com contextualização, modelo e proveniência.
- `docs/LIMITACOES.md`: Transparência crítica sobre assimetrias das fontes e viés de registro.
- `CHANGELOG_DATA.md`: Histórico de evolução estrutural das bases.
- `notebooks/01_reproducao_figuras.ipynb`: Notebook Jupyter reproduzindo as figuras da pesquisa.

### FASE 7 — Auditoria Cartográfica Automatizada (14/14 Checagens)
- Implementação de `scripts/audit_cartographic_integrity.py` validando os 14 pilares:
  1. *Zero coordenadas inventadas ou anômalas* (PASS)
  2. *Preservação estrita de NULL (IDs 89, 91, 124)* (PASS)
  3. *Validação de CRS homologado (EPSG:4326/4674)* (PASS)
  4. *Hashes SHA-256 em todas as bases oficiais* (PASS)
  5. *Rastreabilidade de RegionVersions a datasets existentes* (PASS)
  6. *Consistência de vigência temporal (`valid_from <= valid_to`)* (PASS)
  7. *Sinalização de anacronismo com notas explícitas* (PASS)
  8. *Semântica estrita homologada de relações territoriais* (PASS)
  9. *Marcação `is_contested` para territórios em disputa* (PASS)
  10. *Consistência cronológica de facilities (`opened_at <= closed_at`)* (PASS)
  11. *Geometrias válidas de fluxos espaço-temporais* (PASS)
  12. *Integridade dos 69 snapshots e do `manifest.json`* (PASS)
  13. *Ativação do Embargo Ético de 24 meses sobre anos recentes* (PASS)
  14. *Filtro anti-inteligência operacional ativo em saídas públicas* (PASS)
- Relatório formal salvo em `reports/cartographic_integrity_report.json`.
- Teste unitário em `tests/test_cartographic_integrity_audit.py`.

### FASE 8 & 9 — Telas de Apoio e Interface Unificada
- Integração no `app/ui/app.py` do MapLibre GL 4.x como motor padrão.
- Inclusão das abas de *Auditoria Cartográfica (14/14)*, *Ética & Embargo (24 Meses)* e *Data Paper & Como Citar* na seção de Metodologia.
- Preservação da lista canônica `SECOES` e `VIEW_ALIASES` para garantia de 100% de compatibilidade regressiva.

---

## 3. Matriz Comparativa: Antes vs. Depois

| Aspecto Cartográfico | Estado Anterior (`main`) | Novo Atlas (`claude-atlas-v1`) |
| :--- | :--- | :--- |
| **Motor de Renderização** | Folium em iframe HTML monolítico pesado | **MapLibre GL 4.x (WebGL) a 60 FPS** com snapshots pré-computados |
| **Rastreabilidade** | Polígono sem metadados diretos de proveniência | **Pixel-to-Literal-Quote** com Ficha Epistemológica e hash SHA-256 |
| **Anacronismo** | Malhas de 2024 exibidas em 1970 sem distinção | **Hachurado cinza diagonal** com nota explícita de anacronismo |
| **Rigor de Coordenadas** | Risco de imputação de centroides arbitrários | **`NULL ≠ 0` rigoroso**: IDs 89, 91 e 124 estritamente nulos |
| **Semântica Territorial** | Presença tratada genericamente | **5 estados rigorosos** (*controle, presenca, influencia, disputa, estatal*) |
| **Equipamentos do Estado** | Sem histórico temporal de atividade | **Ciclo de vida institucional** (`opened_at` / `closed_at`) |
| **Deslocamentos** | Inexistentes espacialmente | **Arcos vetoriais de fluxo** (`MovementFlow`) |
| **Salvaguarda Ética** | Inexistente | **Embargo bloqueante de 24 meses** e filtro anti-inteligência |
| **Cobertura e Lacunas** | Sem diagnóstico métrico de vazios | **Matriz (região, década)** e `docs/research_queue.md` |
| **Auditoria Automatizada** | 13 checagens de pesquisa histórica | **27 checagens automáticas** (13 históricas + 14 cartográficas) |
| **Suite de Testes** | 92 testes unitários | **112 testes unitários (100% passing)** |

---

## 4. Relação de Arquivos Produzidos e Modificados

```
├── CITATION.cff                                        (Novo: Citação acadêmica formal)
├── CHANGELOG_DATA.md                                   (Novo: Histórico de versões dos dados)
├── alembic.ini                                         (Novo: Configuração de migrações)
├── alembic/                                            (Novo: Ambiente de migração SQLite batch)
│   ├── env.py
│   └── versions/
│       └── ae9ba2d3d645_create_spatiotemporal_atlas_tables.py
├── app/
│   ├── models/
│   │   ├── __init__.py                                 (Atualizado: Exportação dos 6 novos modelos)
│   │   ├── atlas.py                                    (Novo: Modelos espaço-temporais FASE 1)
│   │   ├── event.py                                    (Atualizado: HistoricalDate e footprints)
│   │   └── region.py                                   (Atualizado: Relacionamento com RegionVersion)
│   ├── services/
│   │   ├── atlas_service.py                            (Novo: WorldState e Ficha Epistemológica)
│   │   ├── coverage_service.py                         (Novo: Matriz de cobertura e lacunas)
│   │   └── ethics_guard.py                             (Novo: Embargo 24m e filtro operacional)
│   └── ui/
│       ├── app.py                                      (Atualizado: Integração MapLibre e abas)
│       └── components/
│           └── atlas_map/                              (Novo: Componente MapLibre GL 4.x)
│               ├── __init__.py
│               └── maplibre_component.py
├── data/
│   ├── exports/
│   │   └── snapshots/                                  (Novo: 69 GeoJSONs anuais 1958-2026)
│   │       ├── manifest.json
│   │       └── snapshot_*.geojson
│   └── rio_historico.db                                (Atualizado: Schema e fundações backfilled)
├── docs/
│   ├── LIMITACOES.md                                   (Novo: Limitações metodológicas críticas)
│   ├── data_paper.md                                   (Novo: Data Paper para submissão científica)
│   ├── research_queue.md                               (Novo: Fila de prioridades arquivísticas)
│   └── metodologia/
│       └── 09_etica_e_limites_do_mapa.md               (Novo: Diretrizes éticas e de salvaguarda)
├── notebooks/
│   └── 01_reproducao_figuras.ipynb                     (Novo: Notebook de reprodução de figuras)
├── reports/
│   ├── auditoria_cartografica_inicial.md               (Novo: Diagnóstico da FASE 0)
│   ├── cartographic_integrity_report.json              (Novo: Relatório das 14 checagens)
│   ├── relatorio_atlas_espaco_temporal.md              (Novo: Este relatório final)
│   └── research_integrity_report.json                  (Atualizado: 13/13 checagens mantidas)
├── scripts/
│   ├── audit_cartographic_integrity.py                 (Novo: Script da auditoria cartográfica)
│   ├── generate_research_queue.py                      (Novo: Gerador da fila de pesquisa)
│   └── geospatial/
│       ├── backfill_atlas_foundations.py               (Novo: Semeador das fundações do atlas)
│       └── build_temporal_snapshots.py                 (Novo: Compilador de snapshots anuais)
└── tests/
    ├── test_atlas_models.py                            (Novo: Testes dos 6 novos modelos)
    ├── test_atlas_service.py                           (Novo: Testes do serviço e snapshots)
    ├── test_cartographic_integrity_audit.py            (Novo: Teste automatizado 14/14 checagens)
    ├── test_coverage_service.py                        (Novo: Testes da matriz de cobertura)
    └── test_ethics_guard.py                            (Novo: Testes do embargo e filtros éticos)
```

---

## 5. Instruções para Abertura do Pull Request

Conforme a Regra Inegociável nº 1, todo o trabalho foi rigorosamente desenvolvido e isolado na branch **`claude-atlas-v1`**. **Nenhum merge direto na branch `main` foi executado.**

Para abrir o Pull Request oficial:
1. Enviar os commits da branch local para o repositório remoto:
   ```bash
   git push -u origin claude-atlas-v1
   ```
2. No GitHub, abrir o PR com base em `main`:
   - **Título:** `feat(atlas): infraestrutura de atlas historico espaco-temporal auditavel e reprodutivel`
   - **Descrição:** Utilizar o conteúdo deste relatório executivo como corpo do Pull Request.
