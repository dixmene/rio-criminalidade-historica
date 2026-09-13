# 03. Metodologia de Proveniência Estrita de Fontes

---

## 1. Princípio de Validação de Domínio

No modelo do projeto:
> **Um evento histórico real sem fonte comprobatória NÃO é um registro histórico válido.**

Essa restrição é aplicada em duas camadas do código:
1. **Schema Pydantic (`EventCreate`)**: A validação `model_validator` rejeita qualquer payload onde `is_demo=False` e `len(sources) == 0`.
2. **Camada de Serviço (`IngestionService.create_event`)**: Lança exceção de domínio (`ValueError`) caso haja tentativa de inserção de evento real desprovido de fontes vinculadas.

---

## 2. Estrutura do Vínculo de Proveniência (`EventSource`)

Cada relacionamento entre Evento e Fonte armazena:
* `source_id`: Identificador da fonte cadastrada.
* `page_or_section`: Localização específica no texto (ex: `p. 45-47`, `Folha 12v`, `Capítulo 2`).
* `excerpt`: Citação textual literal da fonte que comprova o fato (mínimo de 5 caracteres, obrigatório).
* `claim_assertion`: Síntese da afirmação factual sustentada pelo trecho.
* `validation_status`: Classificação da afirmação (`confirmado`, `provavel`, `conflitante`, `nao_verificado`).
* `confidence_notes`: Observações críticas sobre divergências com outras fontes ou ressalvas arquivísticas.
