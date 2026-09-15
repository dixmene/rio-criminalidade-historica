# Protocolo de Pesquisa — Mapa Histórico, Territorial e Antropológico da Criminalidade no Rio de Janeiro

## 1. Finalidade científica

O projeto é um sistema de pesquisa histórica, sociológica, antropológica e geoespacial. Seu objeto não é produzir uma "verdade operacional" sobre criminalidade, mas organizar evidências heterogêneas, explicitar incertezas e permitir que outra pessoa reconstrua o caminho entre uma afirmação e suas fontes.

A unidade epistemológica central é a **afirmação (claim)**, e não o evento como narrativa indivisível. Um evento pode conter várias proposições, cada uma sustentada, contestada ou matizada por fontes diferentes.

## 2. Perguntas de pesquisa

Toda coleta relevante deve ser vinculada a uma pergunta ou eixo de pesquisa. Exemplos:

- Como organizações e formas de organização armada surgiram, se transformaram, se fragmentaram ou desapareceram?
- Como mudanças territoriais se relacionaram temporalmente com políticas públicas, mercados ilícitos, prisões, infraestrutura urbana e transformações socioeconômicas?
- Como diferentes tipos de fonte descrevem o mesmo episódio e por que suas narrativas divergem?
- Quais períodos, territórios e fenômenos permanecem subdocumentados?

Uma associação temporal ou espacial **não deve ser apresentada como causalidade** sem desenho de pesquisa capaz de sustentá-la.

## 3. Hierarquia e crítica de fontes

Não existe uma hierarquia universal que torne uma categoria de fonte automaticamente verdadeira. A confiabilidade é avaliada em relação à afirmação específica.

Cada fonte deve ser classificada por:

1. **Proveniência** — quem produziu, quando, para qual finalidade e em qual contexto institucional.
2. **Proximidade** — relação temporal e material com o fato descrito.
3. **Independência** — se a fonte reproduz outra fonte ou fornece evidência independente.
4. **Método** — como a informação foi obtida.
5. **Cobertura** — população, território e período representados.
6. **Limitações** — censura, interesse institucional, erro de memória, seleção jornalística, subnotificação, mudanças de classificação etc.
7. **Reprodutibilidade** — possibilidade de localizar novamente o documento ou registro.

Um relatório policial pode ser excelente evidência de que uma instituição registrou determinada ocorrência, mas isso não significa automaticamente que todas as afirmações contidas nele sejam fatos independentes e incontroversos.

## 4. Claims e triangulação

Uma afirmação deve ser atômica o suficiente para que seu suporte possa ser avaliado. Evitar frases que agreguem simultaneamente data, autoria, território, motivação e resultado se as fontes não sustentarem todos esses elementos.

Para cada claim, registrar:

- enunciado;
- tipo de afirmação;
- fontes que apoiam;
- fontes que contestam;
- fontes que apenas mencionam ou contextualizam;
- página/seção/identificador do documento;
- trecho comprobatório;
- notas críticas;
- estado de validação.

**Duas fontes não equivalem automaticamente a confirmação.** Se duas reportagens reproduzem o mesmo despacho, existe uma fonte primária compartilhada, não duas evidências independentes.

## 5. Estados epistemológicos

Os rótulos `confirmado`, `provavel`, `conflitante` e `nao_verificado` são estados de documentação, não probabilidades estatísticas.

- `confirmado`: existe suporte documental adequado para o enunciado específico dentro do escopo definido.
- `provavel`: a evidência é consistente, mas insuficiente para o padrão de confirmação adotado.
- `conflitante`: fontes relevantes apresentam versões incompatíveis ou há controvérsia documental ativa.
- `nao_verificado`: a informação foi localizada, mas ainda não passou pelo protocolo de verificação.

O sistema não deve converter automaticamente esses rótulos em porcentagens de certeza.

## 6. Temporalidade

`date_display` preserva a expressão original da fonte. `date_start` e `date_end` representam os limites de um intervalo de conhecimento, e não necessariamente uma data conhecida.

Exemplos:

| Expressão da fonte | Início | Fim | Precisão | Exata? |
|---|---|---|---|---|
| `15/03/1983` | 1983-03-15 | 1983-03-15 | dia | sim |
| `maio de 1978` | 1978-05-01 | 1978-05-31 | mês | não |
| `1975` | 1975-01-01 | 1975-12-31 | ano | não |
| `década de 1970` | 1970-01-01 | 1979-12-31 | década | não |
| `c. 1982` | 1982-01-01 | 1982-12-31 | aproximado | não |

Nunca apresentar `1975-01-01` como se a fonte tivesse informado 1º de janeiro de 1975.

## 7. Geografia histórica

Uma localização deve carregar sua própria incerteza. Diferenciar:

- ponto exato documentado;
- endereço aproximado;
- bairro/localidade;
- centroide cartográfico;
- polígono administrativo;
- território histórico reconstruído;
- localização desconhecida.

O centroide de um polígono **não é o local do acontecimento**. Ele é apenas uma representação geométrica para visualização.

Perímetros territoriais devem possuir fonte, data de referência, versão do conjunto de dados e descrição do que o polígono significa. Termos como `controle`, `presença`, `influência` e `disputa` não devem ser tratados como sinônimos.

## 8. Estatísticas criminais

Dados administrativos de segurança pública não devem ser tratados como medida transparente da incidência real. Mudanças em registro, classificação, política policial, subnotificação e acesso institucional podem alterar a série observada.

Sempre que possível, o projeto deve manter separados:

- ocorrência registrada;
- vítima/pessoa afetada;
- evento histórico documentado;
- estimativa ou reconstrução secundária;
- indicador populacional ou socioeconômico.

Taxas e comparações territoriais devem explicitar denominador, população de referência, unidade geográfica, período e fonte.

## 9. Ausência de evidência

`NULL` significa ausência de informação disponível no registro; não significa zero. A ausência de uma fonte também não prova que um evento não ocorreu.

O sistema deve distinguir:

- `não localizado`;
- `não informado pela fonte`;
- `não aplicável`;
- `zero documentado`.

## 10. Dados de terceiros e versionamento

Conjuntos geoespaciais ou estatísticos externos devem ser registrados como **snapshots versionados**. Para cada importação, guardar, quando disponível:

- fornecedor;
- título do conjunto;
- URL;
- data de acesso;
- período de referência;
- versão/data de publicação;
- licença;
- hash do arquivo;
- transformação aplicada;
- responsável pela ingestão.

O projeto não deve sobrescrever silenciosamente um snapshot anterior.

## 11. Reprodutibilidade

Uma análise publicada deve poder ser reconstruída a partir de:

`fonte → snapshot → extração → transformação → entidade/claim → análise → visualização`.

Transformações não triviais devem existir em código versionado. Dados derivados devem apontar para os insumos que os produziram.

## 12. Política contra anacronismo

Nomes atuais, fronteiras atuais, categorias criminais atuais e organizações atuais não devem ser projetados retroativamente sobre períodos históricos sem justificativa documental.

Quando uma entidade mudou de nome, território ou composição, o sistema deve representar a continuidade como hipótese documentada ou relação histórica, não como identidade automática.

## 13. Transparência ao público

A interface deve sempre responder a quatro perguntas:

1. **O que estou vendo?**
2. **De onde veio?**
3. **O que exatamente a fonte permite afirmar?**
4. **O que continua incerto?**

Uma visualização bonita não deve esconder ausência de dados, conflitos de fontes ou limites cartográficos.

## 14. Princípio de segurança e ética

O sistema é exclusivamente acadêmico e histórico. Não deve fornecer mecanismos de predição operacional, identificação de alvos, recomendação de ações violentas ou otimização de atividades ilícitas.

Informações sensíveis sobre pessoas devem ser tratadas com proporcionalidade, contexto e respeito à legislação aplicável. Alegações contra indivíduos devem ser claramente distinguidas de fatos judicialmente estabelecidos.

## 15. Critério de publicação

Um registro histórico só deve ser considerado pronto quando:

- sua pergunta de pesquisa estiver definida;
- a fonte estiver catalogada;
- a afirmação estiver atomizada;
- a localização e temporalidade tiverem precisão explícita;
- conflitos relevantes estiverem registrados;
- transformações de dados estiverem documentadas;
- a distinção entre fato documentado e interpretação estiver visível.
