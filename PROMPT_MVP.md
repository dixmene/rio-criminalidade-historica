# PROMPT MVP — Daniel Systems
## Sistema de Pesquisa Histórica, Territorialidade e Proveniência de Fontes

---

### 📌 Regra Fundamental de Arquitetura

> **O projeto deverá ser desenvolvido em duas camadas: MVP e arquitetura de produção. Não construir a arquitetura completa inicialmente. Primeiro implementar um MVP funcional e pequeno, capaz de validar o modelo de dados, metodologia de pesquisa, proveniência das fontes, temporalidade, geografia e visualização. Somente após o MVP ser validado deverá ser projetada a arquitetura completa.**

> **O agente não deverá inventar dados para preencher o MVP. Caso ainda não existam dados coletados, deverá preparar o ambiente e criar dados fictícios claramente identificados como `[DEMO]`, apenas para testar tecnicamente o mapa e os relacionamentos. Dados fictícios nunca poderão ser confundidos com dados históricos reais.**

---

### 🎯 Escopo do MVP

O MVP responde à pergunta central:
> **"Consigo selecionar um período, visualizar eventos e relações territoriais documentadas e abrir as fontes que sustentam essas informações?"**

#### O MVP contempla:
1. **1 recorte histórico piloto** (ex: 1970–1989);
2. **Entidades centrais**: Fontes (`sources`), Eventos (`events`), Organizações (`organizations`), Pessoas (`people`), Regiões (`regions`);
3. **Proveniência estrita**: Nenhuma informação/evento entra no sistema sem vínculo a pelo menos uma fonte documentada com citação/trecho;
4. **Níveis de validação**: Confirmado, Provável, Conflitante, Não Verificado;
5. **Interface interativa (Streamlit + Folium)**:
   - Linha do tempo (filtro por ano/intervalo);
   - Mapa geográfico interativo do Rio de Janeiro;
   - Painel detalhado do evento com organizações, pessoas, contexto e fontes comprobatórias;
   - Consulta cruzada por território (eventos por região).

---

### 🗄️ Modelo de Dados Mínimo

```text
sources (fontes)
   │
   ├──────────────┐
   ↓              ↓
events         people (pessoas)
   │
   ↓
organizations (organizações)
   │
   ↓
regions (territórios/regiões)
```

**Tabelas de Relacionamento & Proveniência:**
* `event_sources`: vincula evento à fonte com trecho/página e status de validação (`confirmado`, `provavel`, `conflitante`, `nao_verificado`).
* `event_organizations`: vincula evento a organizações e seus papéis.
* `event_people`: vincula evento a pessoas e seus papéis.
* `event_regions`: vincula evento a territórios geográficos.

---

### 🔄 Ciclo da Informação
```text
fonte → registro da fonte → extração/manual → normalização → validação → banco → linha do tempo → mapa → referência
```

---

### 🚫 O que NÃO entra no MVP
* Scraping massivo de milhares de páginas
* NLP avançado / Extração automática com LLMs em tempo real
* Reconhecimento automático de entidades
* OCR em massa
* Predição / Machine Learning
* Arquitetura de microserviços ou cloud complexa
* Autenticação e permissões multi-inquilino
