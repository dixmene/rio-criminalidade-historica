# 🔬 METODOLOGIA DE PESQUISA, ATOMIZAÇÃO EM CLAIMS E CRÍTICA DE FONTES
**Projeto**: `rio-criminalidade-historica`  
**Destino Arquivístico**: `docs/metodologia/metodologia_pesquisa_blocos.md`  

---

## 1. O Problema do "Pesquisar em Blocos e Juntar Depois"

Pesquisar fatiando estritamente por décadas e tentar consolidar no final produz falhas estruturais graves:
- **Obras canônicas atravessam décadas**: Carlos Amorim cobre de 1958 a 1993 em um único volume; Michel Misse analisa um século de acumulação social da violência. Cortar obras por década fragmenta o argumento e destrói o contexto.
- **Colisão e Duplicidade no Merge**: O mesmo evento pesquisado em blocos separados entra com datas ligeiramente divergentes, grafias distintas e responsabilidades contraditórias, gerando duplicações em vez de acúmulo de evidência.
- **A Causalidade Histórica Atravessa Fronteiras Cronológicas**: A dinâmica da contravenção na Guanabara dos anos 1950 é a raiz direta das estruturas de corrupção e das armas do tráfico nos anos 1980.

---

## 2. A Solução: A Unidade Atômica de Conhecimento é o CLAIM

```text
┌─────────────────────────────────────────────────────────────┐
│  BLOCO        = Organização do trabalho (quem pesquisa o quê)│
│  CLAIM        = Unidade atômica de conhecimento gravada      │
│  EVENTO       = Agregação documental sobre uma ocorrência   │
│  CONTROVÉRSIA = Claims concorrentes sobre a mesma proposição │
└─────────────────────────────────────────────────────────────┘
```

Ao adotar o `Claim` (`Proposição Factual + Fonte + Página/Seção + Trecho Literal + Postura`):
1. **Fontes convergentes somam evidência**: Duas fontes afirmando o mesmo fato tornam-se dois registros em `ClaimSource`, elevando a confiança do evento;
2. **Fontes divergentes viram controvérsias navegáveis**: Duas fontes discordando geram Claims concorrentes com posturas `apoia` e `contesta`. Nenhuma versão é apagada ou arbitrariamente escolhida;
3. **Fontes soltas apenas penduram claims na grade existente**: Qualquer documento recém-descoberto conecta-se às entidades canônicas sem risco de corrupção do banco.

---

## 3. As Seis Grandes Controvérsias do Campo (Mapeamento Obrigatório)

Estas disputas não representam incerteza técnica do pesquisador, mas sim debates historiográficos reais que devem existir no banco como `Claims` concorrentes:

1. **Gênese e Nome do Comando Vermelho**:
   * *Versão A*: Coletivo penitenciário fundado como "Falange Vermelha" com viés de sobrevivência interna; a alcunha "Comando Vermelho" foi cunhada posteriormente pela imprensa policial (1980/1981).
   * *Versão B*: Organização deliberadamente revolucionária que adotou a sigla CV como projeto político direto.
2. **Impacto Real do Confinamento com Presos Políticos**:
   * *Versão A*: Transmissão sistemática de teoria organizacional, disciplina leninista e táticas de guerrilha aos presos comuns na Ilha Grande.
   * *Versão B*: Tese retrospectiva romantizada; o coletivo adotou apenas técnicas de autodefesa e caixa comum contra o arbítrio prisional, rompendo politicamente após a Lei de Anistia de 1979 que libertou apenas os presos políticos.
3. **Dispersão Prisional como Vetor de Expansão**:
   * O erro de cálculo estratégico do Estado ao dispersar os líderes do Fundão para Ilha Grande, Frei Caneca e presídios do continente como acelerador da expansão da facção.
4. **Homogeneização Faccional e Anacronismo Midiático**:
   * A crítica publicada contra o anacronismo da mídia e da criminologia tradicional que retratam as facções sob a ótica das guerras de drogas contemporâneas, apagando a transição de quadrilhas de assalto a banco para o varejo de drogas.
5. **Gênese da Milícia: Continuidade ou Ruptura?**:
   * *Versão A*: Continuidade evolutiva direta dos esquadrões da morte e da polícia mineira dos anos 1960/1970.
   * *Versão B*: Fenômeno novo da virada dos anos 2000, com racionalidade econômica de monopólio de bens e serviços públicos (gás, transporte alternativo, internet, grilagem imobiliária).
6. **Relação Facção versus Estado**:
   * Confronto entre a retórica oficial da "guerra ao crime organizado" e a produção acadêmica (Misse, Alves, Soares) que documenta a simbiose de "mercadorias políticas" e interpenetração institucional.

---

## 4. Vocabulário de Época para Pesquisas em Acervos

Buscar termos modernos em arquivos anteriores a 1980 inviabiliza os resultados na Hemeroteca Digital da BN. O pesquisador deve utilizar estritamente o léxico coetâneo:

| Período | Termos de Busca Obrigatórios nos Acervos Primários | Termos Anacrônicos Proibidos |
| :--- | :--- | :--- |
| **1950–1969** | `marginal`, `quadrilha`, `contraventor`, `bicheiro`, `banco de bicho`, `esquadrão da morte`, `Scuderie`, `Homens de Ouro`, `Guanabara`, `Diligências Especiais` | "facção", "narcotráfico", "CV", "milícia" |
| **1970–1979** | `assalto a banco`, `preso comum`, `preso político`, `Ilha Grande`, `Cândido Mendes`, `Dois Rios`, `Lei de Segurança Nacional`, `Falange Vermelha`, `Falange Jacaré` | "Comando Vermelho", "PCC", "narcomilícia" |
| **1980–1989** | `Comando Vermelho`, `boca de fumo`, `tóxico`, `cocaína`, `chefe do morro`, `LIESA`, `Castor de Andrade`, `bicheiros` | "narcomilícia", "UPP", "TCP" |
| **1990–1999** | `guerra do tráfico`, `Terceiro Comando`, `Bangu 1`, `rebelião`, `chacina`, `Vigário Geral`, `Candelária`, `Uê`, `Orlando Jogador` | "Complexo de Israel", "narcomilícia" |
| **2000–2009** | `polícia mineira`, `milícia`, `grupo de extermínio`, `CPI das Milícias`, `Batan`, `caveirão`, `Liga da Justiça`, `UPP` | "ADPF 635", "Complexo de Israel" |
| **2010–2026** | `UPP`, `pacificação`, `grupo armado`, `domínio territorial`, `intervenção federal`, `ADPF das Favelas`, `Complexo de Israel` | termos descontextualizados |

---

## 5. Crítica de Fontes e Cadeia Circular de Citação

Para cada fonte catalogada, o sistema audita:
1. **Tipo Epistêmico**: Primária (produzida no momento do fato) vs. Secundária (análise posterior) vs. Terciária (agregadora);
2. **Posição Institucional do Autor**: Agente estatal, jornalista investigativo, participante direto, vítima, pesquisador acadêmico;
3. **Cadeia Circular de Citação**: Uma alegação repetida por 10 livros que todos citam a mesma matéria jornalística de 1983 possui **uma única fonte original**, não dez. O Knowledge Graph registra a proveniência original primária em `source_of_claim` para desmascarar a falsa certeza por repetição circular.

---

## 6. Critério de Parada por Saturação

A pesquisa sobre um determinado período ou entidade é encerrada quando:
> **Três fontes independentes novas consecutivas deixam de produzir Claims inéditos.**
Atingida a saturação, a densidade é atestada e arquivada no relatório de Data Quality.
