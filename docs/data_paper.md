# Data Paper: Atlas Histórico da Criminalidade, Instituições e Territórios no Rio de Janeiro (1950–2026)

**Autor:** Daniel Farias  
**Repositório:** [github.com/dixmene/rio-criminalidade-historica](https://github.com/dixmene/rio-criminalidade-historica)  
**Versão:** 1.0.0 (Setembro de 2026)  
**Licença dos Dados:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Licença do Código:** MIT License  

---

## Resumo (Abstract)

Este artigo de dados documenta a construção, curadoria arquivística e modelagem espaço-temporal do *Atlas Histórico da Criminalidade no Rio de Janeiro (1950–2026)*. A base de dados integra acontecimentos históricos documentados, perímetros territoriais vetoriais oficiais, equipamentos estatais com ciclo de vida (presídios, batalhões e delegacias), arcos de deslocamento de lideranças e catálogo genealógico de fontes primárias e secundárias. A infraestrutura adota três princípios fundamentais: (1) **Pixel-to-Literal-Quote**, garantindo rastreabilidade ininterrupta do polígono renderizado no mapa até a página e trecho literal do documento probatório; (2) **Honestidade Cartográfica (NULL ≠ 0)**, proibindo a interpolação ou invenção de coordenadas ausentes; e (3) **Embargo Ético de 24 Meses**, agregando ocorrências contemporâneas para prevenção de inteligência tático-operacional e salvaguarda de pessoas vivas.

---

## 1. Contexto Científico e Motivação

Estudos sobre violência urbana, crime organizado e segurança pública no Rio de Janeiro frequentemente sofrem com duas limitações metodológicas:
1. **Anacronismo Cartográfico:** Projeção acrítica de delimitações territoriais recentes de favelas e complexos armados sobre períodos pretéritos (como as décadas de 1970 ou 1980), ocultando as dinâmicas de expansão e metamorfose territorial.
2. **Circularidade de Evidências:** Compilação de reportagens jornalísticas que apenas reproduzem declarações policiais sem o devido cruzamento com inquéritos, decisões judiciais ou literatura historiográfica de referência.

Este atlas foi concebido como uma infraestrutura digital auditável capaz de superar tais gargalos, oferecendo aos pesquisadores de História, Sociologia, Ciência Política e Geografia um acervo com proveniência explícita e grau de incerteza mensurado.

---

## 2. Estrutura e Modelagem do Banco de Dados

O banco de dados relacional foi modelado sob SQLite/PostgreSQL com as seguintes entidades centrais:

| Entidade | Descrição | Principais Atributos |
| :--- | :--- | :--- |
| `Event` | Acontecimento histórico documentado no tempo e no espaço. | `id`, `title`, `date_start`, `date_end`, `temporal_precision`, `confidence_level` |
| `Source` | Unidade documental e bibliográfica com custódia arquivística. | `id`, `title`, `citation`, `source_type`, `file_hash_sha256`, `derived_from_source_id` |
| `SourceDerivation`| Relação genealógica de derivação e citação entre fontes. | `parent_source_id`, `derived_source_id`, `derivation_type`, `is_independent` |
| `Claim` | Afirmação historiográfica atômica com posturas epistemológicas. | `statement`, `claim_type`, `confidence_level`, `is_disputed` |
| `TerritorialDataset`| Metadados arquivísticos de camadas cartográficas oficiais. | `name`, `provider`, `version`, `crs`, `sha256`, `feature_count` |
| `RegionVersion` | Versão temporalizada de limites territoriais (com vigência). | `region_id`, `geometry_geojson`, `valid_from`, `valid_to`, `is_anachronistic` |
| `TerritorialRelation`| Semântica estrita de domínio armado e presença institucional. | `relation_type` (*controle, presenca, influencia, disputa, presenca_estatal*) |
| `InstitutionalFacility`| Equipamentos do Estado com ciclo de vida (abertura/fechamento). | `facility_type`, `opened_at`, `closed_at`, `capacity` |
| `MovementFlow` | Arcos de deslocamento (fugas, transferências carcerárias). | `origin_geometry`, `destination_geometry`, `flow_type`, `evidence_strength` |

---

## 3. Proveniência e Cadeia de Custódia

Toda feição renderizada no Atlas obedece à cadeia de dependência arquivística:

```
Arquivo Original (PDF/Hemeroteca) 
  → Cálculo SHA-256 
  → Cadastro de Source 
  → Extração de Trecho Literal (EventSource) 
  → Formulação de Claim 
  → Vínculo ao Território (RegionVersion) 
  → Renderização MapLibre GL
```

### Datasets Cartográficos Integrados:
1. **Malha de Bairros Oficiais do Rio de Janeiro (166 polígonos):** Instituto Pereira Passos (IPP / Prefeitura da Cidade do Rio de Janeiro), 2022. CRS EPSG:4326. Hash SHA-256: `6c7b74046992ffa5115c7804a7a3612a901a6503b0d00447522b419eb148270c`.
2. **Áreas Integradas de Segurança Pública — AISP (39 polígonos):** Instituto de Segurança Pública (ISP-RJ) / SEPM, 2023. CRS EPSG:4326. Hash SHA-256: `33f7e28f0ba39ce1185bdaf67d0d89670a48acd3e6addf8e84e91c6099faf2b3`.
3. **Mapeamento de Áreas de Risco e Facções Armadas (1.671 polígonos):** dadosderiscos.com.br, 2024. CRS EPSG:4326. Hash SHA-256: `c0ea0aed7aab3768974028162be3a99415a555b471fa90b1daa23d0d755d1b6d`.

---

## 4. Métodos de Validação e Verificação

A integridade do acervo é verificada continuamente por meio de:
- Suite de testes automatizados via `pytest` (102 checagens ativas).
- Auditoria algorítmica de 13 pilares metodológicos (`scripts/audit_research_integrity.py`).
- Verificação de unicidade e independência de raízes documentais (`GenealogyService`), impedindo que cópias jornalísticas sejam contadas como múltiplas evidências independentes.
- Snapshots anuais pré-computados (1958 a 2026) acompanhados de `manifest.json` com hashes SHA-256.

---

## 5. Diretrizes Éticas e Disponibilização

- **Embargo de 24 Meses:** Dados de acontecimentos dos últimos dois anos não exibem pontos exatos no mapa, sendo agregados ao centroide municipal ou de batalhão da PMERJ.
- **Proibição de Inteligência Tática:** O acervo não contém rotas ativas de fuga, locais correntes de comércio de entorpecentes ou endereços residenciais de pessoas vivas.
- **Reprodutibilidade:** Os códigos, dados e notebooks para reprodução das análises e figuras estão integralmente disponíveis no repositório.
