---
name: design-system-rules
description: Regras mandatórias e invioláveis do Design System Atlas Editorial para qualquer modificação na interface visual.
always_on: true
---

# REGRAS OPERACIONAIS ESTRITAS DO DESIGN SYSTEM (ATLAS EDITORIAL)

> **AVISO À IA**: Você atua estritamente como executora determinística do Design System deste projeto. Está **PROIBIDA** de exercer criatividade estética, inventar cores, fontes, espaçamentos ou usar emojis na interface.

Consulte o documento normativo completo em: [docs/design_system.md](file:///C:/Users/dani/Documents/Daniel%20Systems/docs/design_system.md).

## 1. Cores Proibidas e Autorizadas
* **PROIBIDO**: Temas escuros (`#0B1120`, `#0F172A`), azul/ciano neon (`#38BDF8`), gradientes radiais/lineares.
* **Fundo Principal**: `#F5F3EE` (Papel pergaminho/arquivo).
* **Fundo de Cartões / Dossiê**: `#FFFFFF`.
* **Fundo Secundário / Sidebar**: `#EBE7DF`.
* **Bordas**: `#D8D3C9` (sólida, 1px).
* **Texto Primário**: `#1C1B18` (Grafite carvão, alto contraste).
* **Texto Secundário**: `#5A564F`.
* **Destaque / Ação Exclusiva**: `#7A2E2E` (Vinho clássico, restrito a botões de ação e tabs ativas. PROIBIDO em fundos de cards ou banners).

## 2. Tipografia Homologada
* **Títulos (H1, H2)**: `'Libre Baskerville', Georgia, serif; font-weight: 700;`
* **Corpo e Interface**: `'Source Sans 3', -apple-system, sans-serif; font-weight: 400;` (Proibido corpo ultraleve < 400 ou excessivamente pesado > 500).
* **Códigos, Anos, Hashes e Páginas**: `'JetBrains Mono', monospace; font-weight: 400;`

## 3. Métrica de Espaçamento e Grid
* Múltiplos estritos de 4px e 8px: `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`, `48px`.
* Largura máxima do contêiner: `1280px` (`max-width: 1280px; margin: 0 auto;`).

## 4. Componentes, Bordas e Ícones
* **Bordas**: Finas, sólidas e nítidas (`1px solid #D8D3C9`).
* **Raio de Borda (`border-radius`)**: `3px` para cards/inputs; `2px` para carimbos de postura; `0px` para réguas verticais de citação.
* **PROIBIDO**: Cantos em formato de pílula (`border-radius: 9999px`) e raios > 4px.
* **PROIBIDO**: Sombras esfumaçadas gaussianas (`box-shadow: 0 10px 25px ...`).
* **Ícones**: Lucide Icons com traço fixo em `1.75px`.
* **PROIBIÇÃO TOTAL DE EMOJIS**: Emojis nativos (🏠, 📊, 🗺️, ⏳, 📚, 🛠️, etc.) estão expressamente banidos de títulos, menus e botões.
