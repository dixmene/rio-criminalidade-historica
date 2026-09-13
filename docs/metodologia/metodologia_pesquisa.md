# Metodologia de Pesquisa Histórica e Documental

---

## 1. Visão Geral e Princípios Epistemológicos

Este projeto estabelece um protocolo metodológico rigoroso e reproduzível para o estudo antropológico e histórico da criminalidade organizada no estado do Rio de Janeiro.

O princípio fundante é a **rastreabilidade integral de toda informação**. O sistema opera como um acervo científico-digital onde:
* Não existem fatos "sabidos" sem documento de sustentação;
* Não há atribuição de autoria ou liderança sem citação explícita de fonte primária ou secundária qualificada;
* Conflitos de narrativas não são apagados nem arbitrados arbitrariamente; são explicitamente modelados e contrastados.

---

## 2. Hierarquia da Pesquisa

A investigação organiza-se em camadas conceituais decrescentes de abstração:

```text
PERÍODO HISTÓRICO (Macrocontexto)
       │
       ▼
CONTEXTO SOCIAL / POLÍTICO / PENITENCIÁRIO
       │
       ▼
ORGANIZAÇÕES / GRUPOS / FACÇÕES / MILÍCIAS
       │
       ▼
LIDERANÇAS E ATORES DOCUMENTADOS
       │
       ▼
EVENTOS HISTÓRICOS ESPECÍFICOS
       │
       ▼
DINÂMICAS TERRITORIAIS (Presença, Disputa, Controle)
       │
       ▼
ACERVO DE FONTES COMPROBATÓRIAS (Páginas, Citações e Laudos)
```

---

## 3. Pipeline Metodológico de Extração e Ingestão

Para garantir reproduzibilidade e integridade, o pipeline de pesquisa segue as seguintes etapas:

1. **Busca Estruturada**: Registro da consulta (`query_id`, termos, motor/acervo, data);
2. **Coleta e Custódia do Documento**: Download do documento original em `data/raw/` com cálculo de hash SHA-256 para auditoria;
3. **Extração de Texto e Metadados**: Leitura estruturada de PDFs, relatórios, transcrições e jornais;
4. **Identificação e Extração de Entidades (NER & Análise Qualitativa)**: Mapeamento de pessoas, grupos, datas, locais e eventos;
5. **Normalização e Desambiguação**: Aplicação de regras estritas de normalização preservando os nomes originais;
6. **Classificação da Evidência e Confiabilidade**: Atribuição do grau de certeza (`confirmado`, `provavel`, `conflitante`, `nao_verificado`);
7. **Validação Humana e Curadoria**: Revisão e aprovação por pares ou pesquisadores;
8. **Persistência no Banco Relacional**: Inserção com integridade referencial e proveniência obrigatória.

---

## 4. Estratégia de Pesquisa por Décadas e Marcos Históricos

A investigação é dividida em períodos cronológicos:

* **Etapa 1 — Antecedentes Históricos**: Jogo do bicho, redes clientelistas e dinâmicas pré-década de 1970;
* **Etapa 2 — Década de 1970**: Ocupação prisional na Ilha Grande, Lei de Segurança Nacional, surgimento das primeiras redes articuladas no sistema prisional;
* **Etapa 3 — Década de 1980**: Expansão do comércio de entorpecentes no atacado, armamento, primeiras disputas territoriais e transição política;
* **Etapa 4 — Década de 1990**: Consolidação de facções rivais (CV, TC, ADA), grandes rebeliões, chacinas e primeiras intervenções estaduais/federais;
* **Etapa 5 — Década de 2000**: Surgimento estruturado das milícias na Zona Oeste e Baixada, instalação das UPPs, cisões e disputas territoriais;
* **Etapa 6 — Década de 2010**: Crise do modelo UPP, expansão paramilitar, novas alianças interestaduais (ex: TCP, PCC);
* **Etapa 7 — Década de 2020 e Atual**: Cenário contemporâneo de complexas coalizões, narcomilícias e reconfigurações territoriais contínuas.
