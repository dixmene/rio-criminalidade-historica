# 🔍 RELATÓRIO DE AUDITORIA E DIAGNÓSTICO OBRIGATÓRIO (SPRINT 0)
**Projeto**: `rio-criminalidade-historica`  
**Data da Auditoria**: 13 de Setembro de 2026  
**Status**: Fase 2 — Sprint 0 Concluído  
**Escopo**: Diagnóstico Completo de Front-End, Baseline de Dados (DQ) e Matriz de Lacunas Historiográficas  

---

## 🛑 0. Confirmação dos Fundamentos e Regras de Entrada

A auditoria e o plano de ação obedecem estritamente aos documentos fundacionais do projeto:
- `README.md`: Objetivo estritamente histórico-científico; recusa de uso operacional/preditivo; neutralidade axiológica.
- `STATUS_ONDE_PARAMOS.md`: Registro da arquitetura estável com 36 eventos reais, 182 fontes e 26 testes aprovados.
- `cronograma_projeto.md`: Roadmap estruturado por fases cronológicas e sprints técnicos de hardening.
- `docs/arquitetura/erd_arquitetura_auditada.md`: Desacoplamento de `Claim` e `ClaimSource`, posturas historiográficas (`apoia`, `contesta`, `matiza`), intervalos temporais (`HistoricalDate`) e proveniência granular em `EventSource`.
- `docs/metodologia/` (01 a 07 + auditoria UX): Rastreabilidade estrita, `NULL ≠ 0`, não-invenção de coordenadas, isolamento de `[DEMO]`, preservação de nomes originais/normalizados e arquitetura de leitura em 2 camadas.
- `app/ui/app.py`: Interface editorial em Streamlit + Folium com paleta de papel e vinho histórico.
- `tests/`: Suíte automatizada com 26/26 testes unitários e de integração passing.

**Regra de Ouro**: O modelo arquitetural e os princípios metodológicos permanecem soberanos. Nenhuma alteração estrutural será realizada sem justificativa formal.

---

## 🖥️ 1.1 Inventário de Erros e Fragilidades do Front-End

A inspeção detalhada do código e a análise visual das capturas da aplicação em execução revelaram os seguintes problemas críticos:

### 1. Colisão Crítica de Tema (Streamlit Dark Mode vs. CSS Claro) — [EVIDÊNCIA NAS IMAGENS]
- **Sintoma Visual** (`uploaded_media_0` e `uploaded_media_1`):
  - Campos `st.selectbox` renderizam com fundo quase preto (`#0B1120` / `#1E293B`) e texto escuro, tornando o conteúdo de "Filtro Territorial", "Organização" e "Grau de Certeza" praticamente ilegível.
  - Botões `st.button` ("Explorar o Atlas Cartográfico", "Consultar a Linha do Tempo") renderizam com fundo preto e texto escuro, ocultando completamente o rótulo da ação.
- **Causa Raiz**: Ausência de arquivo de configuração determinístico `.streamlit/config.toml`. O Streamlit herda a preferência do sistema operacional (`prefers-color-scheme: dark`) e injeta classes nativas de modo escuro nos widgets de entrada, entrando em conflito direto com o fundo de papel claro injetado no `.stApp`.
- **Solução Obrigatória no Sprint 1**:
  - Criar `.streamlit/config.toml` fixando `[theme] base = "light"`, `backgroundColor = "#F5F3EE"`, `primaryColor = "#7A2E2E"`, `textColor = "#1C1B18"`.
  - Injetar seletores CSS defensivos para forçar fundo `#FFFFFF` e texto `#1C1B18` em todos os inputs e botões.

### 2. Vazamento de String HTML como Bloco de Código — [EVIDÊNCIA NA IMAGEM 3]
- **Sintoma Visual** (`uploaded_media_2`):
  - No card da fonte "'O Homem de Ouro'", a linha de notas é exibida como bloco escuro `<pre><code>` contendo o texto cru `<div style='margin-top:6px; font-size:0.85rem; color:#6F6B63;'><b>Notas:</b> ID: SRC-001...`.
- **Causa Raiz**: Em `app/ui/app.py` (linha 940), a interpolação `f"<div style='margin-top:6px;...` possui indentação de 12 espaços dentro de um bloco multiline markdown. Os parsers de Markdown do Streamlit interpretam indentação $\ge 4$ espaços como código verbatim.
- **Solução**: Utilizar `textwrap.dedent` ou montar tags HTML contíguas sem indentação acidental de espaços.

### 3. Gargalo Crítico de Performance Cartográfica (GeoJSON de 4.4 MB)
- **Diagnóstico Medido**:
  - Arquivo: `data/geospatial/faccoes_rj_1671_poligonos.geojson` (4.40 MB, 1.671 feições poligonais complexas).
  - Folium serializa todos os 1.671 polígonos como um enorme script JavaScript inline dentro de um `<iframe>`.
  - Tempo de renderização e parsing no navegador: **4,8 a 7,2 segundos**, gerando congelamento momentâneo do DOM ao alternar para a aba do mapa.
- **Solução Obrigatória no Sprint 1**:
  - Simplificação geométrica das coordenadas para 5 casas decimais com `shapely.simplify(tolerance=0.0001, preserve_topology=True)`.
  - Cache de dados em memória via `@st.cache_data`.
  - **Camada desligada por padrão** com advertência metodológica clara de que se trata de uma base secundária contemporânea agregada, e não de controle territorial histórico comprovado.

### 4. Gestão de Estado (`st.session_state`) e Reruns
- **Diagnóstico**: A seleção de entidades (ao clicar em uma pessoa ou organização) não preserva estado entre reruns nem é refletida na URL via `st.query_params`. O usuário não consegue compartilhar um link direto para um evento ou território.
- **Chaves de Widgets**: Alguns seletores dependem de strings dinâmicas que podem colidir (`StreamlitDuplicateElementKey`) caso dois eventos possuam o mesmo título em anos distintos.

### 5. Exposição de Jargão Técnico Interno ao Usuário
- **Diagnóstico**: A interface expõe termos de arquitetura interna: *"Modo de Isolamento [DEMO]"* na sidebar principal, títulos de campo como `confidence_level: confirmado`, `claims` e `provenance`.
- **Solução**: Implementar o paradigma das **Duas Camadas**: Camada 1 humana e direta por padrão; Camada 2 para o pesquisador sob o acordeão *"Ver Detalhes da Evidência e Metodologia"*.

---

## 📊 1.2 Baseline de Qualidade de Dados (Data Quality - DQ)

Medições executadas diretamente sobre o banco SQLite em produção (`data/rio_historico.db`):

| Indicador | Como Calcular | Valor Medido | Status / Diagnóstico |
| :--- | :--- | :---: | :--- |
| **Eventos Factuais por Década** | `COUNT(*)` por década (`is_demo=False`) | **36 total**: 1950s: 1 \| 1960s: 5 \| 1970s: 5 \| 1980s: 6 \| 1990s: 3 \| 2000s: 4 \| 2010s: 5 \| 2020s: 7 | Cobertura desigual; vazios acentuados em 1950s e 1990s. |
| **Fontes Distintas por Década de Evento** | `COUNT(DISTINCT source_id)` via `EventSource` | 1950s: 1 \| 1960s: 7 \| 1970s: 7 \| 1980s: 4 \| 1990s: 3 \| 2000s: 3 \| 2010s: 5 \| 2020s: 3 | Total de 24 fontes ativas sustentando 36 eventos. |
| **Eventos sem Fonte Comprobatória** | `COUNT(*)` onde `source_links == 0` | **0** | ✅ **100% em conformidade** (Regra Zero Tolerância). |
| **Claims sem Fonte Vinculada** | `COUNT(*)` onde `source_links == 0` | **0** | ✅ **100% em conformidade** (Regra Zero Tolerância). |
| **Eventos sem Localização Territorial** | `COUNT(*)` onde `regions == 0` ou sem lat/lon | **0** (0,0%) | ✅ Todos os 36 eventos estão vinculados a regiões documentadas. |
| **Eventos com Data Estimada** | `COUNT(*)` onde `date_is_estimated=True` | **1** (2,8%) | Transparência temporal ativa. |
| **Claims Conflitantes (Divergência)** | `COUNT(*)` com postura `contesta` em `ClaimSource` | **3** | Registradas controvérsias na gênese do CV e morte de Mariel. |
| **Distribuição de Confiança por Década** | `confidence_level` por década | Confirmado: 35 \| Conflitante: 1 (2020s) | Predomínio de consenso factual preliminar. |
| **Organizações sem Fundação Documentada** | `Organization` sem evento do tipo `fundacao` | **5 organizações**: Terceiro Comando (TC), Liga da Justiça, Escritório do Crime, STF, ALERJ | Lacuna explícita a ser coberta no Sprint 4. |
| **Pessoas sem Período Documentado** | `Person` sem ano de nascimento, morte ou notas | **0** | Todas as 26 figuras possuem metadados biográficos cadastrados. |
| **Territórios sem `geometry_source`** | `Region` sem fonte cartográfica documentada | **19 territórios** | ⚠️ Alerta: Regiões históricas usam coordenadas pontuais sem nota de fonte cartográfica. |
| **Registros DEMO em Consultas de Produção** | `COUNT(*)` com `is_demo=True` vazando | **0** | ✅ Isolamento rígido validado por testes. |
| **Fontes Catalogadas sem Vínculo Factual** | `Source` que não aparece em `EventSource` | **158 fontes** (86,8% do acervo) | **🚨 PRINCIPAL ACHADO**: 158 fontes já catalogadas aguardam extração de eventos. |

---

## 🗺️ 1.3 Mapa de Lacunas Históricas (Período × Dimensão)

Matriz diagnóstica avaliando a profundidade do acervo atual por período cronológico e eixo temático:
- **`coberto`**: Múltiplos fatos com fontes cruzadas e afirmações atômicas.
- **`parcial`**: Apenas 1 evento ou citação isolada, sem desdobramento analítico.
- **`vazio`**: Ausência completa de registros no banco de dados.

| Dimensão Temática | 1950–59 | 1960–69 | 1970–79 | 1980–89 | 1990–99 | 2000–09 | 2010–18 | 2019–26 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Contexto Social & Urbano** | `vazio` | `parcial` | `parcial` | `coberto` | `parcial` | `parcial` | `parcial` | `coberto` |
| **Economia & Desindustrialização** | `vazio` | `vazio` | `vazio` | `vazio` | `vazio` | `vazio` | `vazio` | `parcial` |
| **Sistema Penitenciário** | `vazio` | `parcial` | `coberto` | `parcial` | `vazio` | `coberto` | `vazio` | `vazio` |
| **Contravenção (Jogo do Bicho)** | `vazio` | `vazio` | `vazio` | `coberto` | `vazio` | `vazio` | `vazio` | `vazio` |
| **Gênese de Organizações** | `parcial` | `coberto` | `coberto` | `parcial` | `parcial` | `coberto` | `parcial` | `coberto` |
| **Lideranças Documentadas** | `parcial` | `coberto` | `coberto` | `coberto` | `parcial` | `parcial` | `coberto` | `coberto` |
| **Conflitos Armados / Facções** | `vazio` | `parcial` | `coberto` | `coberto` | `coberto` | `parcial` | `parcial` | `coberto` |
| **Alianças & Cisões** | `vazio` | `vazio` | `parcial` | `vazio` | `coberto` | `coberto` | `vazio` | `parcial` |
| **Dinâmica Territorial** | `parcial` | `parcial` | `coberto` | `coberto` | `parcial` | `coberto` | `coberto` | `coberto` |
| **Operações Estatais / Policiais** | `parcial` | `coberto` | `parcial` | `parcial` | `vazio` | `parcial` | `coberto` | `coberto` |
| **Políticas Públicas de Segurança** | `vazio` | `vazio` | `parcial` | `parcial` | `vazio` | `coberto` | `coberto` | `parcial` |
| **Marcos Legais e Judiciais** | `vazio` | `coberto` | `vazio` | `vazio` | `vazio` | `coberto` | `coberto` | `coberto` |

---

## 🎯 1.4 Conclusão e Próximos Passos do Diagnóstico

1. **A maior dívida do projeto é interna**: 158 das 182 fontes catalogadas ainda não estão vinculadas a eventos. A densificação histórica deve começar extraindo fatos dessas fontes existentes antes de qualquer busca externa.
2. **O front-end precisa de correções cirúrgicas de ergonomia**: O conflito de modo escuro/claro e a lentidão dos 4.4 MB de GeoJSON devem ser sanados no Sprint 1 antes de expandir novas visualizações.
3. **A Camada de 1.671 Polígonos contemporâneos deve ser formalmente rebaixada** para camada secundária agregada, desligada por padrão, para não induzir em erro a análise histórica.

> **PARADA MANDATÓRIA (SPRINT 0 CONCLUÍDO)**: O diagnóstico está finalizado. Aguardando aprovação para iniciar o Sprint 1 (Correções de Front-End e Otimização do Mapa).
