# 📐 DIRETRIZES DE DESIGN SYSTEM & REGRAS DE COMPORTAMENTO OPERACIONAL DA IA
**Documento Normativo de Interface — Projeto Rio Criminalidade Histórica**  
**Versão**: 1.0.0 (Atlas Editorial & Arquivo Historiográfico)  
**Status**: INVIOLÁVEL / ATIVO  

---

## 🛑 1. Regras de Comportamento da IA (Contrato Operacional Estrito)

> ### ⚠️ INSTRUÇÃO DIRETIVA MANDATÓRIA PARA MODELOS DE IA
> 
> Você está **ESTRITAMENTE PROIBIDO** de exercer qualquer tipo de "criatividade visual", liberdade estética ou improvisação estilística neste projeto.
> 
> 1. **Proibição de Novas Cores**: Você **NÃO PODE** introduzir nenhum código hexadecimal, cor RGB, HSL ou gradiente que não esteja expressamente catalogado neste documento. É expressamente vedado o uso de azul neon (`#38BDF8`), fundos escuros de SaaS (`#0B1120`, `#0F172A`), roxos de IA ou gradientes radiais.
> 2. **Proibição de Novas Fontes**: Você **NÃO PODE** importar nem declarar nenhuma família tipográfica além de `Libre Baskerville` (títulos), `Source Sans 3` (interface/leitura) e `JetBrains Mono` (código/dados).
> 3. **Proibição de Espaçamentos Aleatórios**: Você **NÃO PODE** inventar valores arbitrários de margem, padding ou gap (como `13px`, `19px`, `27px`, etc.). Todos os espaçamentos devem obedecer rigorosamente à escala matemática de múltiplos de 4px e 8px definida na Seção 4.
> 4. **Proibição de Bibliotecas Não Autorizadas**: Você **NÃO PODE** adicionar novas dependências de componentes, bibliotecas de animação, frameworks CSS ou pacotes de ícones sem autorização explícita.
> 5. **Papel Exclusivo de Executora**: Você atua exclusivamente como uma **executora determinística do Design System**. Sua única função no front-end é aplicar literal e rigorosamente as variáveis CSS, classes utilitárias e regras geométricas estipuladas neste arquivo. Qualquer desvio é considerado quebra de conformidade de código.

---

## 🎨 2. Sistema de Cores (Paleta e Contraste Arquivístico)

A identidade visual é fundamentada na estética de **papel de arquivo histórico, fichamento físico e encadernação clássica**. O contraste atende aos requisitos de acessibilidade WCAG AAA para texto e WCAG AA para componentes interativos.

### 2.1 Variáveis CSS Oficiais (`:root`)

```css
:root {
    /* =========================================================================
       SUPERFÍCIES E FUNDOS
       ========================================================================= */
    --bg-canvas:          #F5F3EE; /* Fundo principal da aplicação (Papel marfim/pergaminho) */
    --bg-surface:         #FFFFFF; /* Fundo de cartões, dossiês e fichas catalográficas */
    --bg-subtle:          #EBE7DF; /* Fundo secundário para barras, cabeçalhos de tabelas e sidebar */
    --bg-muted:           #E2DDD2; /* Fundo de áreas desativadas ou chips secundários */

    /* =========================================================================
       BORDAS E DIVISORES (Linhas estruturais nítidas e finas)
       ========================================================================= */
    --border-subtle:      #D8D3C9; /* Borda padrão para cards, tabelas e divisórias */
    --border-strong:      #B5AEA0; /* Borda de campos de input, foco e ênfase */
    --border-contrast:    #4A463D; /* Divisores fortes de grandes seções editoriais */

    /* =========================================================================
       TIPOGRAFIA E TEXTOS (Contraste estrito de alta legibilidade)
       ========================================================================= */
    --text-primary:       #1C1B18; /* Texto primário: títulos, corpo e rótulos principais */
    --text-secondary:     #5A564F; /* Texto secundário: metadados, fontes, subtítulos e apoio */
    --text-tertiary:      #827D72; /* Texto terciário: placeholders, legendas de data e rodapés */
    --text-on-accent:     #FFFFFF; /* Texto exclusivo sobre botões de destaque */

    /* =========================================================================
       COR DE DESTAQUE / AÇÃO (Uso estritamente delimitado)
       ========================================================================= */
    --accent-action:       #7A2E2E; /* Vinho encadernação clássica: botões de ação e tabs ativas */
    --accent-action-hover: #5C2222; /* Hover para ações primárias */
    --accent-subtle:       #F7EBEB; /* Fundo suave para foco contextual ou badges de destaque */

    /* =========================================================================
       ESTADOS SEMÂNTICOS & HISTORIOGRÁFICOS (Validados para fundo claro)
       ========================================================================= */
    /* Erro / Postura Historiográfica: CONTESTA */
    --status-error-text:   #9E2A2B; /* Vermelho escuro de erro / divergência */
    --status-error-bg:     #FDF2F2;
    --status-error-border: #F1B5B5;

    /* Sucesso / Postura Historiográfica: APOIA */
    --status-success-text:   #2D5A27; /* Verde floresta de validação / consenso */
    --status-success-bg:     #F0F6F0;
    --status-success-border: #BBDCB8;

    /* Aviso / Postura Historiográfica: MATIZA */
    --status-warning-text:   #8C580E; /* Âmbar ocre de atenção / modulação */
    --status-warning-bg:     #FEF9EE;
    --status-warning-border: #F6DEA0;

    /* Informativo / Neutro */
    --status-info-text:      #2B4C6F; /* Azul petróleo arquivístico */
    --status-info-bg:        #EFF4F9;
    --status-info-border:    #BCD4EC;
}
```

### 2.2 Regras de Aplicação de Cor

* **Contaminação Proibida**: A cor de destaque `--accent-action` (`#7A2E2E`) pertence exclusivamente a elementos de ação explícita (botões primários de ação, indicador de aba ativa e borda de foco). É **terminantemente proibido** utilizá-la como cor de fundo de grandes cartões, barras completas ou fundos de página.
* **Proibição de Fundo Escuro**: A aplicação inteira deve permanecer sobre a paleta clara `--bg-canvas` (`#F5F3EE`) e `--bg-surface` (`#FFFFFF`). Não é permitido alternar para modos escuros artificiais com gradientes de SaaS.

---

## 🔤 3. Tipografia e Escala (Hierarquia Historiográfica)

A tipografia reflete a dignidade da pesquisa histórica, aliando o peso clássico da serifa em títulos à clareza funcional da sem serifa no corpo.

### 3.1 Famílias Tipográficas Homologadas

| Função | Família Declarada | Fallback Obrigatório | Finalidade |
| :--- | :--- | :--- | :--- |
| **Display / Títulos** | `'Libre Baskerville'` | `Georgia, 'Times New Roman', serif` | Cabeçalhos principais, títulos de seções, nomes de eventos |
| **Corpo & Interface** | `'Source Sans 3'` | `'Inter', -apple-system, sans-serif` | Texto corrido, botões, campos de entrada, metadados |
| **Código & Metadados** | `'JetBrains Mono'` | `'Fira Code', monospace` | Anos cronológicos, coordenadas, hashes SHA-256, páginas |

### 3.2 Escala Tipográfica Relativa (Base: 1rem = 16px)

| Nível | Seletor / Classe | Tamanho Relativo | Tamanho Equivalente | Altura da Linha (`line-height`) | Peso (`font-weight`) | Família |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Display / H1** | `h1, .text-display` | `2.125rem` | 34px | `1.20` | `700` (Bold) | Serif |
| **Seção Principal / H2** | `h2, .text-heading` | `1.500rem` | 24px | `1.30` | `700` (Bold) | Serif |
| **Subtítulo / H3** | `h3, .text-subheading`| `1.125rem` | 18px | `1.35` | `600` (SemiBold)| Sans |
| **Título de Bloco / H4** | `h4, .text-block` | `1.000rem` | 16px | `1.40` | `600` (SemiBold)| Sans |
| **Corpo Padrão** | `body, p, .text-body` | `0.9375rem`| 15px | `1.60` | `400` (Regular) | Sans |
| **Corpo Compacto / Meta**| `.text-meta` | `0.8125rem`| 13px | `1.45` | `400` / `500` | Sans |
| **Legenda / Carimbo** | `.text-stamp` | `0.6875rem`| 11px | `1.30` | `700` (Bold) | Sans (Caps) |
| **Monospace / Hashes** | `code, .text-mono` | `0.7500rem`| 12px | `1.50` | `400` / `500` | Mono |

### 3.3 Regras Rígidas de Pesos (`font-weight`)

* **Corpo de Texto**: Estritamente `400` (Regular). Proibido o uso de pesos ultraleves (`100`, `200`, `300`) que prejudicam a leitura contínua, bem como textos longos em negrito (`700`).
* **Ênfases Pontuais**: Uso moderado de `600` (SemiBold) para termos conceituais e nomes de fontes.
* **Pesos Pesados (`700`)**: Exclusivos para `h1`, `h2`, tags em caixa alta (uppercase) e números de destaque na barra estatística.

---

## 📏 4. Espaçamento e Grid (Métrica Base 4px / 8px)

Nenhum valor de espaçamento pode ser introduzido sem pertencer à progressão matemática estrita do sistema.

### 4.1 Escala de Espaçamento Modular

```css
:root {
    --space-1:  4px;   /* 0.25rem - Micro-espaçamentos (gaps entre ícone e texto inline) */
    --space-2:  8px;   /* 0.50rem - Espaçamento entre badges, chips e itens condensados */
    --space-3:  12px;  /* 0.75rem - Padding vertical de inputs e botões compactos */
    --space-4:  16px;  /* 1.00rem - Espaçamento padrão entre parágrafos e elementos irmãos */
    --space-5:  20px;  /* 1.25rem - Padding interno padrão de cards, dossiês e painéis */
    --space-6:  24px;  /* 1.50rem - Gap entre colunas do grid principal e margens laterais */
    --space-8:  32px;  /* 2.00rem - Separação vertical entre blocos de conteúdo */
    --space-12: 48px;  /* 3.00rem - Margem estrutural entre grandes seções editoriais */
    --space-16: 64px;  /* 4.00rem - Respiro do rodapé e áreas de encerramento */
}
```

### 4.2 Travamento do Contêiner e Proporções do Grid

1. **Largura Máxima Centralizada**:
   * O contêiner principal da aplicação é travado em `max-width: 1280px` (`80rem`) com `margin: 0 auto`.
   * **Proibição de Espalhamento**: Não permitir que o conteúdo se espalhe descontroladamente em monitores Ultrawide (2K, 4K), mantendo a proporção de página impressa.
   * **Margem de Segurança**: `padding-left: var(--space-6)` e `padding-right: var(--space-6)` em viewports menores que 1280px.
2. **Proporção Cartográfica Protagonista (Layout Split)**:
   * Na visualização do mapa com dossiê arquivístico, a distribuição de colunas é:
     * **Coluna Cartográfica (Mapa)**: `62%` a `65%` da largura útil.
     * **Coluna do Dossiê Arquivístico**: `35%` a `38%` da largura útil.
     * **Gap entre Colunas**: Fixo em `var(--space-6)` (24px).
3. **Preenchimento Interno (Padding) de Componentes Interativos**:
   * **Botão Primário / Ação**: `padding: var(--space-3) var(--space-5)` (12px vertical, 20px horizontal).
   * **Botão Secundário / Compacto**: `padding: var(--space-2) var(--space-4)` (8px vertical, 16px horizontal).
   * **Campos de Entrada (Input, Select)**: `padding: var(--space-2) var(--space-3)` (8px vertical, 12px horizontal).
   * **Cartão / Painel Arquivístico**: `padding: var(--space-5)` (20px em todos os lados).

---

## 🏛️ 5. Identidade dos Componentes, Bordas e Ícones

A identidade dos componentes rejeita a estética de aplicativo móvel moderno (cantos muito arredondados e sombras esfumaçadas) e adota um tratamento gráfico de **ficha catalográfica e instrumento cartográfico**.

### 5.1 Tratamento de Bordas e Raio (`border-radius`)

| Componente | Valor de Raio (`border-radius`) | Estilo e Espessura da Borda | Justificativa Visual |
| :--- | :--- | :--- | :--- |
| **Cartões e Dossiês** | `3px` | `1px solid var(--border-subtle)` | Canto sutilmente atenuado, lembrando papel cortado |
| **Botões e Inputs** | `3px` | `1px solid var(--border-strong)` | Superfície funcional nítida |
| **Tags / Badges de Postura**| `2px` | `1px solid [cor semântica]` | Formato retangular de carimbo arquivístico |
| **Blocos de Citação Literal**| `0px` (Reto) | `border-left: 3px solid var(--accent-action)` | Régua vertical tipográfica clássica |

> **🚫 PROIBIÇÃO ABSOLUTA**: É expressamente proibido o uso de `border-radius: 9999px` ou botões/etiquetas em formato de pílula (*pill badges*). Também é proibido qualquer raio superior a `4px`.

### 5.2 Eliminação de Sombras Esfumaçadas (Zero Névoa de IA)

* **Proibição de Sombras Gaussianas**: Proibido o uso de `box-shadow: 0 10px 25px rgba(...)`, sombras difusas ou gradientes sombreados.
* **Tratamento de Elevação Único**: O contraste de camadas é feito primordialmente através de **bordas sólidas finas** (`1px solid var(--border-subtle)`).
* **Sombra de Sobreposição Excepcional (Popovers e Dropdowns)**: Quando estritamente necessária para indicar elevação física, aplicar exclusivamente uma sombra curta, dura e utilitária:
  ```css
  box-shadow: 0 1px 2px rgba(28, 27, 24, 0.08), 0 2px 4px rgba(28, 27, 24, 0.04);
  ```

### 5.3 Padronização Iconográfica

* **Biblioteca Homologada Única**: **Lucide Icons** (em SVG vetorial puro ou componentes nativos correspondentes).
* **Espessura do Traço (`stroke-width`)**: Fixado rigidamente em **`1.75px`** em toda a interface. Proibido traços ultraleves de 1px ou grossos de 2.5px.
* **Dimensões Padronizadas**:
  * **Ícones Inline / Metadados / Botões**: `14px × 14px`.
  * **Ícones de Navegação e Ferramentas**: `18px × 18px`.
  * **Ícones de Cabeçalho / Destaque de Dossiê**: `20px × 20px`.
* **Banimento de Emojis Nativos**:
  * Emojis de sistema (🏠, 📊, 🗺️, ⏳, 📚, 🛠️, 🚀, 💡) estão **completamente banidos** de títulos, menus, navegações e rótulos de botões. Toda a navegação deve ser tipográfica, sóbria e institucional.

---

## 📋 6. Classes Utilitárias Homologadas (Referência Rápida)

Para manter a conformidade absoluta, o código HTML/CSS deve recorrer exclusivamente a estas classes:

```css
/* Layout & Contêiner */
.container-editorial   { max-width: 1280px; margin: 0 auto; padding: 0 var(--space-6); }
.grid-cartografico     { display: grid; grid-template-columns: 65% calc(35% - var(--space-6)); gap: var(--space-6); }

/* Fichas & Dossiês */
.card-dossie           { background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 3px; padding: var(--space-5); }
.card-dossie-header    { border-bottom: 1px solid var(--border-subtle); padding-bottom: var(--space-3); margin-bottom: var(--space-4); }

/* Citações Literais (Mandatório para proveniência histórica) */
.quote-literal         { border-left: 3px solid var(--accent-action); background-color: var(--bg-subtle); padding: var(--space-3) var(--space-4); margin: var(--space-3) 0; font-style: italic; font-size: 0.875rem; color: var(--text-primary); }

/* Carimbos Historiográficos (Posturas de Claim) */
.stamp-claim-apoia     { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; color: var(--status-success-text); background-color: var(--status-success-bg); border: 1px solid var(--status-success-border); border-radius: 2px; padding: 2px 6px; }
.stamp-claim-contesta  { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; color: var(--status-error-text); background-color: var(--status-error-bg); border: 1px solid var(--status-error-border); border-radius: 2px; padding: 2px 6px; }
.stamp-claim-matiza    { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; color: var(--status-warning-text); background-color: var(--status-warning-bg); border: 1px solid var(--status-warning-border); border-radius: 2px; padding: 2px 6px; }

/* Barra Estatística Editorial */
.stats-band-editorial  { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-4); padding: var(--space-2) 0; border-top: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle); font-size: 0.875rem; color: var(--text-secondary); }
.stats-band-editorial b{ font-family: 'JetBrains Mono', monospace; color: var(--accent-action); font-size: 1.000rem; }
```

---

## 🔒 7. Critérios de Rejeição Imediata em Code Review

Qualquer submissão de código ou sugestão gerada pela IA será **sumariamente rejeitada** se contiver:

1. `background: #0B1120`, `#0F172A` ou qualquer tema escuro não solicitado.
2. `color: #38BDF8` ou qualquer tom de azul/ciano neon.
3. Gradientes decorativos (`linear-gradient(...)` ou `radial-gradient(...)`).
4. Cantos em pílula (`border-radius: 9999px` ou `border-radius: 50px`).
5. Sombras difusas (`box-shadow: 0 10px 30px ...`).
6. Emojis usados como ícones de navegação ou marcadores de lista.
7. Cards flutuantes de métrica ("KPI Cards") isolados.
8. Fontes de display diferentes de `Libre Baskerville`.
9. Espaçamentos arbitrários fora da escala de 4px/8px.
