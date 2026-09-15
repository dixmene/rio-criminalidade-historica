# 09. Ética da Cartografia Histórica e Limites Epistemológicos do Mapa

> **Princípio Fundamental:**  
> A cartografia histórica digital sobre violência, instituições e criminalidade no Rio de Janeiro é um instrumento de **compreensão retrospectiva, memória coletiva, transparência científica e salvaguarda democrática**.  
> Em hipótese alguma o projeto pode funcionar como ferramenta de inteligência tático-operacional, monitoramento em tempo real ou estigmatização territorial de populações vulneráveis.

---

## 1. O Embargo Temporal de Granularidade (24 Meses)

A pesquisa histórica distingue estritamente o **fato histórico consolidado** do **acontecimento policial em curso**. Acontecimentos recentes envolvem investigações em andamento, riscos iminentes à vida de moradores, testemunhas e agentes públicos.

Por este motivo, o sistema implementa uma guarda programática bloqueante (`EthicsGuard`):

1. **Janela de Embargo:**  
   Todo e qualquer evento compreendido na janela dos **últimos 24 meses** (a contar da data civil corrente) tem sua resolução espacial restrita.
2. **Supressão de Coordenadas Exatas:**  
   Coordenadas de latitude/longitude a nível de rua, quarteirão ou logradouro são **obrigatoriamente suprimidas**.
3. **Agregação Obrigatória:**  
   Os pontos são agregados e centralizados no centroide da respectiva **AISP (Área Integrada de Segurança Pública)** ou no centroide do **Município**, acompanhados da sinalização:
   > *"Dado recente protegido por embargo ético de 24 meses: localização agregada para salvaguarda de pessoas vivas."*

---

## 2. Proibição Estrita de Inteligência Tático-Operacional

O acervo não registra, não armazena e rejeita em pipeline automatizado:

- Menções a pontos ativos de venda de entorpecentes ("bocas de fumo");
- Rotas de fuga vigentes ou locais de esconderijo de materiais bélicos;
- Endereços residenciais particulares de pessoas vivas, familiares de lideranças ou agentes de segurança;
- Informações oriundas de grampos ilegais ou fontes sem custódia arquivística oficial e verificada.

Textos submetidos que contenham termos característicos de inteligência operacional são imediatamente higienizados pelo `EthicsGuard`, registrando a redução por diretriz ética na ficha epistemológica.

---

## 3. A Regra do Anacronismo e a Honestidade Cartográfica (NULL ≠ 0)

Um dos erros mais graves da cartografia contemporânea sobre o Rio de Janeiro é projetar delimitações atuais de comunidades sobre o século XX, como se as fronteiras de 2024 existissem em 1970.

O projeto adota regras cartográficas rigorosas:

1. **Sinalização Visual de Anacronismo:**  
   Toda malha de bairros de 2022 (IPP) ou polígono de comunidades de 2024 (dadosderiscos) exibida em anos anteriores recebe padrão visual **hachurado cinza diagonal** e aviso explícito:
   > *"Malha de 2022/2024 aplicada a período pretérito — fronteira ilustrativa, não histórica."*
2. **Recusa a Coordenadas Fictícias (NULL ≠ 0):**  
   Se uma região histórica (como os *Subúrbios Ferroviários da Zona Norte / AP3* ou a *Rede Penitenciária da Guanabara*) não possui delimitação vetorial oficial ou coordenada pontual verificável, seus campos de geometria permanecem **estritamente NULL**.
   Não são plotadas no meio da Baía de Guanabara nem no marco zero (0, 0).

---

## 4. Semântica Estrita de Domínio Territorial

A linguagem cartográfica molda a percepção pública. Para evitar inferências indevidas, o sistema proíbe a presunção automática de controle:

| Relação Territorial | Definição Epistemológica | Requisito de Evidência |
| :--- | :--- | :--- |
| **Controle** | Hegemonia armada exercida sobre o território, impedindo atuação ostensiva de rivais e do Estado. | Documentação primária oficial, inquéritos ou sentenças transitadas. |
| **Presença** | Atuação episódica, circulação ou comércio armado sem garantia de soberania territorial exclusiva. | Reportagens hemerográficas ou registros policiais locais. |
| **Influência** | Extensão de autoridade política, fiscal ou extorsiva sem barricadas físicas contínuas. | Investigações do Ministério Público / GAECO. |
| **Disputa** | Conflito armado aberto ou incursões frequentes entre grupos rivais pelo domínio da área. | Registros recorrentes de tiroteios e inquéritos policiais. |
| **Presença Estatal** | Instalação e operação física de equipamentos públicos (batalhões, UPPs, fóruns, presídios). | Decretos, boletins internos e registros de patrimônio público. |

---

## 5. Auditoria Contínua e Responsabilidade Científica

Qualquer pesquisador ou leitor que identificar inconsistência, risco individual a pessoa viva ou anacronismo não sinalizado pode acionar a equipe de pesquisa por meio do canal de verificação arquivística, acionando o pipeline de reavaliação de fontes e revisão do dataset.
