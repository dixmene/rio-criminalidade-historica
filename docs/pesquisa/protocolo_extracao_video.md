# 📋 Protocolo de Extração: YouTube → Corpus Histórico Versionado

**Finalidade**: Padronizar a transformação de acervos audiovisuais (como os 240 vídeos da playlist *"Histórias do Rio de Janeiro"* do canal *Iconografia da História*) em um **Corpus Histórico de Pesquisa Científica** perfeitamente integrado à cadeia `Source → Claim → Evidence → Event` do repositório.

---

## 🎯 1. Os 15 Pilares do Protocolo Epistemológico

Para que um vídeo do YouTube não seja tratado como "conteúdo solto" nem como "verdade absoluta", cada episódio processado deve cumprir os seguintes 15 requisitos:

| # | Dimensão do Protocolo | Requisito Metodológico | Modelo / Destino no Sistema |
| :-: | :--- | :--- | :--- |
| **1** | **Catálogo do Acervo** | Identificador estável do corpus (`YT-001` a `YT-240`) com rastreabilidade da playlist. | `data/catalogo_playlist_youtube_historias_rio.json` |
| **2** | **Metadados Primários** | Título original, canal produtor, data de publicação, URL canônica e hash da transcrição. | [`Source`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/source.py) (`source_type="audiovisual_youtube"`) |
| **3** | **Custódia da Transcrição** | Arquivo de texto integral da legenda/transcrição arquivado em `data/raw/audiovisual/` com hash SHA-256. | Sidecar de custódia digital (`*_meta.json`) |
| **4** | **Timestamp de Cada Afirmação** | Ponto de partida em minutos e segundos (`MM:SS`) onde a proposição factual é narrada. | [`ClaimSource.section`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) (`section="Timestamp 12:45"`) |
| **5** | **Pessoas Mencionadas** | Identificação nominal, vulgo/alcunha e papel social (liderança, policial, autoridade, vítima). | [`Person`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/person.py) (`original_name`, `alias`, `role`) |
| **6** | **Organizações Mencionadas** | Facções, milícias, esquadrões da morte, batalhões ou órgãos do Estado citados. | [`Organization`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/organization.py) (`original_name`, `acronym`, `org_type`) |
| **7** | **Lugares e Territórios** | Favelas, bairros, presídios ou municípios com classificação semântica de controle. | [`Region`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/region.py) (`original_name`, `location_precision`) |
| **8** | **Datas e Períodos Históricos** | Expressão original sem falsa precisão (`date_display`) convertida em limites (`date_start`, `date_end`). | [`Event`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/event.py) (Intervalos de conhecimento) |
| **9** | **Acontecimentos Históricos** | Vinculação direta a um evento documentado existente ou proposta de novo registro. | [`Event`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/event.py) |
| **10** | **Claims (Afirmações Atômicas)** | Decomposição em proposições factuais singulares, objetivas e auditáveis. | [`Claim`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py) (`statement`, `claim_type`) |
| **11** | **Fontes Citadas no Vídeo** | Registro explícito de livros, CPIs, inquéritos ou matérias jornalísticas mencionadas no roteiro. | [`SourceDerivation`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) (`reproduz`, `cita`, `resume`) |
| **12** | **Tipologia do Discurso** | Distinção entre **fala do entrevistado**, **fala do pesquisador**, **narração**, **opinião** e **dado documental**. | [`ClaimSource.source_assessment`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |
| **13** | **Grau de Certeza & Postura** | Nível de confiança (`confirmado`, `provavel`, `conflitante`) e postura (`apoia`, `contesta`, `matiza`). | [`Claim.confidence_level`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py), [`ClaimSource.stance`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |
| **14** | **Relações entre Vídeos** | Mapeamento de múltiplos episódios que tratam da mesma guerra territorial ou figura biográfica. | Grafo de relações entre fontes |
| **15** | **Detecção de Raiz Comum** | Identificação de que múltiplos vídeos derivam da mesma obra bibliográfica ou inquérito policial. | [`SourceDerivation.is_independent = False`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/associations.py) |

---

## 🔬 2. Tipologia do Discurso e Grafo de Derivação

```mermaid
flowchart TD
    subgraph Raiz["Raiz Documental Primária / Canônica"]
        L1["Livro: Carlos Amorim (1993)"]
        P1["Inquérito Policial PCERJ"]
    end

    subgraph Videos["Corpus Audiovisual YouTube"]
        V1["Vídeo YT-006: A Traição de Uê"]
        V2["Vídeo YT-015: Beira-Mar"]
        V3["Vídeo YT-026: Bangu 1"]
    end

    L1 -->|reproduz (is_independent=False)| V1
    L1 -->|cita (is_independent=False)| V2
    P1 -->|deriva_dado (is_independent=False)| V3

    subgraph Claims["Decomposição em Claims com Tipo de Discurso"]
        C1["Claim: Emboscada a Orlando Jogador"]
        V1 -->|Timestamp 08:34 · Discurso: narracao_documental| C1
        V1 -->|Timestamp 14:20 · Discurso: fala_entrevistado| C1
    end

    style Raiz fill:#2b2b2b,stroke:#7A2E2E,color:#fff
    style Claims fill:#f5f3ee,stroke:#7A2E2E,color:#20201e
```

### Tipologia do Discurso (`tipo_discurso`):
* `dado_documental`: Citação de boletim policial, certidão, laudo balístico ou decisão de sentença.
* `fala_pesquisador`: Análise fundamentada por historiador, sociólogo ou jornalista investigativo creditado.
* `narracao_documental`: Roteiro explicativo que sintetiza a cronologia dos fatos.
* `fala_entrevistado`: Depoimento oral de testemunha, morador, policial ou envolvido direto.
* `opiniao_editorial`: Juízo de valor ou interpretação subjetiva do produtor de conteúdo.

---

## 🤖 3. Prompt de Extração para Gemini / NotebookLM

```text
Você é um pesquisador assistente sênior especializado em Historiografia e Sociologia Urbana do Rio de Janeiro.
Analise a transcrição integral do vídeo indicado e extraia uma Ficha Epistemológica estritamente no formato JSON estruturado.

DIRETRIZES DE RIGOR METODOLÓGICO:
1. NÃO invente fatos, pessoas, datas ou números. Se uma informação não for dita no vídeo, registre null.
2. Cada afirmação atômica DEVE conter o timestamp de início (MM:SS) e a citação literal ("excerpt").
3. Classifique o tipo_discurso estritamente entre:
   - "dado_documental" (autos, certidões, sentenças citadas)
   - "fala_pesquisador" (pesquisador acadêmico ou jornalista especializado)
   - "narracao_documental" (narração que relata cronologia factual)
   - "fala_entrevistado" (depoimento pessoal oral)
   - "opiniao_editorial" (comentário subjetivo do canal)
4. Identifique todas as fontes externas que o vídeo cita ou menciona (ex.: livros de Carlos Amorim, Caco Barcellos, reportagens de jornais, CPIs).

METADADOS DO VÍDEO:
- ID: {VIDEO_ID}
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
        "status": "controle | presenca | disputa"
      }
    ]
  },
  "claims": [
    {
      "statement": "Proposição factual atômica.",
      "timestamp": "MM:SS",
      "excerpt": "Citação literal transcrita da fala.",
      "tipo_discurso": "narracao_documental | fala_entrevistado | dado_documental | fala_pesquisador",
      "confidence_level": "confirmado | provavel | conflitante",
      "stance": "apoia | contesta | matiza",
      "epistemological_notes": "Notas sobre possível dependência de fonte ou controvérsia."
    }
  ],
  "evento_relacionado": {
    "id_existente": null,
    "titulo_sugerido": "Execução de Orlando Jogador por Uê no Complexo do Alemão",
    "ano": 1994,
    "date_display": "12 de junho de 1994"
  }
}
```

---

## 💻 4. Pipeline de Ingestão Automatizado no Repositório

O script [`scripts/ingestion/ingest_youtube_corpus.py`](file:///C:/Users/dani/Documents/Daniel%20Systems/scripts/ingestion/ingest_youtube_corpus.py) executa:
1. Sincronização dos 240 episódios na tabela `sources`;
2. Importação das fichas JSON geradas pelo Gemini / NotebookLM;
3. Criação de registros `SourceDerivation` com `is_independent=False` quando obras já cadastradas (ex.: Carlos Amorim) forem citadas no vídeo;
4. Povoamento atômico das tabelas `claims` e `claim_sources`.
