# 05. Política e Modelagem Temporal de Fatos Históricos

---

## 1. Princípio da Não-Invenção de Precisão Temporal

Documentos históricos registram tempos com graus muito variados de resolução:
* Dias exatos (ex: `"15 de março de 1983"`);
* Apenas meses (ex: `"maio de 1978"`);
* Apenas anos (ex: `"1975"`);
* Períodos aproximados ou intervalos (ex: `"c. 1976"`, `"final da década de 1970"`);
* Datas desconhecidas (ex: `"s/d"`).

> **Regra Temporal Fundamental**: O sistema **NUNCA** inventa dias ou meses inexistentes na fonte. Não se converte arbitrariamente `"1970"` em `"1970-01-01"` para preencher campos.

---

## 2. Estrutura Temporal no Banco de Dados

* `date_display` (VARCHAR, NOT NULL): Registra a expressão temporal **exatamente como informada pela fonte**.
* `date_start` (VARCHAR, NULLABLE): Data normalizada de referência inicial (formato ISO YYYY-MM-DD se dia conhecido, YYYY-MM se mês conhecido, ou YYYY se apenas ano conhecido).
* `date_end` (VARCHAR, NULLABLE): Data de término caso o evento se configure como intervalo temporal contínuo.
* `year` (INTEGER, NULLABLE): Ano numérico principal utilizado para ordenar e filtrar na linha do tempo.
* `temporal_precision` (VARCHAR): Classifica o grau de resolução:
  * `"dia"`: Dia, mês e ano documentados.
  * `"mes"`: Mês e ano documentados.
  * `"ano"`: Apenas ano documentado.
  * `"intervalo"`: Período entre dois marcos.
  * `"aproximado"`: Estimativa contextual (ex: "cerca de 1980").
  * `"desconhecido"`: Sem marco temporal comprovado.
* `exact_date` (BOOLEAN): `True` exclusivamente quando dia, mês e ano forem atestados documentalmente.
