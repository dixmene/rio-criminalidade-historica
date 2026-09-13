# 📊 RELATÓRIO DE QUALIDADE DE DADOS HISTÓRICOS (DATA QUALITY - DQ)
**Gerado em**: 2026-09-13T17:27:21.450939+00:00  
**Ambiente**: Produção / Pesquisa Histórica Auditável  
**Escopo**: Acervo de Dados Reais (`is_demo = False`)

---

## 📈 1. Sumário Executivo do Acervo

| Indicador | Quantidade Real | Quantidade Demo | Total Banco |
| :--- | :---: | :---: | :---: |
| **Eventos Históricos** | **40** | 10 | 50 |
| **Fontes Documentais** | **184** | 6 | 190 |
| **Claims (Afirmações Factuais Atomizadas)** | **7** | 0 | 7 |
| **Territórios / Regiões Mapeadas** | **22** | 10 | 32 |
| **Organizações Documentadas** | **16** | 6 | 22 |
| **Figuras e Lideranças Históricas** | **29** | 5 | 34 |

---

## ⏳ 2. Cobertura Temporal

- **Intervalo Documentado**: `1958 – 2026` (69 anos de cobertura contínua)

### Distribuição de Eventos Factuais por Década
| Década | Eventos Reais | % do Acervo |
| :---: | :---: | :---: |
| **1950s** | 1 | 2.5% |
| **1960s** | 5 | 12.5% |
| **1970s** | 6 | 15.0% |
| **1980s** | 6 | 15.0% |
| **1990s** | 6 | 15.0% |
| **2000s** | 4 | 10.0% |
| **2010s** | 5 | 12.5% |
| **2020s** | 7 | 17.5% |

### Distribuição de Fontes Documentais por Década de Publicação
| Década | Fontes Publicadas |
| :---: | :---: |
| **1960s** | 4 |
| **1980s** | 1 |
| **1990s** | 9 |
| **2000s** | 4 |
| **2010s** | 6 |
| **2020s** | 20 |
| **Sem ano** | 140 |

---

## 🛡️ 3. Auditoria de Integridade & Regras Inegociáveis

| Verificação | Status | Violacões | Tolerância |
| :--- | :---: | :---: | :---: |
| **Eventos Reais sem Fonte Comprobatória** | ✅ OK | **0** | `0` (Zero Tolerância) |
| **Claims sem Fonte Vinculada** | ✅ OK | **0** | `0` (Zero Tolerância) |
| **Registros DEMO misturados com REAL** | ✅ OK | **0** | `0` (Zero Tolerância) |
| **Inconsistências Temporais (start > end)** | ✅ OK | **0** | `0` (Zero Tolerância) |
| **Entidades Duplicadas (Nome Normalizado)** | ✅ OK | **0** | `0` |
| **Nomes Não Normalizados** | ✅ OK | **0** | `0` |
| **Territórios sem Origem Cartográfica** | ✅ OK | **0** | `0` |
| **Eventos sem Vínculo Territorial** | ℹ️ INFO | **4** | Informacional |
| **Fontes Disponíveis sem Vínculo Factual** | ℹ️ INFO | **158** | Fila de Exploração |

---

## ⚖️ 4. Epistemologia e Controvérsias Historiográficas

- **Claims com Controvérsia Registrada**: `3`

### Níveis de Confiança dos Eventos:
- **Confirmado**: 17 eventos
- **Conflitante**: 4 eventos
- **Provavel**: 19 eventos

### Níveis de Confiança dos Claims:
- **Conflitante**: 3 claims
- **Provavel**: 4 claims

---

## 🏛️ 5. Cobertura Temática (Top Entidades Documentadas)

### Top Organizações por Eventos Vinculados:
- **Comando Vermelho (Falange Vermelha / CVRL)**: 8 eventos
- **Polícia Militar do Estado do Rio de Janeiro (PMERJ)**: 5 eventos
- **Liga da Justiça / Bonde do Zinho (Milícia da Zona Oeste)**: 5 eventos
- **Supremo Tribunal Federal (STF)**: 4 eventos
- **Polícia Civil do Estado do Rio de Janeiro (PCERJ / CORE)**: 3 eventos
- **Scuderie Detetive Le Coq / Homens de Ouro**: 3 eventos
- **Batalhão de Operações Policiais Especiais (BOPE / NuCOE)**: 2 eventos
- **Cúpula da Contravenção (Jogo do Bicho)**: 2 eventos
- **Amigos dos Amigos (ADA)**: 2 eventos
- **Terceiro Comando Puro (TCP)**: 2 eventos

### Top Territórios por Eventos Vinculados:
- **Centro do Rio de Janeiro**: 15 eventos
- **Ilha Grande - Instituto Penal Cândido Mendes**: 5 eventos
- **Estácio (Rua Joaquim Palhares / Regimento Caetano de Faria)**: 3 eventos
- **Praça Seca / Morro do Bateau Mouche e Covanca**: 2 eventos
- **Quartel do CFAP / Sulacap - Sede de Fundação do NuCOE**: 1 eventos
- **Complexo da Penha (Vila Cruzeiro)**: 1 eventos
- **Sambódromo da Marquês de Sapucaí / Cidade Nova**: 1 eventos
- **Complexo do Alemão**: 1 eventos
- **Cidade de Deus**: 1 eventos
- **Complexo Penitenciário de Gericinó (Bangu I)**: 1 eventos

---
*Relatório gerado automaticamente pelo motor de DQ (`scripts/dq/calculate_data_quality.py`).*
