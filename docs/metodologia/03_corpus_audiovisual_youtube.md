# 🎥 Metodologia do Corpus Audiovisual Histórico: Playlist "Histórias do Rio de Janeiro"

**Identificador do Corpus**: `CORPUS-AV-YTRIO-01`  
**Título Oficial da Playlist**: *Histórias do Rio de Janeiro*  
**Canal Produtor**: [Iconografia da História](https://www.youtube.com/@IconografiadaHistoria)  
**URL Canônica da Playlist**: [https://youtube.com/playlist?list=PLWgXXZQ4cJXJcHQ6Gnx2ZNEizzSvZGDKF](https://youtube.com/playlist?list=PLWgXXZQ4cJXJcHQ6Gnx2ZNEizzSvZGDKF)  
**Volume Mapeado**: **240 episódios**  
**Catálogo Estruturado Canônico**: [`data/catalogo_playlist_youtube_historias_rio.json`](../../data/catalogo_playlist_youtube_historias_rio.json)  
**Padrão de Identificadores Estáveis**: `YTRIO-0001` a `YTRIO-0240`  
**Estatuto Epistemológico**: `audiovisual_youtube` (Fonte Secundária / Divulgação Histórica / Narrativa Audiovisual)

---

## 🎯 1. Objetivo Científico

Transformar um acervo difuso de vídeos no YouTube em um **Corpus Audiovisual Histórico estruturado, auditável e rastreável**.

O objetivo não é aceitar o roteiro do vídeo como fato histórico consumado, mas tratar cada episódio como um documento audiovisual secundário que veicula:
1. Proposições atômicas sobre a realidade (**Claims**);
2. Citações de obras e inquéritos antecedentes (**Linhagem Documental**);
3. Hipóteses interpretativas sobre dinâmicas criminais e estatais (**Interpretações**);
4. Relatos de testemunhas ou envolvidos (**Depoimentos Orais**).

---

## ⚖️ 2. Estatuto Epistemológico da Fonte Audiovisual

```text
NUNCA TRANSFORMAR: "O vídeo disse X"  ──► EM ──►  "X é fato histórico comprovado".
```

Para assegurar o padrão historiográfico digital:

1. **Unidade Atômica de Análise é a Claim**:
   Cada proposição contida no vídeo é extraída individualmente com seu respectivo trecho literal (`excerpt`), timestamp (`MM:SS`) e avaliação crítica da natureza do discurso.
2. **Genealogia e Prevenção de Falsa Triangulação**:
   Muitos episódios baseiam-se em obras clássicas (Amorim, Zaluar, Misse, Barcellos, Paes Manso) ou reportagens da imprensa. Se múltiplos vídeos reproduzem o mesmo livro, o sistema modela a linhagem documental (`SourceDerivation`) com `is_independent = False` para que todos convirjam para uma única **raiz documental (*root source*)**.
3. **Classificação do Discurso**:
   Diferenciação mandatória entre:
   * `dado_documental` (leitura de autos, laudos, certidões);
   * `fala_pesquisador` (análise de especialista creditado);
   * `narracao_documental` (reconstituição cronológica pelo canal);
   * `fala_entrevistado` (relato oral pessoal);
   * `opiniao_editorial` (juízo de valor do canal).

---

## 📑 3. Estrutura Canônica de Identificação (`YTRIO-XXXX`)

Para garantir reprodutibilidade e integridade relacional, nenhum vídeo é referenciado no banco exclusivamente pelo seu título (que pode sofrer alterações pelo canal). O sistema adota a codificação estável `YTRIO-XXXX`:

| ID Canônico | Video ID | Título Original | Território / Foco | Raiz Documental Identificada |
| :---: | :---: | :--- | :--- | :--- |
| `YTRIO-0001` | `XXRL8Kj_dTE` | Brasileirinho, o Mascote da Rocinha | Rocinha (Zona Sul) | Imprensa de Época |
| `YTRIO-0002` | `Nlvz4QlLdZM` | Jorge Luiz de Acari | Favela de Acari | Inquéritos PCERJ (1990) |
| `YTRIO-0003` | `IAndFXthQ0E` | Bem-Te-Vi: O Traficante da Pistola de Ouro | Rocinha (Zona Sul) | Inquéritos / Imprensa (2005) |
| `YTRIO-0004` | `nNjYjrUTNzk` | Madame Satã: O Temido Malandro | Lapa / Centro | História Oral / Memórias |
| `YTRIO-0005` | `axe6V7UzxO0` | Jogo do Bicho: A História Completa | Centro / Baixada / Vila Isabel | Obras Historiográficas Bicho |
| `YTRIO-0006` | `z-6FAKUvUUc` | A Traição de Uê e a Vingança mais Famosa | Alemão / Bangu 1 | Carlos Amorim (1993) |
| `YTRIO-0007` | `XGttAZfZEtc` | Elias Maluco: O Mais Sanguinário do CV | Vila Cruzeiro / Penha | Processos Judiciais Caso Tim Lopes |
| `YTRIO-0008` | `HYi6id0Z2B0` | Adriano da Nóbrega: Oficial mais Violento | Rio das Pedras / Bahia | Operação Os Intocáveis / GAECO |
| `YTRIO-0010` | `k75RJIsmQMw` | A História das Milícias do Rio de Janeiro | Zona Oeste / Jacarepaguá | CPI das Milícias (2008) |
| `YTRIO-0015` | `WGqH1c0dgcw` | A Trajetória de Fernandinho Beira-Mar | Duque de Caxias / Colômbia | CPI do Narcotráfico / Autos Judiciais |
| `YTRIO-0018` | `6hN2W1rP298` | Águia na Cabeça: Castor de Andrade | Bangu / Zona Oeste | Sentença Juíza Denise Frossard (1993) |
| `YTRIO-0026` | `W0qD1gP0gKk` | Bangu 1: A Penitenciária de Segurança Máxima | Gericinó / Bangu | Relatórios DESIPE / Seap |
| `YTRIO-0027` | `7uK0P2j9aN4` | Scuderie Detetive Le Coq | Guanabara / Baixada | Arquivo DOPS / Hemeroteca BN |

---

## 🔄 4. O Pipeline de Ingestão: Do YouTube ao Atlas

```text
YOUTUBE (Vídeo + Áudio)
   │
   ▼
TRANSCRIÇÃO LITERAL COM TIMESTAMPS
   │  status: exact | generated | unavailable | manually_verified
   │  hash SHA-256 do arquivo original
   ▼
EXTRAÇÃO DE CLAIMS ATÔMICAS
   │  statement, excerpt, timestamp_start, timestamp_end
   │  tipo_discurso, certeza, entidades (Pessoas, Organizações, Territórios)
   ▼
VALIDADOR ANTI-ALUCINAÇÃO
   │  rejeita claims sem correspondência literal em excerpt
   │  gera validation_report.json
   ▼
GENEALOGIA DOCUMENTAL (SourceDerivation)
   │  detecta obras antecedentes citadas (reproduz, cita, resume)
   │  assinala is_independent = False para derivações
   ▼
BANCO RELACIONAL SQLITE (rio_historico.db)
   │  Source (YTRIO-XXXX) ──► Claim ──► ClaimSource ──► Event
   ▼
FICHA EPISTEMOLÓGICA NO ATLAS EDITORIAL
   │  exibição estruturada com separação entre fato, alegação e interpretação
```

---

## ⚠️ 5. Limitações e Salvaguardas Metodológicas

1. **Natureza Comercial da Plataforma**: O YouTube utiliza títulos chamativos e estratégias de retenção visual que podem enfatizar episódios sensacionalistas. O pesquisador deve extrair a base factual, descartando adjetivações retóricas.
2. **Dependência de Obras Não Citadas**: Por vezes o roteiro utiliza informações de um livro sem fornecer a citação bibliográfica explícita. O trabalho do pesquisador no sistema inclui registrar a paternidade intelectual do dado em `notes` de `SourceDerivation`.
3. **Preservação de Conflitos**: Quando o vídeo apresenta uma versão divergente da historiografia consolidada ou de autos judiciais, a proposição é cadastrada com postura `contesta` ou `matiza`, preservando a controvérsia visível na Ficha Epistemológica.
