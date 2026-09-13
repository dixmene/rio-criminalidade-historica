# Metodologia e Tipologia de Fontes

---

## 1. Tipologia de Fontes Documentadas

O sistema reconhece e categoriza as seguintes classes de fontes:

| Código de Tipo | Categoria | Exemplos Típicos | Critérios de Avaliação |
|---|---|---|---|
| `academico_tese` | Teses e Dissertações | PPGSA/UFRJ, IESP/UERJ, CPDOC/FGV | Rigor metodológico, revisão por bancas acadêmicas. |
| `academico_artigo` | Artigos Científicos | Periódicos indexados (Scielo, Qualis) | Revisão por pares, fundamentação teórica. |
| `academico_livro` | Obras Historiográficas | Livros de historiadores e cientistas sociais | Citações arquivísticas, metodologia explícita. |
| `oficial_relatorio` | Relatórios Governamentais/Comissões | Relatório CPI das Milícias (2008), Comissão da Verdade | Documentos públicos institucionais com valor de registro. |
| `oficial_seguranca` | Estatísticas Oficiais | ISP-RJ, Depen, Ministério da Justiça | Dados agregados oficiais (atenção para subnotificação). |
| `documento_judicial` | Autos e Denúncias Públicas | Inquéritos do MP-RJ, Sentenças do TJ-RJ | Peças públicas judiciais (distinguir alegação de sentença). |
| `jornalismo_investigativo` | Reportagens de Fôlego | Piauí, Agência Pública, O Globo, Jornal do Brasil | Cobertura documentada, investigação detalhada. |
| `jornalismo_hemeroteca` | Acervos Históricos de Imprensa | Hemeroteca Digital da Biblioteca Nacional | Registro de época (sujeito a censura e filtros do período). |
| `banco_pesquisa` | Observatórios Independentes | GENI/UFF, Fogo Cruzado, Observatório da Segurança | Metodologia pública de monitoramento e validação. |
| `historia_oral` | Entrevistas e Depoimentos | Entrevistas transcritas de moradores e lideranças | Memória individual contextualizada e confrontada com arquivos. |

---

## 2. Metadados Obrigatórios da Fonte

Cada fonte registrada deve conter:

* `source_id`: Identificador único no banco;
* `title`: Título formal do documento ou matéria;
* `author`: Autor(es) individual(is) ou instituição responsável;
* `publisher`: Veículo de publicação, editora ou órgão público;
* `source_type`: Classificação conforme a tabela acima;
* `publication_date`: Data de publicação da fonte;
* `document_date`: Data dos fatos abordados (quando diferente da publicação);
* `url`: Link digital permanente ou arquivado (Wayback Machine);
* `archive_ref`: Identificação física em acervo (ex: Fundo DOPS/Aperj, Caixa 40);
* `file_hash`: Hash SHA-256 do arquivo original armazenado em `data/raw/`;
* `reliability_level`: Classificação de 1 (baixo) a 5 (máximo).

---

## 3. Protocolo de Citação e Rastreabilidade

Ao vincular uma fonte a um evento histórico (`event_sources`):
* O campo `excerpt` é **obrigatório** e deve conter a citação literal que sustenta o registro;
* O campo `page_or_section` deve apontar o local exato dentro do documento (ex: `p. 142-144`, `Capítulo 3`, `Folha 18v`);
* O campo `confidence_notes` deve apontar ressalvas metodológicas caso a fonte seja única ou conflitante.
