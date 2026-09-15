# Limitações Metodológicas e Epistemológicas do Atlas

> **Aviso ao Pesquisador:**  
> Nenhum mapa é o território. Todo mapa é uma representação seletiva, situada e historicamente contingente.  
> Este documento cataloga com absoluta transparência científica as limitações materiais, arquivísticas e cartográficas desta infraestrutura de pesquisa.

---

## 1. Assimetria e Viés de Registro nas Fontes Históricas

1. **Predomínio de Relatórios Oficiais e Inquéritos Policiais:**  
   Documentos produzidos pelo Estado (Polícia Civil, Polícia Militar, DOPS, DESIPE, Judiciário) refletem a perspectiva institucional e a linguagem burocrática dos aparatos de repressão. Fatos ocorridos em favelas ou celas prisionais sem testemunho oficial tendem a ser sub-registrados ou distorcidos nos boletins originais.
2. **Dependência de Hemeroteca e Noticiário Policial:**  
   Para as décadas de 1960 a 1980, grande parte das evidências primárias provém de periódicos de grande circulação (*Jornal do Brasil*, *O Globo*, *Última Hora*, *A Luta Democrática*). A cobertura de tais veículos era condicionada pela censura da Ditadura Militar (1964-1985), pelo sensacionalismo das editorias policiais e pela reprodução acrítica de versões policiais oficiais.
3. **Lacuna da História Oral e Vozes Comunitárias:**  
   Embora o acervo integre obras sociológicas fundamentais (como Alba Zaluar, Michel Misse e Carlos Amorim), relatos orais diretos de moradores sobre o cotidiano da convivência armada ainda constituem fração minoritária das fontes catalogadas.

---

## 2. Incerteza Espacial e Anacronismo das Malhas

1. **Malhas Vetoriais Contemporâneas:**  
   Os polígonos de favelas (dadosderiscos, 2024) e bairros (IPP, 2022) refletem o tecido urbano e as divisões administrativas do século XXI. Ao projetar tais geometrias sobre eventos de 1970 ou 1985, as fronteiras devem ser lidas exclusivamente como **referências ilustrativas de localização aproximada**, e nunca como perímetros históricos fidedignos da época.
2. **Imprecisão de Centroides:**  
   Acontecimentos referenciados na fonte apenas como ocorridos "em Bangu", "no Morro do Alemão" ou "na Baixada Fluminense" são georreferenciados no centroide aproximado da localidade. A incerteza é explicitada no atributo `location_precision` (`centroide` ou `referencial`).
3. **Regiões Estritamente sem Coordenadas (NULL ≠ 0):**  
   Territórios históricos dispersos ou conceituais (como os *Subúrbios Ferroviários da AP3* ou a *Rede Penitenciária da Guanabara*) mantêm coordenadas estritamente `NULL` e não são renderizados no mapa até que perímetros arquivísticos documentados sejam consolidados.

---

## 3. Dinâmica Temporal e Granularidade

1. **Acontecimentos de Longa Duração vs. Eventos Pontuais:**  
   Processos socioterritoriais como a hegemonia de facções ou expansão miliciana ocorrem ao longo de meses ou anos. A datação inicial (`date_start`) e final (`date_end`) reflete marcos documentados na literatura, mas não encerra a complexidade da transição cotidiana de poder armado.
2. **Embargo Ético dos Últimos 24 Meses:**  
   Para eventos ocorridos nos últimos 24 meses, a resolução espacial é propositalmente degradada para o nível de município ou AISP para salvaguarda de vidas humanas e prevenção contra uso operacional.

---

## 4. Recomendações para Uso Científico

- Ao citar dados ou mapas deste projeto em artigos, dissertações ou teses, o pesquisador deve **consultar os trechos literais das fontes vinculadas** através da Ficha Epistemológica e citar a fonte documental primária original.
- Análises espaciais quantitativas devem levar em conta o índice de densidade documental (`CoverageService`) para não confundir **ausência de evidência documentada** com **ausência de criminalidade real**.
