# Daniel Systems — MVP de Pesquisa Histórica e Territorialidade

Sistema de Mapeamento Histórico, Territorialidade e Proveniência de Fontes focado no Rio de Janeiro.

> **Regra Fundamental de Arquitetura**: 
> 1. Desenvolvido no modelo em duas camadas (**MVP primeiro, produção depois**).
> 2. **Proveniência Estrita**: Nenhuma informação/evento entra no sistema sem vínculo a pelo menos uma fonte documentada com citação/trecho comprobatório.
> 3. **Isolamento de Dados**: Dados de teste técnicos são identificados com `[DEMO]` e nunca misturados com pesquisa documental real.

---

## 🏗️ Estrutura do Projeto

```text
Daniel Systems/
├── PROMPT_MVP.md                   # Especificação e regras fundamentais do MVP
├── README.md                       # Documentação e instruções de execução
├── requirements.txt                # Dependências do projeto
├── .env.example                    # Modelo de configuração de ambiente
├── daniel_systems.db               # Banco de dados local SQLite (ou PostgreSQL via .env)
├── app/
│   ├── config.py                   # Configurações gerais
│   ├── database.py                 # Conexão SQLAlchemy e sessão do banco
│   ├── models/                     # Modelos relacionais (Fontes, Eventos, Regiões, etc.)
│   │   ├── source.py               # Tabela sources
│   │   ├── event.py                # Tabela events
│   │   ├── region.py               # Tabela regions (coordenadas geográficas)
│   │   ├── organization.py         # Tabela organizations
│   │   ├── person.py               # Tabela people
│   │   └── associations.py         # Tabelas intermediárias e proveniência (event_sources, etc.)
│   ├── schemas/                    # Schemas de validação Pydantic com proveniência estrita
│   ├── services/                   # Lógica de negócio (EventService, IngestionService)
│   ├── scripts/                    # Scripts de inicialização e dados DEMO
│   │   ├── init_db.py              # Criação das tabelas
│   │   └── seed_demo.py            # Carga de dados de teste [DEMO]
│   └── ui/
│       └── app.py                  # Interface gráfica Streamlit + Folium (Mapa & Linha do Tempo)
└── tests/                          # Testes automatizados (pytest)
    ├── test_models.py              # Testes de modelos e integridade relacional
    ├── test_provenance.py          # Testes de exigência obrigatória de fontes
    └── test_services.py            # Testes de filtros temporais e espaciais
```

---

## 🚀 Como Executar

### 1. Ativar o Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Inicializar o Banco e Popular Dados de Teste DEMO

```powershell
python -m app.scripts.init_db
python -m app.scripts.seed_demo
```

### 3. Rodar a Interface Interativa (Streamlit + Mapa Folium)

```powershell
streamlit run app/ui/app.py
```

### 4. Executar os Testes Automatizados

```powershell
pytest -v
```
