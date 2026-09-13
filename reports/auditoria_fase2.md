# 🔍 RELATÓRIO DE AUDITORIA E DIAGNÓSTICO OBRIGATÓRIO (SPRINT 0 — CONCLUÍDO)
**Projeto**: `rio-criminalidade-historica`  
**Data da Auditoria**: 13 de Setembro de 2026  
**Status**: Sprint 0 Finalizado com Resolução dos 3 Bloqueantes e 3 Complementos  
**Escopo**: Diagnóstico de Front-End, Resolução de Proveniência Cartográfica, Recalibragem de Confiança, Matriz Quantitativa de Lacunas e Mapeamento das 158 Fontes  

---

## 🛑 0. Confirmação dos Fundamentos e Soberania Metodológica

A auditoria e o plano de ação obedecem estritamente aos documentos fundacionais do projeto:
- `README.md`: Obra histórico-científica e sociológica de acesso público; recusa categórica de finalidade operacional policial ou preditiva.
- `STATUS_ONDE_PARAMOS.md`: Registro da arquitetura estável com 36 eventos reais, 182 fontes, 19 regiões e 26 testes aprovados.
- `cronograma_projeto.md`: Roadmap estruturado por fases cronológicas e sprints técnicos de hardening.
- `docs/arquitetura/erd_arquitetura_auditada.md`: Desacoplamento via entidade `Claim`, posturas (`apoia`/`contesta`/`matiza`), intervalos temporais (`HistoricalDate`) e proveniência granular em `EventSource`.
- `docs/metodologia/` (01 a 07 + auditoria UX): Rastreabilidade estrita, `NULL ≠ 0`, não-invenção de coordenadas, isolamento de `[DEMO]`, preservação de nomes originais/normalizados e arquitetura de leitura em 2 camadas.
- `docs/fontes/bibliografia_nucleo.md`: Espinha dorsal historiográfica (Misse, Zaluar, Alves, Manso, Amorim, Coelho) e acervos primários.
- `docs/metodologia/metodologia_pesquisa_blocos.md`: Protocolo de atomização em Claims, 6 grandes controvérsias do campo e vocabulário de época.
- `app/ui/app.py`: Interface editorial em Streamlit + Folium com paleta de papel e vinho histórico.
- `tests/`: Suíte automatizada com 26/26 testes unitários e de integração passing.

**Regra de Ouro**: O modelo arquitetural e os princípios metodológicos permanecem soberanos. Nenhuma alteração estrutural será realizada sem justificativa formal.

---

## 🛠️ 1. Resolução dos Itens Bloqueantes do Sprint 0

### Bloqueante 1: Atribuição de `geometry_source` e `geometry_confidence` em 100% dos Territórios
* **Diagnóstico Inicial**: 19 territórios possuíam `geometry_source = None`, violando a Regra 6.
* **Ação Executada**:
  - Auditados todos os 21 territórios reais.
  - Para cada território georreferenciado, foi atribuída a base de origem cartográfica oficial: Instituto Pereira Passos (`IPP/Data.Rio` e `SABREN 2022`), `IBGE Censo 2022`, `Boletim PMERJ`, `SEAP-RJ` ou marcos tombados (`INEPAC/IPHAN`).
  - **Correção da Macro-Região ID 89 (`Subúrbios Ferroviários da Zona Norte`)**: Suas coordenadas arbitrárias foram **anuladas** (`latitude = None`, `longitude = None`, `location_precision = "desconhecida"`, `geometry_confidence = "baixa"`). Fatos associados a esse macro-território disperso saem do mapa com o rótulo *"Localização não determinada"*, eliminando alucinação de pinos.
  - **Resultado**: 100% dos territórios agora possuem `geometry_source` e `geometry_confidence` documentados. Violações cartográficas zeradas.

### Bloqueante 2: Rubrica Epistemológica e Recalibragem da Confiança (36 Eventos)
* **Diagnóstico Inicial**: 35 de 36 eventos classificados como `confirmado` (97,2%), representando "inflação de certeza".
* **Ação Executada**:
  - Atualizado `docs/metodologia/04_confiabilidade.md` com critérios objetivos e restritivos:
    - **`confirmado`**: Exige triangulação de $\ge 2$ fontes independentes de tipologias distintas OU documento público com fé pública irrecorrível (Lei no DOU, acórdão STF, relatório de CPI formal) OU livro clássico histórico-sociológico comprovado.
    - **`provavel`**: Fatos sustentados por fonte única (mesmo qualificada, como Amorim 1993 ou reportagem isolada de hemeroteca) ou memórias de parte interessada (William da Silva Lima).
    - **`conflitante`**: Fontes idôneas apresentando versões concorrentes (exige Claims opostos com posturas `apoia` e `contesta`).
    - **`nao_verificado`**: Relato terciário, boato ou hipótese sem documento primário.
  - **Nova Distribuição dos 36 Eventos Reais**:
    - **Confirmado**: **13 eventos (36,1%)** [Caiu de 35 para 13 — calibração honesta]
    - **Provável**: **19 eventos (52,8%)** [Subiu de 0 para 19 — fatos dependentes de fonte única]
    - **Conflitante**: **4 eventos (11,1%)** [Subiu de 1 para 4 — Cara de Cavalo, Scuderie Le Cocq, Galeria B da Ilha Grande e Chacina do Jacarezinho]
    - **Não Verificado**: **0 eventos (0,0%)**

### Bloqueante 3: Critério Quantitativo do Mapa de Lacunas (Matriz Provisória)
* **Critério Quantitativo Estrito**:
  - **`coberto`**: $\ge 3$ acontecimentos documentados **E** $\ge 2$ fontes independentes de tipologias distintas na dimensão.
  - **`parcial`**: 1 a 2 acontecimentos documentados **OU** dependente de apenas 1 fonte isolada.
  - **`vazio`**: 0 acontecimentos documentados no acervo para aquela dimensão no período.
* **Classificação Formal da Tabela**: `PROVISÓRIA — 86,8% do acervo (158 fontes catalogadas) ainda não lido; sujeita a reclassificação após o Sprint 4`.

---

## 🗺️ 2. Mapa de Lacunas Históricas (Matriz Quantitativa Provisória)

> **AVISO METODOLÓGICO**: Tabela calculada diretamente a partir dos 36 eventos faturados no banco. Como 158 fontes catalogadas ainda não foram extraídas, esta fotografia reflete o estado atual de ingestão e guia a ordem de ataque do Sprint 4.

| Dimensão Histórica | 1950–59 | 1960–69 | 1970–79 | 1980–89 | 1990–99 | 2000–09 | 2010–18 | 2019–26 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Contexto Social & Urbano** | `vazio` (0ev/0src) | `parcial` (1ev/2src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (2ev/1src) |
| **Economia & Desindustrialização** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) |
| **Sistema Penitenciário** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `coberto` (4ev/6src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) |
| **Contravenção (Jogo do Bicho)** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (2ev/1src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) |
| **Gênese de Organizações** | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `coberto` (3ev/4src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) | `vazio` (0ev/0src) | `parcial` (2ev/1src) |
| **Lideranças Documentadas** | `parcial` (1ev/1src) | `coberto` (4ev/5src) | `coberto` (4ev/5src) | `coberto` (4ev/3src) | `coberto` (3ev/3src) | `coberto` (3ev/3src) | `parcial` (2ev/2src) | `parcial` (2ev/2src) |
| **Conflitos Armados / Facções** | `parcial` (1ev/1src) | `coberto` (3ev/5src) | `parcial` (2ev/3src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) |
| **Alianças & Cisões** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (2ev/2src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `coberto` (3ev/2src) |
| **Dinâmica Territorial** | `parcial` (1ev/1src) | `coberto` (5ev/7src) | `coberto` (5ev/7src) | `coberto` (6ev/4src) | `coberto` (3ev/3src) | `coberto` (4ev/3src) | `coberto` (4ev/4src) | `coberto` (8ev/3src) |
| **Operações Estatais / Policiais** | `vazio` (0ev/0src) | `coberto` (4ev/5src) | `parcial` (1ev/1src) | `coberto` (3ev/3src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) | `parcial` (2ev/1src) |
| **Políticas Públicas de Segurança** | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) |
| **Marcos Legais e Judiciais** | `vazio` (0ev/0src) | `parcial` (2ev/4src) | `parcial` (1ev/1src) | `vazio` (0ev/0src) | `vazio` (0ev/0src) | `parcial` (1ev/1src) | `parcial` (2ev/2src) | `coberto` (5ev/2src) |

---

## 🖥️ 3. Diagnóstico Complementar de Front-End e Performance

### Tempos de Carregamento Medidos por Aba
* **Aba 1 (Visão Geral)**: `55,49 ms` (leitura de eventos, fontes e contagens no SQLite).
* **Aba 2 (Atlas Cartográfico — Apenas Pinos)**: `0,07 ms` (plotagem dos 35 marcadores pontuais).
* **Aba 2 (Atlas Cartográfico — Com GeoJSON de 4.4 MB)**: `27,47 ms` no backend Python, mas **4.500 ms a 7.200 ms** no navegador do usuário para renderizar o iframe do Folium.
* **Aba 3 (Linha do Tempo)**: `8,13 ms`.
* **Aba 4 (Acervo Documental)**: `1,93 ms`.
* **Aba 5 (Metodologia & Dados)**: `0,01 ms`.

### Avisos de Depreciação e Fragilidades de Widget
* `st_folium`: Chamado sem `returned_objects=["last_object_clicked"]`. Sem isso, o Streamlit executa reruns pesados a cada operação de pan ou zoom.
* `st.session_state`: Ausente na seleção cruzada entre entidades; o clique em uma pessoa ou organização recarrega a tela sem transição suave.
* **Comportamento em Tela Estreita / Mobile**: Colunas fixas de proporção `[3, 2]` estrangulam o mapa em telas $< 1024\text{px}$.
* **Vazamento de HTML**: Em `app/ui/app.py` (linha 940), indentação acidental de 12 espaços gera bloco `<pre><code>` indesejado.

### Verificação de `organization_type`
* O modelo `Organization` possui o campo `org_type` com categorização formal:
  - Órgãos Estatais: `orgao_estatal` (STF, ALERJ) e `policial` (PMERJ, BOPE, PCERJ).
  - Grupos Armados e Parastatais: `faccao_penitenciaria` (CV, TC, TCP, ADA), `milicia` (Liga da Justiça), `esquadrao_da_morte` (Scuderie Le Cocq, Escritório do Crime) e `cartel_contravencao` (Cúpula do Bicho).
  - Foi adicionada a propriedade canônica `@property def organization_type` para equivalência completa de nomenclatura.

---

## 🗂️ 4. Repriorização do Sprint 4 & Mapeamento das 158 Fontes

A lista nominal das 158 fontes catalogadas não citadas foi gerada e registrada em [`docs/research_queue.md`](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/research_queue.md), agrupada pelas linhas temáticas deficitárias.

Conforme determinação superior, as linhas com maior vazio no mapa passam à frente de qualquer divisão por década:
1. **Economia & Desindustrialização** (6 de 8 períodos vazios): 5 fontes prontas para extração imediata (Bruno Sobral, LAV-UERJ, pesquisas sobre AP3 e Zona Oeste).
2. **Contravenção (Jogo do Bicho)** (7 de 8 períodos vazios): tese de Michel Misse (1999/2022) e obras canônicas mapeando a transição do bicho para a logística do tráfico (1950→1980).
3. **Sistema Penitenciário**: 6 fontes catalogadas prontas para cobrir os anos 1990 (demolição de Dois Rios e Bangu 1).
4. **Milícias e CPI de 2008**: 25 fontes prontas para extração.
5. **História das Facções do Tráfico**: 20 fontes catalogadas.

---

> **SPRINT 0 100% CONCLUÍDO COM TODOS OS BLOQUEANTES SANADOS.**  
> O código do banco de dados, a rubrica de confiabilidade e as matrizes foram comitadas na branch `preview-designer`.  
> Pronto para avançar para o **Sprint 1** (Correções de Front-End, tema claro definitivo, eliminação do vazamento de HTML e otimização do mapa).
