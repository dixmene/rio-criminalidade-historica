# Metodologia e Regras de Normalização de Dados

---

## 1. REGRA 1 — ZERO vs. DESCONHECIDO (NULL)

Esta é uma regra absoluta do projeto:

> **O valor matemático `0` NUNCA deve ser utilizado para representar ausência de informação, campo desconhecido ou dado não coletado.**

### Princípios da Regra:
* `NULL` / `None` / `Vazio`: Representa **dado desconhecido, não informado pela fonte ou não verificado**.
* `0` (Zero Numérico): Representa **quantidade comprovada e expressamente informada como zero** (ex: "zero apreensões registradas na data X", "0 baixas civis documentadas no laudo Y").

### Tabela de Decisão para Pipelines:

| Informação na Fonte | Representação no Banco | Justificativa |
|---|---|---|
| A fonte diz expressamente "zero prisões" | `0` (inteiro) | Fato afirmativo de contagem nula. |
| A fonte não menciona o número de prisões | `NULL` | Ausência de dado na fonte. |
| O campo não foi coletado ou não se aplica | `NULL` | Desconhecido. |
| A fonte diz "nenhum dado disponível" | `NULL` | Desconhecido. |

---

## 2. Preservação do Valor Original vs. Valor Normalizado

Para evitar perda de especificidade histórica (grafias de época, topônimos antigos, apelidos), todas as entidades de texto possuem duplo armazenamento:

```text
display_name / original_name  → Mantém a grafia original com acentuação e caixa mista
normalized_name               → Letras maiúsculas, sem acentos, sem caracteres especiais
```

### Exemplos:
* **Pessoa**:
  * `original_name`: `"Sebastião Mendes"`
  * `normalized_name`: `"SEBASTIAO MENDES"`
* **Município / Bairro**:
  * `original_name`: `"São Gonçalo"`
  * `normalized_name`: `"SAO GONCALO"`
* **Organização**:
  * `original_name`: `"Comando Vermelho Rogério Lemgruber"`
  * `normalized_name`: `"COMANDO VERMELHO ROGERIO LEMGRUBER"`

---

## 3. Normalização de Datas Históricas

Datas históricas podem apresentar graus variados de precisão temporal:

| Formato na Fonte | `date_start` | `year` | `date_precision` |
|---|---|---|---|
| "15 de março de 1983" | `"1983-03-15"` | `1983` | `"dia"` |
| "Maio de 1978" | `"1978-05-01"` | `1978` | `"mes"` |
| "Ano de 1975" | `"1975-01-01"` | `1975` | `"ano"` |
| "Início da década de 1980" | `"1980-01-01"` | `1980` | `"aproximado"` |
