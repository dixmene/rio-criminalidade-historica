# 04. Metodologia de Confiabilidade e Gestão de Narrativas Conflitantes

---

## 1. Classificação das Afirmações Históricas

O status de validação é atribuído a cada asserção factual individualmente:

* 🟢 **Confirmado (`confirmado`)**: Fato atestado por duas ou mais fontes independentes de alta relevância (ex: tese acadêmica + documento oficial + acervo hemerográfico), ou por relatório com ampla instrução probatória.
* 🔵 **Provável (`provavel`)**: Fato atestado por fonte qualificada consistente com o contexto geral, porém sem confirmação cruzada independente adicional.
* 🔴 **Conflitante (`conflitante`)**: Fontes idôneas apresentam versões divergentes quanto a autoria, circunstâncias, datas ou dinâmicas.
* ⚪ **Não Verificado (`nao_verificado`)**: Informe anônimo, boato de imprensa ou rumor não confirmado por investigações posteriores.

---

## 2. Tratamento Obrigatório de Versões Divergentes

Quando fontes divergirem:
* O sistema **NUNCA** escolhe arbitrariamente uma versão em detrimento da outra;
* Cada versão é registrada como um vínculo de `EventSource` com status `conflitante`;
* O campo `confidence_notes` documenta explicitamente os pontos de atrito entre as narrativas;
* A interface gráfica exibe visualmente o marcador de conflito (badge vermelho) alertando o pesquisador para a discordância documental.
