# Diretrizes de Contribuição e Protocolo de Pesquisa

Este projeto é uma iniciativa de **pesquisa histórica, sociológica, antropológica e de dados geoespaciais** sobre o estado do Rio de Janeiro.

---

## 🏛️ Princípios Éticos e Metodológicos

1. **Finalidade Estritamente Acadêmica e Histórica**:
   - Este projeto **NÃO** é uma ferramenta de inteligência operacional policial, monitoramento em tempo real ou assistência a qualquer atividade delituosa.
   - O foco é a análise científica, historiográfica e documentada de dinâmicas territoriais pretéritas e contemporâneas.

2. **Rastreabilidade e Proveniência Estrita de Fontes**:
   - **Nenhum dado é registrado por inferência isolada ou sem fonte documentada.**
   - Toda asserção deve estar vinculada a uma fonte primária ou secundária verificável (jornalismo histórico, teses, dissertações, livros, relatórios oficiais).
   - O trecho textual e a página/arquivo que sustentam a afirmação devem ser obrigatoriamente preservados.

3. **Neutralidade e Tratamento de Conflitos**:
   - Quando fontes respeitáveis divergirem sobre um mesmo fato ou autoria, **ambas as versões devem ser catalogadas**, e o status deve ser registrado como `conflitante` / `disputed`. Nunca arbitre versões sumariamente.

4. **Regras de Dados Inegociáveis**:
   - **Regra do Zero vs. Desconhecido**: Valor numérico `0` denota contagem confirmada como zero. Informações não informadas ou ausentes devem ser armazenadas como `NULL` / `None`.
   - **Preservação do Original**: Nomes, topônimos e citações devem sempre manter o valor original (`original_name`), além do normalizado (`normalized_name`).
