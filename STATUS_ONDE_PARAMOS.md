# 📌 STATUS DO PROJETO — ONDE PARAMOS
**Data do Registro**: 13 de Setembro de 2026 (02:30)  
**Repositório Remoto**: [GitHub (Privado) — `dixmene/rio-criminalidade-historica`](https://github.com/dixmene/rio-criminalidade-historica)  
**Branch Atual**: `main` (100% sincronizada)  
**Qualidade Técnica**: 16/16 Testes Automatizados Aprovados (`pytest -v`)

---

## 🟢 1. O que foi Concluído Hoje

1. **Infraestrutura Completa de Engenharia de Dados**:
   - Estrutura profissional de diretórios (`data/raw/`, `docs/`, `research/`, `scripts/`, `database/`, `src/`, `tests/`, `app/`).
   - Ambiente virtual `.venv` configurado com `pandas`, `SQLAlchemy`, `psycopg2-binary`, `pydantic`, `shapely`, `pyproj`, `folium`, `beautifulsoup4`, `pdfplumber`, `pypdf`, `pytest`.
   - `.gitignore` blindado: **zero exposição** de credenciais, bancos `.db` ou arquivos `.env`.

2. **Sprint de Hardening do MVP Realizada**:
   - **Camada Central de Normalização**: Todas as entidades possuem `original_name` (grafia histórica preservada) e `normalized_name` (maiúsculas sem acentos via decomposição canônica Unicode).
   - **REGRA 1 (ZERO vs. NULL)**: `NULL` é usado exclusivamente para dado desconhecido/não informado; `0` é preservado exclusivamente quando o valor for comprovadamente zero. Nenhuma conversão automática de vazio para zero.
   - **Proveniência Obrigatória**: A nível de schema Pydantic e serviço de domínio (`IngestionService`), eventos históricos reais (`is_demo=False`) sem fontes vinculadas com citação literal (`excerpt`) são **terminantemente rejeitados**.
   - **Isolamento de Dados [DEMO]**: Dados sintéticos possuem `is_demo=True` e `[DEMO]`. A interface gráfica possui seletor explícito de visualização para não misturar dados de teste com história real.
   - **Geografia sem Invenção de Coordenadas**: `Region.latitude` e `Region.longitude` são estritamente `nullable=True`. Se o território histórico não tiver delimitação cartográfica precisa, não são inventadas coordenadas falsas. O Folium só plota pontos documentados e a interface lista os eventos sem coordenadas em painel dedicado.
   - **Temporalidade Rigorosa**: O campo `date_display` preserva a escrita original da fonte (`"1975"`, `"maio de 1978"`), sem inventar dias ou meses fictícios. Suporte completo a datas por extenso em português.
   - **Separação Conceitual de Fontes**: Desacoplamento da tipologia do documento da avaliação de alegações específicas (feitas por afirmação em `EventSource.validation_status`).

3. **Documentação Metodológica Padronizada (`docs/metodologia/`)**:
   - `01_principios_dados.md`: Rastreabilidade integral e epistemologia histórica.
   - `02_normalizacao.md`: Decomposição Unicode e REGRA 1 (ZERO vs. NULL).
   - `03_proveniencia.md`: Validação estrita de proveniência de fontes.
   - `04_confiabilidade.md`: Níveis de evidência e gestão de versões conflitantes.
   - `05_temporalidade.md`: Política temporal de não-invenção de datas.
   - `06_geografia.md`: Gestão de incerteza geoespacial.
   - `07_demo_vs_real.md`: Protocolos de isolamento de dados DEMO.

4. **Testes Automatizados (16 Suítes Aprovadas)**:
   - Conexão e integridade de tabelas (`test_database_connection.py`).
   - Normalização Unicode e preservação de original (`test_normalization_rules.py`).
   - REGRA 1 ZERO vs. NULL (`test_zero_vs_null.py`).
   - Rejeição de eventos sem fontes (`test_provenance.py`).
   - Relações territoriais e proveniência temporal (`test_schema_models.py`).
   - Filtros temporais e territoriais (`test_services.py`).
   - **Ciclo Completo End-to-End** (`test_end_to_end.py`): Fonte $\rightarrow$ Território $\rightarrow$ Organização $\rightarrow$ Pessoa $\rightarrow$ Evento $\rightarrow$ Consulta $\rightarrow$ Rastreabilidade.

---

## 🛑 2. Onde Paramos Exatamente

* **O MVP está 100% estabilizado e blindado.**
* **Nenhum dado histórico real foi inserido ainda.**
* O banco de dados contém apenas a carga controlada de 10 eventos `[DEMO]` para testes técnicos da interface e dos filtros.
* O trabalho foi pausado exatamente no portão de entrada da **Pesquisa Histórica Real**.

---

## 🚀 3. Roteiro para o Retorno (Amanhã)

Ao reabrir o projeto, a sequência imediata será:

### Passo 1: Seleção do Corpus do Piloto Histórico (1970–1989)
* Focar no recorte inicial: **1970–1989** (Antecedentes, Ilha Grande, formação das primeiras organizações prisionais e transição política).
* Definir as primeiras **10 a 20 fontes reais**:
  1. *Obras Historiográficas/Sociológicas de Referência*:
     - Amorim, Carlos. *Comando Vermelho: A história secreta do crime organizado* (1993).
     - Misse, Michel. *Crime e Violência no Brasil Contemporâneo* (2006).
     - Zaluar, Alba. *Condomínio do Diabo* (1994).
     - Paixão, Antônio Luiz. *Recuperar ou Punir? Como o Estado trata o criminoso* (1987).
  2. *Fontes Institucionais e Arquivísticas*:
     - Acervo do Fundo DOPS / Arquivo Público do Estado do Rio de Janeiro (Aperj).
     - Documentos históricos da Comissão da Verdade do Rio de Janeiro (CEV-Rio).
  3. *Acervo Hemerográfico*:
     - Matérias históricas digitalizadas da Biblioteca Nacional (Jornal do Brasil e O Globo do período 1975–1985).

### Passo 2: Registro e Extração das Primeiras Fontes
* Utilizar `scripts/ingestion/ingest_source.py` para armazenar os documentos/trechos em `data/raw/` com cálculo de hash SHA-256.
* Fichar as fontes em `research/source_reviews/`.

### Passo 3: Ingestão dos Primeiros 10 a 20 Eventos Históricos Reais
* Utilizar `IngestionService` para cadastrar os eventos reais (`is_demo=False`), garantindo:
  - Citação literal exata em `excerpt`.
  - Página ou seção documental.
  - Vínculo com os territórios (com coordenadas reais se delimitadas, ou `None` se incertas).
  - Vínculo com lideranças e organizações documentadas.

### Passo 4: Validação no Mapa e na Linha do Tempo
* Rodar o Streamlit e testar o modo **"Apenas Dados Históricos Reais"** com a primeira base factual viva.

---

## 💻 4. Comandos Rápidos de Execução

```powershell
# 1. Ativar o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 2. Rodar todos os testes automatizados
pytest -v

# 3. Executar o Painel Interativo (Streamlit + Mapa Folium)
streamlit run app/ui/app.py

# 4. Verificar saúde e tabelas do banco de dados
python -m scripts.validation.check_db
```
