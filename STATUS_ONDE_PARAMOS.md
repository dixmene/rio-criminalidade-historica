# 📌 STATUS DO PROJETO — ONDE PARAMOS
**Data do Registro**: 13 de Setembro de 2026  
**Repositório Remoto**: [GitHub (Privado) — `dixmene/rio-criminalidade-historica`](https://github.com/dixmene/rio-criminalidade-historica)  
**Branch Atual**: `main`  
**Qualidade Técnica**: 17/17 Testes Automatizados Aprovados (`python -m pytest -v`)

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

### B. Povoamento Histórico Integral (1950–2026)
1. **Módulo de Povoamento Central (`scripts/ingestion/seed_full_historical_corpus.py`)**:
   - **31 Eventos Históricos Reais Documentados (1958–2026)**, cobrindo seis décadas de dinâmica territorial, política e de segurança pública.
   - **20 Fontes Históricas Reais** cadastradas com citação formal em norma ABNT, autoria, tipologia, URLs arquivísticas e hashes SHA-256 para arquivos locais.
   - **19 Territórios Históricos Reais**:
     - Georreferenciados com precisão documentada: Ilha Grande/Dois Rios, Quartel Sulacap, Centro/Rua Gonçalves Dias, Brás de Pina/Penha, Sambódromo da Marquês de Sapucaí, Estácio/Caetano de Faria, Morro do Juramento, Bangu 1, Morro do Dendê, Morro do Adeus/Alemão, Rio das Pedras, Complexo do Alemão, Morro Dona Marta, Complexo da Maré, Morro do Chapadão, Gardênia Azul, Complexo de Israel, Cidade Nova/Rua Joaquim Palhares.
     - Território histórico sem coordenadas fictícias: *Rede Penitenciária Geral da Guanabara* (`latitude=None`, `longitude=None`), cumprindo estritamente a **Regra 1 (Não invenção de coordenadas)**.
   - **14 Organizações Históricas Documentadas**: Comando Vermelho, PMERJ, NuCOE/BOPE, Scuderia Le Cocq / Homens de Ouro, Cúpula da Contravenção, LIESA, Terceiro Comando (TC), Amigos dos Amigos (ADA), Terceiro Comando Puro (TCP), Liga da Justiça, Escritório do Crime, Polícia Civil do Estado do Rio de Janeiro (PCERJ), Assembleia Legislativa do Estado do Rio de Janeiro (ALERJ) e Supremo Tribunal Federal (STF).
   - **22 Figuras e Lideranças Históricas Mapeadas**: Milton Le Cocq, Tenório Cavalcanti, Mariel Mariscot de Mattos, Rogério Lemgruber (Bagulhão), William da Silva Lima (Professor), Castor de Andrade, José Carlos dos Reis Encina (Escadinha), Paulo César Amendola, Orlando da Conceição (Orlando Jogador), Fernandinho Beira-Mar, Álvaro Malaquias Santa Rosa (Peixão), Jerônimo Guimarães Filho (Jerominho), Adriano Magalhães da Nóbrega (Capitão Adriano), Ronnie Lessa, Marielle Franco, Chiquinho Brazão, Domingos Brazão, Rivaldo Barbosa, Alba Zaluar, Michel Misse, Marcelo Freixo e Sérgio Cabral Filho.
   - **100% dos eventos possuem fontes vinculadas com citação textual literal (`excerpt`), página ou seção e validação de afirmação**.

2. **Arquivo de Auditoria e Custódia JSON (`data/corpus_historico_1950_2026.json`)**:
   - Exportação completa e auditável contendo metadados, catálogo de fontes com SHA-256 e os 31 eventos estruturados com seus relacionamentos territoriais, institucionais e biográficos.

---

### C. Cobertura Histórica em Seis Ciclos Estruturais

| Ciclo Histórico | Recorte Temporal | Eventos Emblemáticos Ingeridos |
| :--- | :---: | :--- |
| **Ciclo 1: Esquadrões da Morte e Gênese Prisional** | 1958–1979 | Criação do Grupo de Diligências Especiais (Le Cocq); Enquadramento da Lei de Segurança Nacional na Ilha Grande; Fundação do NuCOE (Boletim nº 14); Massacre da Falange Jacaré no IPM; Fundação da Falange Vermelha. |
| **Ciclo 2: Consolidação do CV e Monopólio do Bicho** | 1980–1989 | Difusão das primeiras cartas/estatutos do CV; Cerco da Rua Juramento e consagração pública do CV; Assassinato de Mariel Mariscot no Centro; Fundação da LIESA; Fuga de helicóptero de Escadinha; Elevação do NuCOE para Companhia de Operações Especiais (COE); Transferência gradual de líderes para favelas. |
| **Ciclo 3: Fragmentação Faccional e Supermáxima** | 1990–1999 | Inauguração do Presídio Bangu 1; Demolição do Presídio de Dois Rios na Ilha Grande; Dissidência e surgimento do Terceiro Comando (TC); Assassinato de Orlando Jogador e racha do CV; Criação da facção Amigos dos Amigos (ADA). |
| **Ciclo 4: Ascensão das Milícias e CPI** | 2000–2009 | Rebelião e consolidação nacional em Bangu 1; Criação formal do Batalhão de Operações Policiais Especiais (BOPE); Expansão da Liga da Justiça e milícias na Zona Oeste; CPI das Milícias na ALERJ; Abate do helicóptero Fênix no Morro dos Macacos. |
| **Ciclo 5: Era das UPPs e Intervenção Federal** | 2010–2018 | Implantação da primeira UPP piloto (Santa Marta); Ocupação do Complexo do Alemão pelas Forças Armadas; Assassinato de Marielle Franco e Anderson Gomes; Intervenção Federal na Segurança Pública do RJ. |
| **Ciclo 6: Complexo de Israel, ADPF 635 e Sentença Marielle** | 2019–2026 | Operação dos Inocentes e desarticulação do Escritório do Crime; Criação e expansão do Complexo de Israel por Peixão; Concessão da liminar na ADPF 635 pelo STF (ADPF das Favelas); Condenação no STF dos mandantes do Caso Marielle Franco (Fevereiro/2026). |

---

### D. Unificação da Arquitetura e Suíte de Testes
1. **Unificação da Conexão com o Banco**:
   - `app/config.py` e `config/settings.py` unificados para apontar de forma determinística para `data/rio_historico.db`.
2. **Suíte de Testes Automatizados (17/17 Aprovados)**:
   - Testes de integridade do acervo (`tests/test_real_pilot_data.py`), regras de normalização (`test_normalization_rules.py`), zero vs null (`test_zero_vs_null.py`), proveniência estrita (`test_provenance.py`), modelos (`test_models.py`, `test_schema_models.py`), serviços (`test_services.py`), ciclo de vida (`test_end_to_end.py`) e conexão (`test_database_connection.py`).
3. **Painel Interativo (Streamlit + Folium)**:
   - Configurado por padrão no modo **"Apenas Dados Históricos Reais"**, com slider temporal dinâmico adaptado aos limites do banco real (`1958` a `2026`).
   - Cards de eventos com citações literais das fontes, seções/páginas e indicação de status de validação factual.
   - Painel cartográfico com marcadores georreferenciados e gaveta retrátil dedicada a territórios não-georreferenciados.

---

## 🛑 2. Situação Atual do Banco de Dados (`data/rio_historico.db`)

| Entidade | Dados Históricos Reais (`is_demo=False`) | Dados Técnicos de Teste (`is_demo=True`) | Total |
| :--- | :---: | :---: | :---: |
| **Eventos Históricos** | **31** | 10 | 41 |
| **Fontes Documentais** | **20** | 6 | 26 |
| **Regiões / Territórios** | **19** | 10 | 29 |
| **Organizações** | **14** | 6 | 20 |
| **Pessoas / Biografias** | **22** | 5 | 27 |

---

## 🚀 3. Próximos Passos Recomendados

1. **Refinamento Cartográfico Vetorial (GeoJSON)**:
   - Inserir arquivos de delimitação poligonal em `data/geospatial/` para complexos favelares e áreas de atuação de milícias (ex: Maré, Alemão, Penha, Cidade de Deus, Rio das Pedras, Complexo de Israel) para visualização combinada de pontos e polígonos.
2. **Interface Visual para Narrativas Conflitantes**:
   - Exibir na interface visual do Streamlit alertas e abas de controvérsias historiográficas para eventos com `validation_status="conflitante"` ou com múltiplas fontes divergentes (ex: controvérsia da fundação do CV e mortes em operações policiais).
3. **Exportação de Relatórios de Pesquisa**:
   - Adicionar botão de download no Streamlit para geração de dossiês bibliográficos/metodológicos em formato Markdown ou PDF a partir dos filtros ativos na tela.

---

## 💻 4. Comandos para Execução e Demonstração

```powershell
# 1. Ativar o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 2. Rodar todos os testes automatizados (17 testes)
python -m pytest -v

# 3. Executar o Painel Interativo no Navegador
streamlit run app/ui/app.py

# 4. Re-executar ou atualizar a carga histórica integral se necessário
python -m scripts.ingestion.seed_full_historical_corpus
```
