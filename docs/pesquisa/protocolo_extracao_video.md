# 📋 Protocolo de Extração Epistemológica de Vídeos Históricos

**Finalidade**: Padronizar a ingestão de vídeos, entrevistas e minidocumentários da playlist *"Histórias do Rio de Janeiro"* (e outros acervos audiovisuais) no modelo de dados científico do projeto (`Source → Claim → Evidence → Event`).

---

## 🎯 1. Princípios do Protocolo

1. **Separação entre Fato, Afirmação e Interpretação**:
   - **Fato Documentado**: Acontecimento com comprovação oficial ou judicial inequívoca (ex.: "Bangu 1 foi inaugurado em 1987").
   - **Claim (Afirmação Factual)**: O que o narrador ou entrevistado declara ter ocorrido (ex.: "A facção X pagava propina mensal de R$ 50 mil ao batalhão Y").
   - **Interpretação**: A tese explicativa que o vídeo propõe sobre o fato (ex.: "A criação da facção foi consequência direta do convívio com os presos políticos").
2. **Citação Literal com Timestamp (`excerpt` + `timestamp`)**:
   - Nenhuma afirmação pode ser salva sem a marcação temporal exata (`MM:SS`) e a transcrição literal de pelo menos uma frase representativa.
3. **Rastreamento de Fontes Citadas (*Stemma Codicum*)**:
   - Se o vídeo cita explicitamente um livro (ex.: Carlos Amorim, Caco Barcellos), uma CPI (ex.: CPI das Milícias de Freixo) ou uma matéria jornalística, esses dados devem ser registrados em `fontes_secundarias_citadas` para evitar falsa triangulação.
4. **Intervalos Temporais sem Falsa Precisão**:
   - Menções a anos ("em 1984") devem ser registradas como intervalos `1984-01-01` a `1984-12-31` com precisão `ano`, nunca `01/01/1984` como dia exato.

---

## 🤖 2. Prompt Estruturado de Extração (Template para Gemini / NotebookLM)

```text
Você é um pesquisador assistente sênior em História e Sociologia da Violência no Rio de Janeiro.
Sua tarefa é analisar a transcrição integral do vídeo abaixo e produzir uma ficha epistemológica estritamente estruturada em formato JSON.

REGRAS INEGOCIÁVEIS:
1. NÃO invente fatos, pessoas, datas ou números. Se uma data ou local não for explicitamente mencionado, registre null.
2. Cada afirmação extraída DEVE conter o timestamp de início (MM:SS) e a citação textual literal da transcrição ("excerpt").
3. Distinga rigorosamente:
   - "confirmado": fato amplamente estabelecido em fontes judiciais/acadêmicas citadas no vídeo.
   - "provavel": alegação consistente, mas sem comprovação documental direta na fala.
   - "conflitante": versão que colide com outras narrativas conhecidas ou contestada no próprio vídeo.
4. Preserve a grafia original dos nomes e favelas citados.

METADADOS DO VÍDEO:
- ID: {VIDEO_ID}
- Título: {VIDEO_TITLE}
- Canal: {VIDEO_CHANNEL}
- URL: {VIDEO_URL}

TRANSCRIÇÃO DO VÍDEO:
\"\"\"
{VIDEO_TRANSCRIPT}
\"\"\"

SAÍDA OBRIGATÓRIA (JSON VÁLIDO):
{
  "source_meta": {
    "video_id": "{VIDEO_ID}",
    "title": "{VIDEO_TITLE}",
    "channel": "{VIDEO_CHANNEL}",
    "url": "{VIDEO_URL}",
    "periodo_historico_coberto": {
      "date_display": "ex: anos 1980 a 1994",
      "date_start": "YYYY-MM-DD",
      "date_end": "YYYY-MM-DD",
      "temporal_precision": "ano | decada | dia | mes | intervalo",
      "date_is_estimated": true | false
    },
    "fontes_ou_autores_citados_no_video": ["ex: Carlos Amorim (1993)", "Jornal O Globo", "CPI das Milícias"]
  },
  "entidades_mencionadas": {
    "pessoas": [
      {
        "nome": "Nome completo ou grafia usada",
        "vulgo": "Apelido conhecido ou null",
        "papel": "lideranca_criminosa | policial | autoridade_publica | pesquisador | vitima | contraventor"
      }
    ],
    "organizacoes": [
      {
        "nome": "Nome da facção, milícia, batalhão ou instituição",
        "sigla": "CV | TCP | ADA | PMERJ | PCERJ | BOPE | etc.",
        "tipo": "faccao_trafico | grupo_paramilitar_milicia | cupula_contravencao | orgao_seguranca | orgao_justica"
      }
    ],
    "territorios": [
      {
        "nome": "Nome da comunidade, favela ou bairro",
        "municipio": "Rio de Janeiro | Duque de Caxias | etc.",
        "status_mencionado": "presenca | controle | influencia | disputa"
      }
    ]
  },
  "claims": [
    {
      "claim_type": "fato | data | autoria | territorio | baixa_letal | motivacao | relacao_estado",
      "statement": "Enunciado factual atômico e objetivo.",
      "timestamp": "MM:SS",
      "excerpt": "Citação literal transcrita da fala no vídeo que sustenta a afirmação.",
      "confidence_level": "confirmado | provavel | conflitante",
      "stance": "apoia | contesta | matiza",
      "epistemological_notes": "Análise crítica sobre a fonte primária dessa alegação ou possível viés."
    }
  ],
  "acontecimento_central_sugerido": {
    "title": "Título sintético para possível cadastro de Evento Histórico",
    "year": 1994,
    "date_display": "12 de junho de 1994",
    "description": "Descrição factual resumida do acontecimento principal.",
    "confidence_level": "confirmado | provavel | conflitante"
  }
}
```

---

## 🔄 3. Mapeamento Direto com os Modelos SQLAlchemy do Repositório

| Campo da Extração JSON | Modelo de Destino no Banco | Atributo / Coluna |
| :--- | :--- | :--- |
| `source_meta.title`, `url` | [`Source`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/source.py) | `title`, `url`, `source_type="audiovisual_youtube"` |
| `source_meta.fontes_citadas` | [`Source`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/source.py) | `notes`, `derived_from_source_id` |
| `claims[i].statement` | [`Claim`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py) | `statement`, `claim_type`, `confidence_level` |
| `claims[i].excerpt`, `timestamp` | [`ClaimSource`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/claim.py) | `excerpt`, `section=f"Timestamp {timestamp}"`, `stance` |
| `acontecimento_central` | [`Event`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/event.py) | `title`, `date_display`, `date_start`, `date_end`, `description` |
| `entidades.pessoas` | [`Person`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/person.py) | `original_name`, `alias`, `role` |
| `entidades.organizacoes` | [`Organization`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/organization.py) | `original_name`, `acronym`, `org_type` |
| `entidades.territorios` | [`Region`](file:///C:/Users/dani/Documents/Daniel%20Systems/app/models/region.py) | `original_name`, `municipality`, `location_precision="aproximada"` |

---

## 🛡️ 4. Critérios de Rejeição e Auditoria de Qualidade

1. **Rejeição Automática de Alucinações**: Se o campo `excerpt` não existir ipsis litteris na transcrição do vídeo, a claim é descartada na validação Pydantic.
2. **Salvaguarda contra Imputação Caluniosa**: Alegações sobre envolvimento de autoridades públicas ainda vivas sem citação explícita de condenação judicial transitada em julgado ou relatório oficial de CPI devem ser catalogadas estritamente com `confidence_level = "nao_verificado"` e notas explicativas.
3. **Auditabilidade SHA-256 da Transcrição**: Cada arquivo de transcrição `.txt` ou `.json` ingerido gera um sidecar com cálculo de hash SHA-256 em `data/raw/audiovisual/` para garantia de integridade arquivística.
