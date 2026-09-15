# Relatório de Auditoria Cartográfica Inicial e Diagnóstico Espaço-Temporal

**Data:** 15 de Setembro de 2026  
**Branch:** `claude-atlas-v1`  
**Projeto:** Atlas Histórico da Criminalidade e Dinâmica Territorial do Rio de Janeiro (1950–2026)  
**Autor:** Engenheiro de Software Sênior, Cartógrafo Digital e Arquiteto de Dados Espaço-Temporais  

---

## 1. Sumário Executivo

Este documento cumpre a **FASE 0** da missão de construção do **Atlas Espaço-Temporal Auditável** do projeto `rio-criminalidade-historica`.

O repositório consolidou recentemente uma base epistemológica rigorosa (claims atômicas, genealogia documental anti-falsa triangulação, normalização de intervalos temporais e validação anti-alucinação textual). Contudo, a **camada geográfica e cartográfica permaneceu atrasada em relação ao rigor historiográfico do restante do sistema**.

O mapa vinha operando sob premissas que induzem ao anacronismo e à falsa precisão:
1. Exibia uma camada estática de 1.671 polígonos levantada em 2026 sobre acontecimentos de 1958 a 2025;
2. Não distinguia conceitualmente *presença armada*, *controle territorial*, *influência* e *disputa*;
3. Confundia identidade faccional (matiz de cor) com grau de certeza documental;
4. Omitia o ciclo de vida das instituições estatais (presídios, batalhões, UPPs);
5. Reconstruía todo o HTML do mapa via Folium a cada interação, inviabilizando scrubbing temporal fluido.

Abaixo é apresentado o inventário minucioso do acervo atual e o plano de transição da FASE 1 à FASE 10.

---

## 2. Inventário da Infraestrutura Atual

### 2.1 Modelos e Esquemas Relacionais (`app/models/`)

| Modelo | Tabela | Registros Atuais | Avaliação Crítica |
| :--- | :--- | :---: | :--- |
| `Region` | `regions` | **32** (22 reais / 10 demo) | Possui campos iniciais de PostGIS (`geometry_type`, `geometry_valid_from`, `geometry_valid_to`), mas **carece de versionamento real 1:N**. Uma região só pode ter 1 geometria no modelo atual. Não existe relação com dataset citável. |
| `EventRegion` | `event_regions` | **46** | Associação n-para-n simples entre Evento e Região com campo `specific_location_name`. Não modela raio de incerteza, tipo de pegada espacial ou coordenadas do evento independentes da região. |
| `Event` | `events` | **53** (43 reais / 10 demo) | Intervalos temporais estritamente normalizados (`date_start`, `date_end`, `temporal_precision`, `date_is_estimated`), mas no mapa os eventos são reduzidos a pinos pontuais no centroide da região. |
| `Claim` / `ClaimSource` | `claims` / `claim_sources` | **12** / **14** | Modelo exemplar com posturas (`apoia`, `contesta`, `matiza`), trechos literais e tipologia de discurso, porém **desconectado das geometrias dos polígonos territoriais**. |
| `Source` / `SourceDerivation` | `sources` / `source_derivations` | **291** / **2** | Árvore genealógica de proveniência ativa, porém nenhuma camada cartográfica cita formalmente o `dataset_id` de onde emanou. |

#### Diagnóstico das Coordenadas em `Region`:
- **Regiões com coordenadas válidas**: 29
- **Regiões com coordenadas estritamente `NULL` (Cumprimento da Regra 1)**: 3
  1. `ID 89`: *Subúrbios Ferroviários da Zona Norte (AP3)* — Território histórico de abrangência difusa;
  2. `ID 91`: *Rede Penitenciária da Guanabara / Rio de Janeiro* — Sistema carcerário disperso;
  3. `ID 124`: *[DEMO] Território em Litígio Histórico* — Registro de teste.

---

### 2.2 Inventário Físico de Camadas e Geometrias (`data/geospatial/`)

| Arquivo | Formato / CRS | Feições | Proveniência Declarada | Limitações Historiográficas |
| :--- | :---: | :---: | :--- | :--- |
| `faccoes_rj_1671_poligonos.geojson` | GeoJSON (RFC 7946) / `EPSG:4326` | **1.671** | `dadosderiscos.com.br` (extração: 13/09/2026, SHA-256: `c0ea0a...`) | **Camada atemporal**. Reflete o cenário contemporâneo de 2024–2026. Aplicá-la retroativamente a 1968, 1979 ou 1994 constitui anacronismo cartográfico grave. Não separa presença de controle. |
| `aisps_batalhoes_pmerj.geojson` | GeoJSON / `EPSG:4326` | **39** | PMERJ / ISP-RJ (39 Áreas Integradas de Segurança Pública) | Malha administrativa contemporânea. As circunscrições de batalhões mudaram historicamente ao longo das décadas (batalhões criados, desmembrados ou renumerados). |
| `bairros_rio_166_poligonos.geojson` | GeoJSON / `EPSG:4326` | **166** | PCRJ / Instituto Pereira Passos (Data.Rio) | Delimitação oficial municipal contemporânea do Rio de Janeiro. Não reflete a criação e emancipação histórica de bairros ou os limites do antigo Distrito Federal / Estado da Guanabara. |

---

### 2.3 Componentes de UI e Renderização Atual (`app/ui/`, `app/map/`)

1. **`app/map/builder.py`**:
   - Constrói o mapa interativo através de `folium.Map`.
   - Gera um arquivo/bloco HTML em string serializado que o Streamlit injeta via `st_folium`.
   - **Gargalo**: Cada alteração de slider ou filtro reconstrói 1.671 polígonos GeoJSON no servidor Python e retransmite o DOM HTML completo, tornando impossível a animação contínua (*scrubbing* temporal interativo).
2. **`app/map/styles.py`**:
   - Define cores sólidas para as facções (CV: vermelho, TCP: verde, ADA: amarelo, Milícias: azul, Neutro: cinza).
   - **Problema**: O mapa usa cores saturadas para os grupos e usa marcadores verdes/azuis/vermelhos para nível de evidência (Níveis A, B, C, Conflitante). O usuário não sabe se o verde é o TCP ou uma evidência Nível A confirmada.
3. **`app/ui/app.py`**:
   - O mapa é apresentado como a terceira aba ("Mapa Histórico & Territórios"), quando metodologicamente deveria ser a interface nuclear de navegação do projeto.

---

## 3. Os Sete Problemas Metodológicos Centrais

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                    PROBLEMAS IDENTIFICADOS NA AUDITORIA                    │
├────────────────────────────────────────────────────────────────────────────┤
│ 1. 1.671 polígonos atemporais  ──► Projeta o presente de 2026 no passado  │
│ 2. Sem valid_from / valid_to   ──► Anacronismo: Bairro de 2020 em 1968    │
│ 3. Presença tratada como Controle ──► Afirmação abusiva sem prova textual  │
│ 4. Linhas firmes de cartório   ──► Falsa precisão: Facção atua em zona    │
│ 5. Confiança e Ator por cor    ──► Ambiguidade visual (TCP vs Nível A)    │
│ 6. Mapa como aba secundária    ──► Produto central fica submerso          │
│ 7. Folium re-renderiza DOM     ──► Impossível scrubbing temporal fluido   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Arquitetura Alvo: O Atlas Espaço-Temporal

A reformulação proposta ataca diretamente cada um dos 7 problemas:

### 4.1 Novos Modelos de Dados (Alembic Migrations)
1. **`TerritorialDataset`**:
   - Toda malha e polígono passa a ser indexado como um dataset formal (GENI/UFF, IPP, IBGE, DadosDeRiscos, etc.) com versão, data de extração, período de referência (`reference_period_start`/`reference_period_end`), licença, metodologia e hash SHA-256.
   - O total de feições é **calculado via `COUNT` dinâmico**, jamais hardcoded em código.
2. **`RegionVersion`**:
   - Permite que uma mesma `Region` possua geometrias diferentes ao longo do tempo.
   - Campos `valid_from` e `valid_to`.
   - Detecção e marcação de **anacronismo**: Se o pesquisador inspeciona o ano de 1979 e só dispomos da malha de 2022, o sistema renderiza com **hachura diagonal cinza** e aviso formal: *"Malha de 2022 aplicada a 1979 — fronteira ilustrativa, não histórica."*
3. **`TerritorialRelation`**:
   - Separação estrita dos 4 estados de soberania:
     - `presenca`: Circulação e pontos documentados sem exclusividade armada;
     - `controle`: Imposição de regras locais, taxação e monopólio coercitivo;
     - `influencia`: Relação política, aliança contígua ou subordinação;
     - `disputa`: Conflito bélico ativo documentado entre dois ou mais atores no mesmo espaço-tempo.
   - Vinculação obrigatória a um `claim_id` e a um `excerpt` literal que sustente a classificação.
4. **`EventFootprint`**:
   - Eventos deixam de ser pontos fixos forçados.
   - Admite `local_exato`, `area_aproximada`, `regiao_referencial` e `trajetoria`, com raio de incerteza (`buffer_meters`) e indicação da fonte das coordenadas.
5. **`InstitutionalFacility`**:
   - Mapeamento das estruturas do Estado no território com ciclo de vida (`opened_at`, `closed_at`):
     - Ex: Presídio de Ilha Grande (fecha em 1994 e desaparece do mapa em 1995); Bangu 1 (inaugurado em 1988); UPPs (ciclo de instalação e desativação 2008–2025).
6. **`MovementFlow`**:
   - Arcos direcionados de origem $\rightarrow$ destino (transferências penitenciárias, deslocamentos de lideranças, fugas, operações policiais de grande escala).

### 4.2 Tecnologia e Performance Cartográfica
- **MapLibre GL JS 4.x**: Motor vetorial WebGL operando no navegador com renderização a 60 FPS.
- **Componente Streamlit Bidirecional**: Implementado em `app/ui/components/atlas_map/` via `Streamlit.setComponentValue`, permitindo selecionar uma feição e atualizar instantaneamente a Ficha Epistemológica lateral sem recarregar o mapa.
- **Precomputed Snapshots**: `scripts/geospatial/build_temporal_snapshots.py` pré-computa snapshots anuais (1958–2026) em GeoJSON com `manifest.json`, garantindo respostas $< 200\text{ ms}$ durante o scrubbing temporal.

### 4.3 Trava Ética e Limite de Escopo (`EthicsGuard`)
- **Embargo de 24 meses**: Dados dos últimos 24 meses são agregados apenas por município/AISP, nunca por comunidade, impedindo qualquer uso como inteligência tática imediata.
- **Filtro anti-inteligência operacional**: Bloqueio de cadastramento de rotas, pontos de venda ou localização de indivíduos vivos não condenados.
- **Rótulo obrigatório de finalidade acadêmica** em todas as exportações GeoJSON e CSV.

---

## 5. Cronograma de Execução Sequencial

```
[FASE 0] Auditoria e Diagnóstico Inicial (ENTREGUE NESTE RELATÓRIO)
   │
   ▼
[FASE 1] Modelo Espaço-Temporal + Migrations Alembic + Backfill Conservador
   │
   ▼
[FASE 2] atlas_service.py + Snapshots Pré-computados + Testes Unitários
   │
   ▼
[FASE 3] Componente MapLibre GL + 9 Modos Cartográficos + Aparato Formal
   │
   ▼
[FASE 4] coverage_service.py + Mapa da Cobertura Documental + research_queue.md
   │
   ▼
[FASE 5] ethics_guard.py (Embargo 24m + Limites Operacionais - BLOQUEANTE)
   │
   ▼
[FASE 6] Citação Acadêmica (CITATION.cff, Zenodo, data_paper.md, LIMITACOES.md)
   │
   ▼
[FASE 7] audit_cartographic_integrity.py (14 Checagens Cartográficas Automatizadas)
   │
   ▼
[FASE 8] Suíte de Testes Automatizados (pytest)
   │
   ▼
[FASE 9] Telas de Apoio e Navegação Editorial
   │
   ▼
[FASE 10] Relatório Final e Abertura de PR (claude-atlas-v1 -> main)
```

**Status da FASE 0:** `DONE`.  
Aprovado para início imediato da **FASE 1**.
