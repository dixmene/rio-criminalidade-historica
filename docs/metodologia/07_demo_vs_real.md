# 07. Isolamento Estrito: Dados Técnicos [DEMO] vs. Pesquisa Histórica Real

---

## 1. Princípio do Isolamento

Para testar tecnicamente a interface, a linha do tempo e a integridade de banco antes do início da coleta empírica, dados sintéticos controlados são permitidos sob rígido isolamento.

> **Regra Fundamental**: Dados fictícios de teste jamais podem ser confundidos com dados históricos reais.

---

## 2. Padrões de Identificação Obrigatórios para Dados DEMO

1. **Flag no Banco de Dados**: Toda entidade sintética possui a coluna booleana `is_demo = True`.
2. **Prefixo no Título/Nome**: O nome e título devem obrigatoriamente conter o prefixo `[DEMO] ` (ex: `[DEMO] Assembleia Sindical...`, `[DEMO] Dra. Helena Vasconcelos`).
3. **Isolamento de Contagem**: O método `EventService.count_real_events()` conta apenas registros com `is_demo == False`.

---

## 3. Comportamento da Interface Gráfica

A interface (Streamlit) implementa um seletor explícito de modo de visualização:
* **"Apenas Dados Históricos Reais"**: Modo padrão prioritário. Se nenhum dado histórico tiver sido coletado ainda, exibe um alerta claro e informativo sem poluir com registros falsos.
* **"Incluir Dados Técnicos [DEMO]"**: Modo de desenvolvimento para inspeção e auditoria da interface.
* **"Apenas Dados [DEMO]"**: Modo isolado de teste técnico.
* **Badges Visuais**: Todas as telas e modais exibem etiquetas destacadas (`DADO DEMO` vs. `HISTÓRICO REAL`).
