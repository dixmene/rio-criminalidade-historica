# 02. Normalização de Dados e REGRA 1 (ZERO vs. NULL)

---

## 1. REGRA 1 — ZERO vs. DESCONHECIDO (NULL)

> **Regra Absoluta do Projeto**: O valor matemático `0` nunca deve ser utilizado para representar ausência de informação, campo desconhecido ou dado não coletado.

### Mapeamento Obrigatório:
* `NULL` / `None` / Vazio: Representa **dado desconhecido, não informado pela fonte ou não verificado**.
* `0` (Zero Numérico): Representa **quantidade comprovada e expressamente informada como zero** na fonte (ex: "zero apreensões registradas na data X", "0 baixas civis documentadas no laudo Y").

### Implementação no Código (`src/normalization/rules.py`):
```python
def normalize_nulls(value: Any) -> Optional[Any]:
    # 0 ou '0' são estritamente preservados como 0
    # '', None, 'N/A', 'desconhecido', 'não informado' viram None (NULL)
```
Nenhum pipeline ou função de transformação pode converter `None → 0`, `NaN → 0` ou `"" → 0`.

---

## 2. Normalização de Nomes e Entidades

Para viabilizar consultas cruzadas sem perda de autenticidade histórica:
* `original_name`: Grafia literal com acentuação e maiúsculas/minúsculas da fonte.
* `normalized_name`: Convertido via decomposição canônica Unicode (NFD), sem acentos, com remoção de espaços múltiplos e em letras maiúsculas.

Exemplos:
* `"João da Silva"` $\rightarrow$ `original_name: "João da Silva"`, `normalized_name: "JOAO DA SILVA"`
* `"São Gonçalo"` $\rightarrow$ `original_name: "São Gonçalo"`, `normalized_name: "SAO GONCALO"`
* `"Praça Seca - Jacarepaguá"` $\rightarrow$ `normalized_name: "PRACA SECA - JACAREPAGUA"`
