# 📌 STATUS DO PROJETO — ONDE PARAMOS
**Data do Registro**: 13 de Setembro de 2026  
**Repositório Remoto**: [GitHub (Privado) — `dixmene/rio-criminalidade-historica`](https://github.com/dixmene/rio-criminalidade-historica)  
**Branch Atual**: `main`  
**Qualidade Técnica**: 17/17 Testes Automatizados Aprovados (`pytest -v`)

---

## 🟢 1. O que foi Concluído nesta Etapa

### A. Download e Catalogação Automatizada do Corpus do NotebookLM
1. **Pipeline de Ingestão e Hashes Criptográficos (`scripts/ingestion/download_corpus.py`)**:
   - Baixou documentos integrais em `data/raw/` organizados por pastas temáticas (`academia/`, `governo/`, `processos_publicos/`, `seguranca_publica/`, `jornalismo/`).
   - Gerou metadados arquivísticos em formato JSON sidecar (`*_meta.json`) com cálculo de **SHA-256** para auditoria e custódia digital.
   - Gerou o catálogo consolidado `data/catalogo_fontes_notebooklm.json`.

2. **Documentos Físicos e Digitais no Acervo Local**:
   - `data/raw/academia/no_sapatinho_milicia_rj.pdf` (6.3 MB) — Heinrich Böll / LAV-UERJ
   - `data/raw/processos_publicos/stf_adpf_635_info_sociedade.pdf` (190 KB) — Supremo Tribunal Federal (ADPF das Favelas)
   - `data/raw/seguranca_publica/isp_balanco_indicadores_upp_2015.pdf` (564 KB) — Instituto de Segurança Pública (ISP-RJ)
   - `data/raw/academia/clio_ufpel_artigo_historico.pdf` (211 KB) — Revista Clio (UFPel)
   - `data/raw/academia/revista_passagens_uff_artigo.pdf` (584 KB) — Revista Passagens (UFF)
   - `data/raw/academia/redalyc_trajetoria_milicias_rj.pdf` (169 KB) — Redalyc
   - `data/raw/governo/sepm_rj_historico_bope.html` (98 KB) — Polícia Militar do RJ (Histórico Oficial NuCOE/BOPE)
   - `data/raw/jornalismo/elpais_adriano_nobrega_submundo_rj.html` (335 KB) — El País Brasil
   - `data/raw/jornalismo/elpais_intervencao_federal_seguranca_rj.html` (331 KB) — El País Brasil
   - `data/raw/jornalismo/ihu_upps_ajustes_fracasso.html` (55 KB) — IHU Unisinos

3. **Módulo de Extração Multi-Formato (`scripts/extraction/extract_text.py`)**:
   - Extração estruturada de páginas e texto limpo para PDFs (`pdfplumber` / `pypdf`) e páginas web (`BeautifulSoup`).

---

### B. Ingestão do Piloto Histórico Real (1970–1989)
1. **Script de Ingestão Factual (`scripts/ingestion/seed_real_sources.py`)**:
   - **12 Fontes Históricas Reais** cadastradas com citação formal, autoria, tipologia, link arquivístico e hash SHA-256 (`is_demo=False`).
   - **8 Territórios Históricos Reais**:
     - Com coordenadas cartográficas delimitadas (Ilha Grande/Dois Rios, Quartel Sulacap, Centro/Rua Gonçalves Dias, Brás de Pina/Penha, Sambódromo da Marquês de Sapucaí, Estácio/Caetano de Faria, Morro do Juramento).
     - Com coordenadas estritamente `NULL` (Rede Penitenciária Geral da Guanabara), cumprindo a **Regra 1 (Não invenção de coordenadas)**.
   - **6 Organizações Históricas**: Comando Vermelho, PMERJ, NuCOE/BOPE, Scuderia Le Cocq / Homens de Ouro, Cúpula da Contravenção e LIESA.
   - **7 Lideranças e Personagens Históricos**: Rogério Lemgruber (Bagulhão), William da Silva Lima (Professor), Capitão Amendola, Mariel Mariscot, Castor de Andrade, José Carlos dos Reis Encina (Escadinha), José Jorge Saldanha (Zezinho).
   - **10 Eventos Históricos Reais Documentados (1970–1989)**:
     - 1970: Aplicação da Lei de Segurança Nacional e Remessa de Presos Comuns e Políticos para a Ilha Grande.
     - 1978: Criação do Núcleo da Companhia de Operações Especiais (NuCOE) da PMERJ (Boletim nº 14).
     - 1979: Fundação e Estruturação do Coletivo 'Falange Vermelha' no Instituto Penal Cândido Mendes.
     - 1981: O Cerco da Rua Juramento e a Consagração Pública do Termo 'Comando Vermelho'.
     - 1982: Assassinato do Ex-Policial Mariel Mariscot no Centro do Rio de Janeiro.
     - 1984: Fundação da Liga Independente das Escolas de Samba (LIESA) e Monopólio da Contravenção.
     - 1985: Fuga de Helicóptero de José Carlos dos Reis Encina ('Escadinha') do Presídio da Ilha Grande.
     - 1988: Reorganização e Elevação do NuCOE para Companhia de Operações Especiais (COE) da PMERJ.
     - 1980-1988: Circulação e Codificação das Primeiras Cartas e Estatuto Disciplinar do Comando Vermelho.
     - 1989: Transferência Gradual de Lideranças da Ilha Grande e Transição do Foco Territorial para as Favelas.
   - **100% dos eventos possuem fontes vinculadas com citação textual literal (`excerpt`), página ou seção e validação de afirmação**.

---

### C. Unificação do Banco de Dados e Testes Automatizados
1. **Unificação da Conexão**:
   - `app/config.py` e `config/settings.py` unificados para apontar diretamente para `data/rio_historico.db`.
2. **Suíte de Testes Aprovada (17/17)**:
   - Novo teste `tests/test_real_pilot_data.py` validando integridade, proveniência estrita, não-invenção de coordenadas e hashes da base real.
   - Isolamento total entre dados reais (`is_demo=False`) e dados sintéticos (`is_demo=True`).
3. **Painel Interativo (Streamlit + Folium)**:
   - Configurado por padrão para o modo **"Apenas Dados Históricos Reais"**, exibindo o mapa interativo, linha do tempo 1970–1989, cards de proveniência com citação literal e caixa de territórios sem coordenadas geográficas.

---

## 🛑 2. Situação Atual do Banco de Dados (`data/rio_historico.db`)

| Entidade | Dados Históricos Reais (`is_demo=False`) | Dados Técnicos de Teste (`is_demo=True`) | Total |
| :--- | :---: | :---: | :---: |
| **Eventos** | **10** | 10 | 20 |
| **Fontes Documentais** | **12** | 6 | 18 |
| **Regiões / Territórios** | **8** | 10 | 18 |
| **Organizações** | **6** | 6 | 12 |
| **Pessoas / Biografias** | **7** | 5 | 12 |

---

## 🚀 3. Próximos Passos Recomendados

1. **Expansão do Recorte Histórico para os Anos 1990 (Fase 2)**:
   - Ingestão de eventos da década de 1990: desativação/demolição do Instituto Penal Cândido Mendes (1994), CPI do Narcotráfico, surgimento do Terceiro Comando (TC) e Amigos dos Amigos (ADA).
2. **Extração das Fontes do Acervo de Transição (2000–2020)**:
   - Utilizar o extrator nos PDFs já baixados (`no_sapatinho_milicia_rj.pdf`, `isp_balanco_indicadores_upp_2015.pdf`, `stf_adpf_635_info_sociedade.pdf`) para catalogar eventos da gênese das milícias e UPPs.
3. **Refinamento Cartográfico**:
   - Adicionar arquivos GeoJSON vetoriais dos bairros e limites de favelas históricas em `data/geospatial/`.

---

## 💻 4. Comandos para Execução e Demonstração

```powershell
# 1. Ativar o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 2. Rodar todos os testes automatizados (17 testes)
pytest -v

# 3. Executar o Painel Interativo no Navegador
streamlit run app/ui/app.py

# 4. Re-executar ou atualizar a carga histórica real se necessário
python -m scripts.ingestion.seed_real_sources
```
