# Mapa Histórico, Territorial e Antropológico da Criminalidade no Rio de Janeiro

Projeto de pesquisa científica, histórica, sociológica e antropológica sobre a evolução da criminalidade organizada e dinâmicas territoriais no estado do Rio de Janeiro.

---

## 🏛️ 1. Objetivo e Escopo

O objetivo deste projeto é construir uma **base histórica documentada, auditável e reproduzível** acompanhada de um **mapa geoespacial interativo associado a uma linha do tempo**, permitindo o estudo analítico e historiográfico de:

* Origem, formação e evolução de facções criminosas e grupos paramilitares (milícias);
* Lideranças históricas documentadas;
* Dinâmicas de disputas territoriais, alianças e cisões;
* Relações entre grupos e territórios ao longo do tempo;
* Operações e intervenções estatais de repercussão histórica;
* Contexto político, social, econômico e penitenciário;
* **Biblioteca de fontes primárias e secundárias que sustentam cada informação.**

> **⚠️ AVISO ÉTICO E LIMITAÇÃO DE ESCOPO:**  
> Este projeto possui finalidade **exclusivamente acadêmica, historiográfica e de pesquisa sociológica**.  
> **NÃO** é uma ferramenta de inteligência operacional policial, **NÃO** realiza predições, **NÃO** indica alvos e **NÃO** auxilia qualquer atividade ilícita.

---

## 🧭 2. Princípios Metodológicos Fundamentais

1. **Rastreabilidade e Proveniência Estrita de Fontes**:  
   Nenhum fato, data ou vinculação territorial é inserido no banco sem vínculo a uma fonte documentada com citação literal, página e referência arquivística.
2. **Tratamento de Narrativas Conflitantes**:  
   Quando fontes confiáveis divergirem, ambas as versões são preservadas com suas respectivas referências e classificadas como `conflitante` / `disputed`.
3. **REGRA 1 — ZERO vs. DESCONHECIDO (NULL)**:  
   O valor matemático `0` denota contagem confirmada como zero. Dados ausentes, desconhecidos ou não informados são estritamente armazenados como `NULL` / `None`.
4. **Preservação de Grafias Originais**:  
   Toda entidade textual preserva a forma original (`original_name`) e a forma normalizada para buscas (`normalized_name`).

---

## 🏗️ 3. Estrutura Profissional de Diretórios

```text
rio-criminalidade-historica/
│
├── README.md                       # Documentação geral do projeto
├── cronograma_projeto.md           # Cronograma detalhado por fases e tarefas
├── CONTRIBUTING.md                 # Diretrizes éticas e de pesquisa
├── .gitignore                      # Regras de exclusão do controle de versão
├── .env.example                    # Modelo de variáveis de ambiente
├── requirements.txt                # Dependências Python gerenciadas
├── pyproject.toml                  # Configuração de build e testes
│
├── config/
│   └── settings.py                 # Configurações centralizadas (Pydantic / os.getenv)
│
├── data/                           # Armazenamento estruturado de dados
│   ├── raw/                        # Documentos brutos (jornalismo, academia, governo, etc.)
│   ├── staging/                    # Dados intermediários de extração
│   ├── processed/                  # Dados limpos e prontos para inserção
│   ├── geospatial/                 # Malhas cartográficas (IBGE, IPP, GeoJSON)
│   └── exports/                    # Relatórios e exportações de pesquisa
│
├── docs/                           # Documentação técnica e científica
│   ├── metodologia/                # Protocolos de pesquisa, fontes, cartografia, normalização
│   ├── fontes/                     # Catálogo e critérios de fontes
│   ├── pesquisa/                   # Guias e recortes históricos
│   └── arquitetura/                # ERD e arquitetura relacional
│
├── research/                       # Planejamento de pesquisa empírica
│   ├── questions/                  # Banco de queries e perguntas de pesquisa
│   ├── timelines/                  # Recortes por décadas
│   ├── entities/                   # Caderno de entidades
│   ├── regions/                    # Caderno de territórios
│   └── source_reviews/             # Fichamento crítico de fontes
│
├── scripts/                        # Scripts executáveis de automação
│   ├── ingestion/                  # Download e registro de fontes (hash SHA-256)
│   ├── extraction/                 # Extratores de texto (PDF, HTML, TXT)
│   ├── cleaning/                   # Utilitários de normalização
│   ├── normalization/              # Regras de transformação
│   ├── geospatial/                 # Processamento de geometrias
│   └── validation/                 # Verificação de banco e integridade
│
├── database/                       # Infraestrutura do banco de dados
│   ├── migrations/                 # Migrações Alembic
│   ├── schema/                     # DDL SQL (PostgreSQL/PostGIS) e modelos ORM
│   ├── seeds/                      # Cargas de referência
│   └── queries/                    # Consultas SQL analíticas
│
├── src/                            # Biblioteca de código-fonte reutilizável
│   ├── ingestion/                  # Módulos de coleta e custódia
│   ├── extraction/                 # Parsers polimórficos
│   ├── processing/                 # Processamento e pipelines
│   ├── normalization/              # Implementação de regras de normalização
│   ├── entities/                   # Modelos de domínio
│   ├── geospatial/                 # Utilitários geográficos e espaciais
│   ├── database/                   # Conexão, sessões e engine SQLAlchemy
│   └── utils/                      # Unicode, hashes e funções auxiliares
│
├── tests/                          # Testes automatizados (pytest)
│
└── app/                            # Interface visual do usuário
    ├── components/                 # Componentes reutilizáveis de UI
    ├── pages/                      # Páginas da aplicação Streamlit
    └── map/                        # Renderizadores de mapas (Folium)
```

---

## 🚀 4. Instalação e Execução

### 1. Criar e Ativar o Ambiente Virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```powershell
cp .env.example .env
```

### 4. Verificar Conexão com o Banco de Dados

```powershell
python -m scripts.validation.check_db
```

### 5. Demonstrar as Regras de Normalização

```powershell
python -m scripts.cleaning.normalize_text
```

### 6. Executar os Testes Automatizados

```powershell
pytest -v
```

---

## 📚 5. Documentação Metodológica

Consulte os guias detalhados em `docs/metodologia/`:
* [Metodologia de Pesquisa](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/metodologia/metodologia_pesquisa.md)
* [Metodologia de Fontes e Tipologia](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/metodologia/metodologia_fontes.md)
* [Metodologia de Confiabilidade e Validação](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/metodologia/metodologia_confiabilidade.md)
* [Metodologia de Normalização e Regra do Zero](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/metodologia/metodologia_normalizacao.md)
* [Metodologia Geográfica e Territórios no Tempo](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/metodologia/metodologia_geografica.md)
* [Proposta de ERD Relacional](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/arquitetura/erd_proposta.md)
* [Cronograma Detalhado do Projeto](file:///C:/Users/dani/Documents/Daniel%20Systems/cronograma_projeto.md)
