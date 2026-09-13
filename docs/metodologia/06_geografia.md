# 06. Metodologia Geográfica e Gestão de Incerteza Espacial

---

## 1. Princípio da Não-Invenção de Coordenadas

Muitos acontecimentos históricos ocorrem em territórios cujos limites precisos não foram georreferenciados na época (ex: litígios fundiários, fronteiras comunitárias imprecisas, áreas rurais antigas).

> **Regra Geográfica Fundamental**: Se a fonte não fornecer coordenadas ou limites cartográficos delimitados, os campos `latitude` e `longitude` devem ser estritamente mantidos como `NULL`. Nenhuma coordenada genérica de centroide pode ser inventada sem documentação.

---

## 2. Estrutura do Modelo `Region`

* `original_name`: Topônimo original na fonte (ex: `"Complexo da Maré"`).
* `normalized_name`: Nome normalizado em maiúsculas sem acentos (`"COMPLEXO DA MARE"`).
* `region_type`: Categoria (`bairro`, `favela`, `complexo`, `municipio`, `zona`, `territorio_historico`).
* `municipality`: Município de localização (NULL se desconhecido).
* `latitude` e `longitude`: Float **NULLABLE**.
* `location_precision`:
  * `"exata"`: Ponto ou marco geodésico comprovado.
  * `"centroide"`: Ponto médio de polígono oficial (IBGE / IPP).
  * `"aproximada"`: Estimativa baseada em referências históricas.
  * `"desconhecida"`: Território sem coordenadas atribuíveis.
* `geometry_source`: Origem cartográfica da geometria (ex: `"IBGE/2022"`, `"Data.Rio/IPP"`, `"Pesquisa Documental"`).
* `geometry_confidence`: Nível de certeza (`"alta"`, `"media"`, `"baixa"`).

---

## 3. Comportamento do Mapa (Folium)

* Eventos associados a regiões com coordenadas válidas são plotados interativamente com marcadores coloridos conforme o status de validação.
* Eventos associados a territórios sem coordenadas documentadas (`latitude is None`) **NÃO** são omitidos: são apresentados na linha do tempo e listados em um painel destacado de *"Eventos em Territórios Sem Delimitação Cartográfica Exata"*, garantindo visibilidade sem contaminação cartográfica.
