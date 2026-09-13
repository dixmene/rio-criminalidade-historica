# Metodologia de Confiabilidade e Validação Histórica

---

## 1. Níveis de Evidência e Classificação

Cada afirmação factual ou vínculo no banco de dados deve ser classificado em uma das seguintes categorias:

```text
                                 STATUS DA AFIRMAÇÃO
                                          │
       ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
       ▼                  ▼                               ▼                  ▼
  CONFIRMADO           PROVÁVEL                      CONFLITANTE       NÃO VERIFICADO
 (Múltiplas fontes   (Fonte sólida,                 (Fontes fiáveis     (Apenas informe
  independentes)      contexto coerente)             divergem)           ou rumor)
```

### 🟢 Confirmado (`confirmed`)
* **Critério**: O fato ou relação territorial é atestado por duas ou mais fontes independentes de alta confiabilidade (ex: tese acadêmica + documento oficial + cobertura hemeroteca), ou por decisão judicial/relatório de comissão oficial com ampla documentação probatória.

### 🔵 Provável (`probable`)
* **Critério**: O fato provém de uma fonte qualificada de alta relevância (ex: livro de referência historiográfica ou matéria investigativa detalhada), sendo coerente com o contexto histórico geral, porém sem confirmação cruzada independente adicional.

### 🔴 Conflitante / Disputado (`disputed`)
* **Critério**: Fontes qualificadas apresentam versões divergentes sobre datas, autoria, dinâmica do conflito ou alianças.
* **Ação Obrigatória do Sistema**: Registrar ambas as versões de forma explícita com suas respectivas fontes e expor a divergência nas notas críticas.

### ⚪ Não Verificado (`unverified`)
* **Critério**: Informação que consta apenas em informe anônimo, boato de época ou relato secundário sem detalhamento empírico.

---

## 2. Tratamento de Narrativas Conflitantes

Quando duas fontes divergirem, o modelo relacional associa múltiplos registros em `event_sources` com o status `disputed` / `conflitante`.

Exemplo:
* **Fonte 1 (Jornal de Época)**: Atribui a explosão de artefato em 1981 a grupo guerrilheiro externo (`status: conflitante`).
* **Fonte 2 (Laudo Pericial Posterior / Comissão da Verdade)**: Atribui a explosão a militares do DOI-CODI dentro do veículo (`status: confirmado / contestação histórica`).

O sistema preserva a evolução do entendimento histórico, demonstrando como versões oficiais iniciais foram superadas ou contestadas por investigações posteriores.
