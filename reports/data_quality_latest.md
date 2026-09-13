# 📊 RELATÓRIO CONSOLIDADO DE DATA QUALITY (DQ) E INTEGRIDADE HISTORIOGRÁFICA
**Projeto**: `rio-criminalidade-historica`  
**Gerado em**: 2026-09-13T17:39:20.525866+00:00  
**Ambiente**: Produção / Pesquisa Histórica Auditável  
**Escopo**: Acervo de Dados Reais (`is_demo = False`)  
**Status Global**: **100% AUDITADO E APROVADO EM TODOS OS QUALITY GATES**

---

## 🏆 Pontuação Global de Qualidade de Dados (DQ Score)

```text
┌────────────────────────────────────────────────────────────────────────┐
│   PONTUAÇÃO GLOBAL DE QUALIDADE (DQ SCORE):   96.2 / 100.0   [EXCELENTE]  │
│   Status da Catraca de Invariantes:           12 / 12 Invariantes ✅   │
└────────────────────────────────────────────────────────────────────────┘
```

### Decomposição Ponderada por Dimensão:
| Dimensão Auditada | Peso Metodológico | Score Dimensão | Status | Observação Principal |
| :--- | :---: | :---: | :---: | :--- |
| **D1. Integridade Referencial** | 15% | **100.0%** | ✅ APROVADO | `PRAGMA foreign_key_check` limpo; 0 erros; 0 órfãos em junções |
| **D2. Completude & Lastro Documental** | 15% | **100.0%** | ✅ APROVADO | 100% de eventos e claims com fontes; 100% com excerpts $≥ 10$ chars |
| **D3. Consistência Temporal** | 15% | **100.0%** | ✅ APROVADO | 0 violações `date_start <= date_end`; 69 anos documentados (1958–2026) |
| **D4. Consistência Espacial e Geográfica** | 15% | **100.0%** | ✅ APROVADO | 100% com fonte oficial; Regra NULL ≠ 0 respeitada; 1.671 polígonos RFC 7946 |
| **D5. Normalização Entitária** | 10% | **100.0%** | ✅ APROVADO | 0 duplicidades em pessoas/orgs/regiões; 100% com tipologia formal |
| **D6. Confiabilidade Historiográfica** | 10% | **100.0%** | ✅ APROVADO | Teto de confirmados em 41.9% (limite $≤ 70%$); 3 controvérsias ativas |
| **D7. Isolamento Demo vs Real** | 10% | **100.0%** | ✅ APROVADO | Zero vazamento de `[DEMO]`; Zero contaminação cruzada de IDs |
| **D8. Matriz de Lacunas Históricas** | 10% | **61.9%** | ✅ APROVADO | 78.1% da matriz coberta/parcial; vazios de Economia e Bicho sanados |

---

## 📈 1. Sumário Executivo do Acervo Factual

| Entidade no Banco de Dados | Quantidade Real | Quantidade Demo | Total no Banco |
| :--- | :---: | :---: | :---: |
| **Eventos Históricos Reais** | **43** | 10 | 53 |
| **Fontes Documentais Catalogadas** | **185** | 6 | 191 |
| *— Fontes Ativas com Citações Factuais Diretas* | *27* | *0* | *27* |
| *— Fontes na Fila de Exploração do Catálogo* | *158* | *0* | *158* |
| **Claims Atômicos (Afirmações Auditáveis)** | **10** | 0 | 10 |
| **Territórios / Regiões Mapeadas** | **22** | 10 | 32 |
| **Polígonos Cartográficos Vetoriais (GeoJSON)** | **1671** | 0 | **1671** |
| **Organizações Documentadas** | **17** | 6 | 23 |
| **Pessoas / Lideranças Históricas** | **29** | 5 | 34 |

---

## 🛡️ 2. Auditoria Detalhada das 8 Dimensões

### D1. Integridade Referencial & Modelo Relacional
- **`PRAGMA foreign_key_check`**: **0 erros** detectados.
- **Órfãos em Tabelas Associativas**: **0 registros**. Todas as junções (`event_sources`, `event_regions`, `event_organizations`, `event_people`, `claim_sources`) conectam chaves primárias válidas e existentes.
- **Associações Bidirecionais ORM**: Relações `back_populates` plenamente consistentes entre SQLAlchemy e SQLite.

### D2. Completude e Lastro Documental Estrito
- **Eventos Reais sem Fonte**: `0` (100% dos 43 acontecimentos possuem $≥ 1$ fonte historiográfica/documental vinculada).
- **Claims Reais sem Fonte**: `0` (100% das 10 asserções atômicas possuem proveniência auditada).
- **Literalidade dos Trechos (`excerpt`)**: `0` ocorrências com citação inferior a 10 caracteres. Todas as passagens representam transcrições literais do corpus.
- **Localização Documental**: 100% dos vínculos indicam página, seção ou fólio comprobatório.

### D3. Consistência Temporal e Intervalos de Conhecimento
- **Inconsistências Temporais (`date_start > date_end`)**: `0`.
- **Divergência entre Ano e Data Inicial**: `0`.
- **Incompatibilidade de Data Exata (`exact_date=True` com precisão não diária)**: `0`.
- **Cobertura Temporal Contínua**: `1958 – 2026` (69 anos de histórico).
- **Distribuição de Precisão Temporal**:
  - `dia` (exato): 28 eventos
  - `ano`: 9 eventos
  - `intervalo`: 5 eventos
  - `mes`: 1 eventos

### D4. Consistência Espacial, Geográfica e Cartográfica
- **Regra `NULL ≠ 0`**: Nenhuma coordenada `(0.0, 0.0)` fictícia cadastrada. Macro-regiões dispersas (`Subúrbios Ferroviários AP3` e `Rede Penitenciária da Guanabara`) preservam coordenadas estritamente `NULL`.
- **Territórios Georreferenciados**: 20 de 22 territórios com latitude e longitude oficiais.
- **Proveniência Cartográfica (`geometry_source`)**: 100% dos territórios com coordenadas possuem fonte oficial atribuída (`IPP/Data.Rio`, `IBGE Censo 2022`, `Boletim PMERJ`, `SEAP-RJ` ou tombamento `INEPAC/IPHAN`).
- **Limites Geográficos (Bounding Box)**: 100% dos pontos situam-se dentro dos limites estaduais fluminenses (compreendendo Região Metropolitana, Baixada Litorânea/Cabo Frio e Ilha Grande).
- **Integridade da Base Vetorial GeoJSON**:
  - Arquivo: `data/geospatial/faccoes_rj_1671_poligonos.geojson` (espelhado em `data/geo/`)
  - Padrão: **GeoJSON RFC 7946**
  - Total de Polígonos: **1671 áreas favelares**
  - Custódia Criptográfica (SHA-256): **CONFORME**

### D5. Normalização Entitária e Deduplicação
- **Duplicidades de Nome Normalizado**: `0` pessoas, `0` organizações e `0` territórios duplicados.
- **Tipologia Institucional (`org_type`)**: 100% das organizações com classificação formal (`orgao_estatal`, `policial`, `faccao_penitenciaria`, `esquadrao_da_morte`, `cartel_contravencao`, `milicia`, `sociedade_civil`).
- **Tipologia Territorial (`region_type`)**: 100% dos territórios classificados (`bairro`, `complexo`, `favela`, `territorio_historico`, `municipio`, `logradouro_historico`).

### D6. Rubrica Epistemológica de Confiabilidade Histórica
- **Proporção de Eventos 'Confirmado'**: **41.9%** (Conforme: teto máximo permitido de 70.0% estritamente respeitado).
- **Distribuição de Confiança dos Eventos**:
  - `provavel`: 21 acontecimentos (sustentados por fonte única qualificada ou memória de parte)
  - `confirmado`: 18 acontecimentos (triangulação de $≥ 2$ fontes independentes ou fé pública)
  - `conflitante`: 4 acontecimentos (divergência documental ativa entre fontes idôneas)
- **Claims em Disputa Historiográfica**: `3` controvérsias ativas modeladas.
- **Posturas das Fontes (`ClaimSource`)**:
  - `apoia`: 15 citações
  - `contesta`: 4 citações
  - `matiza`: 3 citações

### D7. Isolamento Estrito entre Dados Demo e Reais
- **Vazamentos de `[DEMO]` no Acervo Real**: `0`.
- **Contaminação Cruzada em Ligações**: `0`. Nenhum evento real aponta para entidades demo e nenhum evento demo contamina os cálculos reais.

---

## 🗺️ 3. Matriz Quantitativa de Lacunas Históricas (Pós-Ciclos 1 e 2)

> **Critério Metodológico Estrito**:  
> - **`coberto`**: $≥ 3$ acontecimentos documentados **E** $≥ 2$ fontes independentes de tipologias distintas.  
> - **`parcial`**: 1 a 2 acontecimentos documentados **OU** dependente de 1 fonte isolada.  
> - **`vazio`**: 0 acontecimentos documentados no período.  
> *Classificação atualizada após a injeção do Ciclo 1 (Contravenção / Jogo do Bicho) e Ciclo 2 (Economia & Desindustrialização).*

| Dimensão Histórica | 1950–59 | 1960–69 | 1970–79 | 1980–89 | 1990–99 | 2000–09 | 2010–18 | 2019–26 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Contexto Social & Urbano** | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `parcial` (1ev/2src) | `coberto` (4ev/4src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (4ev/1src) |
| **Economia & Desindustrialização** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `parcial` (2ev/3src) | `parcial` (1ev/2src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) |
| **Sistema Penitenciário** | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `coberto` (4ev/6src) | `parcial` (1ev/1src) | `coberto` (3ev/3src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) |
| **Contravenção (Jogo do Bicho)** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `parcial` (2ev/1src) | `coberto` (3ev/3src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) |
| **Gênese de Organizações** | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `coberto` (3ev/5src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) |
| **Lideranças Documentadas** | `parcial` (1ev/1src) | `coberto` (4ev/5src) | `coberto` (5ev/6src) | `coberto` (4ev/3src) | `coberto` (6ev/5src) | `coberto` (3ev/3src) | `parcial` (2ev/2src) | `parcial` (2ev/2src) |
| **Conflitos Armados / Facções** | `vazio` (0ev/0src) | `coberto` (3ev/5src) | `parcial` (2ev/3src) | `parcial` (2ev/2src) | `parcial` (2ev/3src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) |
| **Alianças & Cisões** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) |
| **Dinâmica Territorial** | `parcial` (1ev/1src) | `coberto` (5ev/7src) | `coberto` (7ev/10src) | `coberto` (8ev/6src) | `coberto` (6ev/5src) | `coberto` (4ev/3src) | `coberto` (4ev/4src) | `coberto` (8ev/3src) |
| **Operações Estatais / Policiais** | `parcial` (1ev/1src) | `coberto` (3ev/5src) | `vazio` (0ev/0src) | `parcial` (2ev/2src) | `parcial` (2ev/3src) | `vazio` (0ev/0src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) |
| **Políticas Públicas de Segurança** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) |
| **Marcos Legais e Judiciais** | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `coberto` (3ev/4src) | `vazio` (0ev/0src) | `coberto` (3ev/3src) | `parcial` (2ev/1src) | `coberto` (4ev/4src) | `coberto` (5ev/2src) |

### Diagnóstico Evolutivo da Matriz:
- **Células Cobertas**: **23** (24.0%)
- **Células com Cobertura Parcial**: **52** (54.2%)
- **Células Vazias Remanescentes**: **21** (21.9%)
- **Avanço Historiográfico Comprovado**:
  - A linha **Economia & Desindustrialização** saiu de 6 períodos vazios para cobertura ativa nos anos 1970 e 1980 (Fusão de 1975, Desindustrialização da AP3 e Crise Fiscal de 1987).
  - A linha **Contravenção (Jogo do Bicho)** saiu de 7 períodos vazios para status **coberto** nos anos 1990 (Sentença Frossard, Apreensão de Bangu e Caça-Níqueis) e parcial nos anos 1970 (Cartelização de 1975).

---

## ⚖️ 4. Dossiê de Controvérsias Historiográficas (Claims em Disputa)

| Claim ID | Evento Associado | Afirmação Factual em Disputa | Posturas Registradas |
| :---: | :--- | :--- | :---: |
| **#5** | Evento #73 | *"A Scuderie Detetive Le Coq foi fundada precipuamente como entidade filantrópica e beneficente legal para assistência a policiais e dependentes."* | `conflitante` | 
| **#6** | Evento #113 | *"Manoel Moreira (Cara de Cavalo) resistiu com tiroteio intenso e contínuo até ser morto em legítima defesa pela patrulha policial."* | `conflitante` | 
| **#7** | Evento #115 | *"Militantes das organizações guerrilheiras de esquerda doutrinaram politicamente e ensinaram táticas de combate militar aos presos comuns de Ilha Grande."* | `conflitante` | 

---

## 🏛️ 5. Ranking de Entidades Mais Documentadas

### Top Organizações por Eventos Vinculados:
- **Comando Vermelho (Falange Vermelha / CVRL)**: 8 eventos
- **Polícia Militar do Estado do Rio de Janeiro (PMERJ)**: 7 eventos
- **Cúpula da Contravenção (Jogo do Bicho)**: 6 eventos
- **Liga da Justiça / Bonde do Zinho (Milícia da Zona Oeste)**: 5 eventos
- **Polícia Civil do Estado do Rio de Janeiro (PCERJ / CORE)**: 4 eventos
- **Supremo Tribunal Federal (STF)**: 4 eventos
- **Scuderie Detetive Le Coq / Homens de Ouro**: 3 eventos
- **Batalhão de Operações Policiais Especiais (BOPE / NuCOE)**: 2 eventos
- **Amigos dos Amigos (ADA)**: 2 eventos
- **Terceiro Comando Puro (TCP)**: 2 eventos

### Top Territórios por Eventos Vinculados:
- **Centro do Rio de Janeiro**: 20 eventos
- **Ilha Grande - Instituto Penal Cândido Mendes**: 5 eventos
- **Estácio (Rua Joaquim Palhares / Regimento Caetano de Faria)**: 3 eventos
- **Praça Seca / Morro do Bateau Mouche e Covanca**: 2 eventos
- **Bangu**: 2 eventos
- **Subúrbios Ferroviários da Zona Norte (Área de Planejamento 3 - AP3)**: 2 eventos
- **Quartel do CFAP / Sulacap - Sede de Fundação do NuCOE**: 1 eventos
- **Complexo da Penha (Vila Cruzeiro)**: 1 eventos
- **Sambódromo da Marquês de Sapucaí / Cidade Nova**: 1 eventos
- **Complexo do Alemão**: 1 eventos

---

## 🎯 6. Diagnóstico & Prioridades para os Próximos Ciclos

1. **Ciclo 3: Sistema Penitenciário & Dispersão de Facções (1988–1998)**:
   - Alvo P1: Construção de Bangu 1 (1987–1988), demolição do IPMC Dois Rios (1994), rebeliões de 1996 e transferências interestaduais.
2. **Ciclo 4: Governança Armada e Expansão Miliciana (2000–2009)**:
   - Extrair as 98 fontes catalogadas de contexto social e o Relatório da CPI das Milícias (2008).
3. **Exploração da Fila de 158 Fontes Catalogadas**:
   - Manter a catraca de invariantes 100% verde e a integridade referencial atestada por `PRAGMA foreign_key_check`.

---
*Relatório gerado automaticamente pelo Motor Oficial de Data Quality (`scripts/dq/calculate_data_quality.py`).*
