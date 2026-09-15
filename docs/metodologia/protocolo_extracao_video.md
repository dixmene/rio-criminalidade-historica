# 📋 Protocolo de Extração: YouTube → Corpus Histórico Versionado

**Finalidade**: Padronizar a transformação de acervos audiovisuais (como os 240 episódios da playlist *"Histórias do Rio de Janeiro"* do canal *Iconografia da História*) em um **Corpus Histórico de Pesquisa Científica** perfeitamente integrado à cadeia `Source → Claim → Evidence → Event` do repositório.

---

## 🎯 1. Os 15 Pilares do Protocolo Epistemológico

Para que um vídeo do YouTube não seja tratado como "conteúdo solto" nem como "verdade absoluta", cada episódio processado deve cumprir os seguintes 15 requisitos:

| # | Dimensão do Protocolo | Requisito Metodológico | Modelo / Destino no Sistema |
| :-: | :--- | :--- | :--- |
| **1** | **Catálogo do Acervo** | Identificador estável do corpus (`YTRIO-0001` a `YTRIO-0240`) com rastreabilidade da playlist. | `data/catalogo_playlist_youtube_historias_rio.json` |
| **2** | **Metadados Primários** | Título original, canal produtor, data de publicação, URL canônica e hash da transcrição. | [`Source`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/source.py) (`source_type="audiovisual_youtube"`) |
| **3** | **Custódia da Transcrição** | Arquivo de texto integral da legenda/transcrição arquivado em `data/raw/audiovisual/` com hash SHA-256. | Sidecar de custódia digital (`*_meta.json`) |
| **4** | **Timestamp de Cada Afirmação** | Ponto de partida e término em minutos e segundos (`timestamp_start`, `timestamp_end`). | [`ClaimSource.section`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) (`section="Timestamp 12:45"`) |
| **5** | **Pessoas Mencionadas** | Identificação nominal, vulgo/alcunha e papel social (liderança, policial, autoridade, vítima). | [`Person`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/person.py) (`original_name`, `alias`, `role`) |
| **6** | **Organizações Mencionadas** | Facções, milícias, esquadrões da morte, batalhões ou órgãos do Estado citados. | [`Organization`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/organization.py) (`original_name`, `acronym`, `org_type`) |
| **7** | **Lugares e Territórios** | Favelas, bairros, presídios ou municípios com classificação semântica de controle (`presenca`, `controle`, `influencia`, `disputa`). | [`Region`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/region.py) (`original_name`, `location_precision`) |
| **8** | **Datas e Períodos Históricos** | Expressão original sem falsa precisão (`date_display`) convertida em limites (`date_start`, `date_end`). | [`Event`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/event.py) (Intervalos de conhecimento) |
| **9** | **Acontecimentos Históricos** | Vinculação direta a um evento documentado existente ou proposta de novo registro. | [`Event`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/event.py) |
| **10** | **Claims (Afirmações Atômicas)** | Decomposição em proposições factuais singulares, categorizadas estritamente entre `FACTUAL_CLAIM`, `INTERPRETATION`, `OPINION`, `ALLEGATION`, `TESTIMONY` e `NARRATIVE_DESCRIPTION`. | [`Claim`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py) (`statement`, `claim_type`) |
| **11** | **Fontes Citadas no Vídeo** | Registro explícito de livros, CPIs, inquéritos ou matérias jornalísticas mencionadas no roteiro. | [`SourceDerivation`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) (`reproduz`, `cita`, `resume`) |
| **12** | **Tipologia do Discurso** | Distinção entre **fala do entrevistado**, **fala do pesquisador**, **narração**, **opinião** e **dado documental**. | [`ClaimSource.source_assessment`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |
| **13** | **Grau de Certeza & Postura** | Nível de confiança (`confirmado`, `provavel`, `conflitante`, `nao_verificado`) e postura (`apoia`, `contesta`, `matiza`). | [`Claim.confidence_level`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py), [`ClaimSource.stance`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |
| **14** | **Relações entre Vídeos** | Mapeamento de múltiplos episódios que tratam da mesma guerra territorial ou figura biográfica. | Grafo de relações entre fontes |
| **15** | **Detecção de Raiz Comum** | Identificação de que múltiplos vídeos derivam da mesma obra bibliográfica ou inquérito policial. | [`SourceDerivation.is_independent = False`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |

---

## 🔬 2. Tipologia Epistemológica das Afirmações (Claims)

Para evitar que narrativas ficcionais ou juízos morais sejam gravados como fatos históricos comprovados, cada afirmação deve ser tipada em uma das 6 categorias epistemológicas:

1. `FACTUAL_CLAIM` (*Fato Proposto*): Enunciado que descreve um acontecimento materialmente verificável no tempo e espaço (ex.: *"Em 12 de junho de 1994, ocorreu tiroteio no Morro do Adeus"*).
2. `INTERPRETATION` (*Interpretação Historiográfica*): Hipótese explicativa ou correlação teórica apresentada para conectar eventos (ex.: *"A convivência na Ilha Grande estruturou as técnicas de assalto do grupo"*).
3. `OPINION` (*Opinião Editorial*): Julgamento de valor ou comentário axiológico do produtor de conteúdo (ex.: *"Aquele foi o confronto mais cinematográfico da história carioca"*).
4. `ALLEGATION` (*Alegação / Acusação Não Transitada*): Imputação de crime ou conluio sem sentença condenatória definitiva (ex.: *"O comandante do batalhão recebia semanalmente propina da quadrilha"*).
5. `TESTIMONY` (*Depoimento Oral / Testemunho*): Relato na primeira pessoa de quem viveu ou presenciou o acontecimento (ex.: *"O morador narra que os tiros começaram às 05 horas da manhã"*).
6. `NARRATIVE_DESCRIPTION` (*Descrição de Contexto*): Detalhamento cenográfico, biográfico ou de ambiente urbano (ex.: *"Na época, a favela não possuía acesso asfaltado e era cercada por mata densa"*).

---

## 🤖 3. Prompt Estruturado de Extração para Gemini / NotebookLM

```text
Você é um pesquisador assistente sênior especializado em Historiografia e Sociologia Urbana do Rio de Janeiro.
Analise a transcrição integral do vídeo indicado e extraia uma Ficha Epistemológica estritamente no formato JSON estruturado.

DIRETRIZES DE RIGOR METODOLÓGICO:
1. NÃO invente fatos, pessoas, datas ou números. Se uma informação não for dita no vídeo, registre null.
2. Cada afirmação atômica DEVE conter o timestamp de início (MM:SS) e a citação literal ("excerpt").
3. Classifique a claim_type estritamente entre:
   - "FACTUAL_CLAIM", "INTERPRETATION", "OPINION", "ALLEGATION", "TESTIMONY", "NARRATIVE_DESCRIPTION"
4. Classifique o tipo_discurso estritamente entre:
   - "dado_documental", "fala_pesquisador", "narracao_documental", "fala_entrevistado", "opiniao_editorial"
5. Identifique todas as fontes externas que o vídeo cita ou menciona (ex.: livros de Carlos Amorim, Caco Barcellos, reportagens de jornais, CPIs).

METADADOS DO VÍDEO:
- ID Estável: {CORPUS_ID} (ex: YTRIO-0006)
- Video ID: {VIDEO_ID}
- Título: {VIDEO_TITLE}
- Canal: {VIDEO_CHANNEL}
- URL: {VIDEO_URL}

TRANSCRIÇÃO COMPLETA:
\"\"\"
{VIDEO_TRANSCRIPT}
\"\"\"

FORMATO JSON DE SAÍDA:
{
  "source_meta": {
    "corpus_id": "{CORPUS_ID}",
    "video_id": "{VIDEO_ID}",
    "title": "{VIDEO_TITLE}",
    "channel": "{VIDEO_CHANNEL}",
    "url": "{VIDEO_URL}",
    "periodo_historico_coberto": {
      "date_display": "Texto da data como falado (ex: junho de 1994)",
      "date_start": "YYYY-MM-DD",
      "date_end": "YYYY-MM-DD",
      "temporal_precision": "dia | mes | ano | decada | aproximado",
      "date_is_estimated": false
    },
    "fontes_secundarias_citadas": [
      {
        "nome": "Carlos Amorim (1993)",
        "tipo_relacao": "reproduz | cita | resume | deriva_dado"
      }
    ]
  },
  "entidades": {
    "pessoas": [
      {
        "nome": "Nome completo",
        "alias": "Vulgo",
        "role": "lideranca_criminosa | policial | autoridade | pesquisador | vitima"
      }
    ],
    "organizacoes": [
      {
        "nome": "Comando Vermelho",
        "acronym": "CV",
        "org_type": "faccao_trafico"
      }
    ],
    "territorios": [
      {
        "nome": "Morro do Adeus / Complexo do Alemão",
        "municipio": "Rio de Janeiro",
        "status": "presenca | controle | influencia | disputa"
      }
    ]
  },
  "claims": [
    {
      "statement": "Proposição factual atômica.",
      "claim_type": "FACTUAL_CLAIM | INTERPRETATION | OPINION | ALLEGATION | TESTIMONY | NARRATIVE_DESCRIPTION",
      "timestamp_start": "MM:SS",
      "timestamp_end": "MM:SS",
      "excerpt": "Citação literal transcrita da fala.",
      "tipo_discurso": "narracao_documental | fala_entrevistado | dado_documental | fala_pesquisador | opiniao_editorial",
      "confidence_level": "confirmado | provavel | conflitante | nao_verificado",
      "stance": "apoia | contesta | matiza",
      "epistemological_notes": "Notas sobre possível dependência de fonte ou controvérsia."
    }
  ],
  "evento_relacionado": {
    "id_existente": null,
    "titulo_sugerido": "Título sintético para possível cadastro de Evento",
    "ano": 1994,
    "date_display": "12 de junho de 1994"
  }
}
```
