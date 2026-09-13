# 📌 STATUS DO PROJETO — ONDE PARAMOS
**Data do Registro**: 13 de Setembro de 2026  
**Repositório Remoto**: [GitHub (Privado) — `dixmene/rio-criminalidade-historica`](https://github.com/dixmene/rio-criminalidade-historica)  
**Branch Atual**: `main`  
**Último Commit**: `ce8e033` (Polígonos 1.671 Áreas)  
**Qualidade Técnica**: 26/26 Testes Automatizados Aprovados (`pytest`)


---

## 🟢 1. O que foi Concluído nesta Etapa

### A. Download e Catalogação Automatizada do Acervo do NotebookLM
1. **Pipeline de Ingestão e Hashes Criptográficos (`scripts/ingestion/download_corpus.py`)**:
   - Baixou documentos integrais em `data/raw/` organizados por pastas temáticas (`academia/`, `governo/`, `processos_publicos/`, `seguranca_publica/`, `jornalismo/`).
   - Gerou metadados arquivísticos em formato JSON sidecar (`*_meta.json`) com cálculo de **SHA-256** para auditoria e custódia digital.
   - Gerou o catálogo consolidado `data/catalogo_fontes_notebooklm.json`.

2. **Documentos Físicos e Digitais no Acervo Local**:
   - `data/raw/academia/no_sapatinho_milicia_rj.pdf` (6.3 MB) — Heinrich Böll / LAV-UERJ
   - `data/raw/processos_publicos/stf_adpf_635_info_sociedade.pdf` (190 KB) — Supremo Tribunal Federal (ADPF das Favelas)
   - `data/raw/seguranca_publica/isp_balanco_indicadores_upp_2015.pdf` (564 KB) — Instituto de Segurança Pública (ISP-RJ)
   - `data/raw/academia/clio_ufpel_artigo_historico.pdf` (211 KB) — Revista Clio (UFPel)
   - `data/raw/academia/revista_passagens_uff_artigo.pdf` (584 KB) — Revista Passagens (UFF)
   - `data/raw/academia/redalyc_trajetoria_milicias_rj.pdf` (169 KB) — Redalyc
   - `data/raw/governo/sepm_rj_historico_bope.html` (98 KB) — Polícia Militar do RJ (Histórico Oficial NuCOE/BOPE)
   - `data/raw/jornalismo/elpais_adriano_nobrega_submundo_rj.html` (335 KB) — El País Brasil
   - `data/raw/jornalismo/elpais_intervencao_federal_seguranca_rj.html` (331 KB) — El País Brasil
   - `data/raw/jornalismo/ihu_upps_ajustes_fracasso.html` (55 KB) — IHU Unisinos

3. **Módulo de Extração Multi-Formato (`scripts/extraction/extract_text.py`)**:
   - Extração estruturada de páginas e texto limpo para PDFs (`pdfplumber` / `pypdf`) e páginas web (`BeautifulSoup`).

---

### B. Ingestão do Catálogo Completo de Fontes (`lista_fontes_pesquisa_rio.xlsx`)
1. **Importação Automatizada (`scripts/ingestion/import_sources_from_excel.py`)**:
   - Processou as **159 fontes** da planilha enviada pelo pesquisador, classificadas em **25 eixos temáticos**.
   - Preservou e enriqueceu as 20 fontes originais vinculadas aos 31 eventos factuais.
   - Adicionou 152 novas referências bibliográficas, totalizando **172 fontes reais** no banco de dados.
   - Mapeamento tipológico automatizado: `academico_artigo`, `documento_judicial`, `oficial_relatorio`, `jornalismo_investigativo`, `academico_livro` e `historia_oral`.
   - Exportação de backup em JSON: `data/catalogo_fontes_excel.json`.
2. **Novo Teste de Cobertura (`tests/test_sources_catalog.py`)**:
   - Validação contínua da cobertura bibliográfica ($\ge 150$ fontes reais) e presença dos eixos temáticos fundamentais.

---

### C. Povoamento Histórico Integral (1950–2026)
1. **Módulo de Povoamento Central (`scripts/ingestion/seed_full_historical_corpus.py`)**:
   - **31 Eventos Históricos Reais Documentados (1958–2026)**, cobrindo seis décadas de dinâmica territorial, política e de segurança pública.
   - **19 Territórios Históricos Reais**:
     - Georreferenciados com precisão documentada: Ilha Grande/Dois Rios, Quartel Sulacap, Centro/Rua Gonçalves Dias, Brás de Pina/Penha, Sambódromo da Marquês de Sapucaí, Estácio/Caetano de Faria, Morro do Juramento, Bangu 1, Morro do Dendê, Morro do Adeus/Alemão, Rio das Pedras, Complexo do Alemão, Morro Dona Marta, Complexo da Maré, Morro do Chapadão, Gardênia Azul, Complexo de Israel, Cidade Nova/Rua Joaquim Palhares.
     - Território histórico sem coordenadas fictícias: *Rede Penitenciária Geral da Guanabara* (`latitude=None`, `longitude=None`), cumprindo estritamente a **Regra 1 (Não invenção de coordenadas)**.
   - **14 Organizações Históricas Documentadas**: Comando Vermelho, PMERJ, NuCOE/BOPE, Scuderia Le Cocq / Homens de Ouro, Cúpula da Contravenção, LIESA, Terceiro Comando (TC), Amigos dos Amigos (ADA), Terceiro Comando Puro (TCP), Liga da Justiça, Escritório do Crime, Polícia Civil do Estado do Rio de Janeiro (PCERJ), Assembleia Legislativa do Estado do Rio de Janeiro (ALERJ) e Supremo Tribunal Federal (STF).
   - **22 Figuras e Lideranças Históricas Mapeadas**: Milton Le Cocq, Tenório Cavalcanti, Mariel Mariscot de Mattos, Rogério Lemgruber (Bagulhão), William da Silva Lima (Professor), Castor de Andrade, José Carlos dos Reis Encina (Escadinha), Paulo César Amendola, Orlando da Conceição (Orlando Jogador), Fernandinho Beira-Mar, Álvaro Malaquias Santa Rosa (Peixão), Jerônimo Guimarães Filho (Jerominho), Adriano Magalhães da Nóbrega (Capitão Adriano), Ronnie Lessa, Marielle Franco, Chiquinho Brazão, Domingos Brazão, Rivaldo Barbosa, Alba Zaluar, Michel Misse, Marcelo Freixo e Sérgio Cabral Filho.
   - **100% dos eventos possuem fontes vinculadas com citação textual literal (`excerpt`), página ou seção e validação de afirmação**.

2. **Arquivo de Auditoria e Custódia JSON (`data/corpus_historico_1950_2026.json`)**:
   - Exportação completa e auditável contendo metadados, catálogo de fontes com SHA-256 e os 31 eventos estruturados.

---

### D. Cobertura Histórica em Seis Ciclos Estruturais

| Ciclo Histórico | Recorte Temporal | Eventos Emblemáticos Ingeridos |
| :--- | :---: | :--- |
| **Ciclo 1: Esquadrões da Morte e Gênese Prisional** | 1958–1979 | Criação do Grupo de Diligências Especiais (Le Cocq); Enquadramento da LSN na Ilha Grande; Fundação do NuCOE (Boletim nº 14); Massacre da Falange Jacaré; Fundação da Falange Vermelha. |
| **Ciclo 2: Consolidação do CV e Monopólio do Bicho** | 1980–1989 | Estatutos do CV; Cerco da Rua Juramento; Assassinato de Mariel Mariscot; Fundação da LIESA; Fuga de helicóptero de Escadinha; Elevação para COE/PMERJ; Transição do foco para favelas. |
| **Ciclo 3: Fragmentação Faccional e Supermáxima** | 1990–1999 | Inauguração de Bangu 1; Demolição da prisão de Dois Rios (Ilha Grande); Surgimento do Terceiro Comando (TC); Assassinato de Orlando Jogador; Criação da facção Amigos dos Amigos (ADA). |
| **Ciclo 4: Ascensão das Milícias e CPI** | 2000–2009 | Rebelião em Bangu 1; Fundação formal do BOPE; Expansão da Liga da Justiça na Zona Oeste; CPI das Milícias na ALERJ; Abate do helicóptero Fênix no Morro dos Macacos. |
| **Ciclo 5: Era das UPPs e Intervenção Federal** | 2010–2018 | UPP Santa Marta; Ocupação militar do Complexo do Alemão; Assassinato de Marielle Franco e Anderson Gomes; Intervenção Federal na Segurança Pública do RJ. |
| **Ciclo 6: Complexo de Israel, ADPF 635 e Sentença Marielle** | 2019–2026 | Operação dos Inocentes (Escritório do Crime); Expansão do Complexo de Israel (Peixão); Liminar da ADPF 635 pelo STF; Condenação no STF dos mandantes do Caso Marielle Franco (Fev/2026). |

---

### E. Painel Interativo Streamlit & Folium
1. **Modo Histórico Real Ativo por Padrão**:
   - Slider dinâmico adaptado às datas do acervo (`1958` a `2026`).
2. **Aba "Acervo Geral de Fontes" Ampliada**:
   - Filtros dinâmicos por **Eixo Temático de Pesquisa** (25 eixos), **Tipologia Documental** e **Busca Textual** (título, autor, veículo).
   - Indicadores de custódia digital (arquivos locais com hash SHA-256 vs fontes remotas catalogadas).
   - Ficha catalográfica completa ao selecionar qualquer fonte: citação formal ABNT, notas, links de acesso e lista de eventos vinculados com trechos literais.
3. **Resolução de Namespace e Camada Cartográfica**:
   - Injeção determinística de prioridade de importação em `app/ui/app.py` eliminando colisões com o diretório `app/ui`.
   - Camada base de mapas configurada com **OpenStreetMap** (100% livre de limites ou chaves de API).

---

### F. Mapeamento Geoespacial Vetorial (1.671 Polígonos de Facções & Milícias)
1. **Pipeline de Extração Automatizado (`scripts/extraction/extract_territorial_polygons.py`)**:
   - Ingestão da base georreferenciada de perímetros territoriais aberta (`dadosderiscos.com.br`).
   - Geração de GeoJSON RFC 7946 enriquecido com centroides aproximados, nomes de comunidades e cores oficiais: `data/geospatial/faccoes_rj_1671_poligonos.geojson` (4.6 MB).
   - Cálculo de metadados sidecar e custódia digital com hash SHA-256 (`data/geospatial/faccoes_rj_1671_meta.json`).
   - Distribuição espacial identificada:
     - **Comando Vermelho (CV)**: 1.000 áreas (59,8%)
     - **Terceiro Comando Puro (TCP)**: 295 áreas (17,7%)
     - **Liga da Justiça (LJ / CL220)**: 130 áreas (7,8%)
     - **Amigos dos Amigos (ADA)**: 92 áreas (5,5%)
     - **Outras Milícias (MIL)**: 91 áreas (5,4%)
     - **Milícia de Nova Iguaçu (MNI)**: 42 áreas (2,5%)
     - **Áreas Neutras / Disputadas (NEU)**: 21 áreas (1,3%)
2. **Integração no Painel Streamlit (`app/ui/app.py`)**:
   - **Camada de Sobreposição Opcional**: Toggle na aba principal do mapa para sobrepor perímetros favelares diretamente sobre os pinos históricos (1958–2026).
   - **Nova Aba Exclusiva (`🏴 Mapeamento Territorial (1.671 Áreas)`)**:
     - Cards de indicadores e proporção territorial dos grupos armados.
     - Filtro dinâmico por facção/organização armada.
     - Localizador com autocomplete para focar e dar zoom direto em qualquer uma das 1.671 favelas/comunidades.
     - Tabela completa de exploração com exportação para CSV.
3. **Nova Suíte de Testes Cartográficos (`tests/test_geospatial_polygons.py`)**:
   - 3 novos testes automatizados validando presença dos arquivos, integridade de formato GeoJSON, limites geográficos no RJ e hashes SHA-256.

---

### G. Auditoria de Fundação Arquitetural e Epistemológica
Executada a reestruturação profunda do modelo conceitual e relacional antes da expansão de novos eventos reais, conforme os 6 pilares de rigor historiográfico:

1. **Modelo Temporal Rigoroso (Intervalos de Conhecimento)**:
   - `date_start` e `date_end` tipados como `HistoricalDate` (Date no banco), permitindo queries por sobreposição de intervalos temporais com precisão diária, mensal, anual ou decenal.
   - Preservação da grafia original da fonte em `date_display` e flag booleana `date_is_estimated`.
2. **Proveniência Granular em EventSource**:
   - Campos `page`, `section`, `excerpt` (literal mandatório), `claim` (proposição factual), `source_assessment` (crítica da fonte) e `confidence_level` por ligação fonte-evento.
3. **Desacoplamento da Confiança & Nova Entidade `Claim`**:
   - Entidade de primeiro nível `Claim` (`EVENTO -> CLAIM -> FONTE`) permitindo cadastrar afirmações factuais atômicas e confrontar visões historiográficas divergentes.
   - Suporte a posturas epistemológicas em `ClaimSource`: `apoia`, `contesta`, `matiza`.
4. **Rigor Geográfico & Regra `NULL ≠ 0`**:
   - Remoção de default artificial `Rio de Janeiro` em `Region.municipality` (ausência de dado é estritamente `NULL`).
   - Preparação para PostGIS com vigência temporal de perímetros: `geometry_type`, `geometry_valid_from`, `geometry_valid_to`, `geometry_source`, `geometry_confidence`.
5. **Diagrama Entidade-Relacionamento Auditado**:
   - Criado documento de referência com diagrama Mermaid e justificativas metodológicas em `docs/arquitetura/erd_arquitetura_auditada.md`.
6. **Suíte de Testes da Fundação (`tests/test_architectural_foundations.py`)**:
   - 5 novos testes cobrindo intervalos de conhecimento, ausência de defaults, PostGIS readiness, proveniência detalhada e posturas conflitantes de claims.
   - Total do projeto ampliado para **26/26 testes passando em 1.3s**.

---

## 🛑 2. Situação Atual do Banco de Dados (`data/rio_historico.db`)

| Entidade | Dados Históricos Reais (`is_demo=False`) | Dados Técnicos de Teste (`is_demo=True`) | Total |
| :--- | :---: | :---: | :---: |
| **Eventos Históricos** | **31** | 10 | **41** |
| **Fontes Documentais** | **173** | 6 | **179** |
| **Regiões / Territórios** | **19** | 10 | **29** |
| **Polígonos Cartográficos Vetoriais** | **1.671** | 0 | **1.671** |
| **Organizações** | **14** | 6 | **20** |
| **Pessoas / Biografias** | **22** | 5 | **27** |

---

## 🚀 3. Próximos Passos & Linhas de Pesquisa Disponíveis no Acervo

1. **Aprofundamento Temático a partir do Acervo de Fontes**:
   - **Economia & Desindustrialização**: Inserir eventos e dados da tese da "Estrutura Produtiva Oca" (Bruno Sobral) e o impacto dos vazios industriais na Zona Norte (AP3).
   - **Milícias & Minha Casa, Minha Vida**: Mapear a captura imobiliária na Zona Oeste (pesquisas da EMERJ e LAV-UERJ).
   - **Ruptura Nacional CV vs PCC (2016)**: Registrar o rompimento da aliança histórica nas prisões e reflexos nas favelas cariocas.
   - **Educação e Violência Armada (CESeC)**: Mapear o impacto das operações em escolas da Maré e Alemão.
2. **Integração de Novas Bases Geoespaciais e Abertas**:
   - **GENI/UFF + Fogo Cruzado**: Incorporar a série temporal do *Mapa dos Grupos Armados* (2006–2024) para comparar a evolução territorial histórica ano a ano.
   - **Data.Rio / IPP (Sabren)**: Ingerir limites territoriais municipais oficiais de favelas para cruzamento poligonal de sobreposição.
   - **Fogo Cruzado API**: Integrar dados de tiroteios e disparos para análise de eventos recentes.
   - **ISP-RJ**: Ingerir as camadas oficiais de AISP (Batalhões) e CISP (Delegacias).
3. **Módulo de Análise de Controvérsias Historiográficas**:
   - Expor confrontos de versões em eventos com divergência (ex: ADPF 635, origens da Falange e mortes em operações).

---

## 💻 4. Como Retomar Amanhã (Comandos Prontos)

```powershell
# 1. Entrar na pasta e ativar o ambiente
cd "C:\Users\dani\Documents\Daniel Systems"
.\.venv\Scripts\Activate.ps1

# 2. Rodar a suíte de testes (garantia de 18/18 aprovados)
python -m pytest -v

# 3. Abrir o Painel Interativo no Navegador
streamlit run app/ui/app.py
```
