# Metodologia Geográfica e Modelagem Territorial Temporal

---

## 1. Princípios da Cartografia Histórica

O território não é estático. Uma das premissas fundamentais deste projeto é que **o controle ou influência de uma organização sobre um espaço é uma relação temporalmente delimitada e documentalmente fundamentada**.

> **Nenhuma geometria ou relação espacial é permanente ou presumida sem fonte.**

---

## 2. Taxonomia de Relações Territoriais (`relation_type`)

Ao mapear a presença de um grupo em uma região ao longo do tempo, o vínculo deve ser tipificado:

| Tipo de Relação | Descrição | Requisito Probatório |
|---|---|---|
| `presenca_documentada` | Menção documental de integrantes ou atividades no local sem evidência de controle exclusivo. | Noticiário de época ou inquérito citando ocorrências no local. |
| `influencia_comercial` | Controle de pontos de venda ou taxas em área com atuação partilhada ou tolerada. | Relatório de segurança ou pesquisa acadêmica. |
| `dominio_hegemonico` | Controle territorial ostensivo com imposição de regras e expulsão de rivais. | Sentença, relatório oficial (ex: CPI) ou estudos sociológicos. |
| `disputa_ativa` | Conflito bélico contínuo pelo território entre dois ou mais grupos. | Registros contínuos de confrontos na área. |
| `mudanca_de_controle` | Transição de hegemonia de um grupo para outro em data identificável. | Marco histórico de invasão, tomada ou operação. |
| `ocupacao_estatal` | Presença de forças de segurança pública com instalação de postos (ex: UPPs). | Decreto governamental ou diário oficial. |

---

## 3. Modelo de Território no Tempo

Cada relação territorial é modelada como um intervalo no tempo:

```text
REGIÃO (Território)
       │
       ▼
ORGANIZAÇÃO (Grupo / Facção / Milícia)
       │
       ├── data_inicio (YYYY-MM-DD ou YYYY)
       ├── data_fim (YYYY-MM-DD ou YYYY ou NULL se persistente)
       ├── tipo_relacao (dominio_hegemonico, disputa, presenca)
       ├── fontes_comprobatorias (IDs das fontes)
       └── nivel_confianca (confirmado, provavel, conflitante)
```

---

## 4. Gestão de Incerteza Geoespacial

Quando uma localidade não puder ser delimitada por um polígono exato de época:
* Utiliza-se um ponto de referência central (centróide aproximado);
* Registra-se `precision_level: "aproximado"` / `"bairro"` / `"municipio"`;
* Documenta-se a fonte cartográfica de origem (ex: IBGE, IPP/Data.Rio).
