# EYXO Design System (Guidelines para IAs e Devs)

Este documento atua como a fonte da verdade (Source of Truth) para o padrão visual e de desenvolvimento de interfaces digitais da EYXO. Toda nova tela, componente, plugin ou sistema web deve obrigatoriamente seguir estas regras para garantir total consistência.

## 1. Cores (Color Palette)
O tema padrão dos sistemas é **Dark Mode**.
- **Fundo Principal (Background):** `#000000` (Preto absoluto) -> `var(--eyxo-bg)`
- **Superfície / Cartões (Surface):** `#0A0A0A` (Cinza super escuro, quase preto) -> `var(--eyxo-surface)`
- **Hover de Superfície:** `#141414` -> `var(--eyxo-surface-hover)`
- **Bordas / Linhas Separadoras:** `#1F1F1F` -> `var(--eyxo-border)`
- **Texto Principal:** `#FFFFFF` (Branco puro) -> `var(--eyxo-text)`
- **Texto Secundário (Muted):** `#8F8F8F` (Cinza claro) -> `var(--eyxo-text-muted)`
- **Cor de Ação (Primary Brand):** `#0000FF` (Azul puro) -> `var(--eyxo-blue)`
- **Hover de Ação (Primary Hover):** `#0000D1`

## 2. Tipografia
A tipografia deve transmitir robustez, precisão técnica e modernidade.

- **Fonte Principal (UI / Textos):** `'Moderat', 'Helvetica Neue', Helvetica, Arial, sans-serif`
- **Fonte Monospace (Números, Inputs numéricos e Código):** `'Moderat Mono', 'Courier New', Courier, monospace`

### Hierarquia:
- **Títulos (H1/H2):** Negrito (`font-weight: 700`), sem margem superior, margem inferior curta (`5px` a `15px`). O kerning deve ser levemente apertado (`letter-spacing: -0.5px`).
- **Parágrafos:** Cinza (`--eyxo-text-muted`), peso normal (`400`), tamanho amigável (ex: `14px` ou `15px`), espaçamento entre linhas confortável (`line-height: 1.5`).

## 3. Componentes Visuais

### Botões Primários (Ações Principais)
- **Background:** `--eyxo-blue` (`#0000FF`)
- **Texto:** Branco (`#FFFFFF`)
- **Tipografia:** CAIXA ALTA (`text-transform: uppercase`), Negrito (`font-weight: 700`), Letras espaçadas (`letter-spacing: 1px`).
- **Formato:** Bordas não exageradas (`border-radius: 8px` ou `10px`). Sem bordas (`border: none`).
- **Tamanho:** Padding confortável (`padding: 12px` a `16px`).
- **Transição:** Suave no hover (`transition: all 0.2s`).
- **Estado Desabilitado:** Fundo `#333`, texto `#777`, sem cursor (`cursor: not-allowed`).

### Botões Secundários (Ações de Suporte)
- **Background:** Transparente (ou `--eyxo-text`)
- **Texto:** `--eyxo-text` (ou `--eyxo-bg` se fundo for branco)
- **Borda:** Opcional (se transparente, usar `--eyxo-border`).
- Mantém caixa alta e espaçamento.

### Inputs (Campos de Texto/Número)
- **Background:** `--eyxo-surface` (`#0A0A0A`)
- **Texto:** `--eyxo-text` (`#FFFFFF`). Para campos de peso/número, **sempre usar fonte Monospace**.
- **Formato:** Borda de `1px solid var(--eyxo-border)`. Cantos levemente arredondados (`border-radius: 6px` a `10px`).
- **Foco (Focus):** Borda fica azul (`border-color: var(--eyxo-blue)`), sem aquele glow azul padrão do navegador (`outline: none`).

### Caixas de Item (File/Item Lists)
- Fundo no tom `--eyxo-surface`, contornado por `--eyxo-border`.
- **Preenchimento:** Padding interno em torno de `10px 12px`.
- **Disposição:** Flexbox (`display: flex`), alinhando elementos verticalmente no centro e separados adequadamente.

## 4. Loader (Estado de Carregamento)
O padrão de carregamento da EYXO **NÃO** usa barras de progresso ou spinners genéricos.
- **Spinner Oficial:** Um círculo vazado de tamanho pequeno/médio (`24px` a `30px`).
- **Cor do Anel:** `3px solid var(--eyxo-border)`.
- **Ponta animada:** `border-top: 3px solid var(--eyxo-blue)`.
- **Animação:** Linear ou Cubic-Bezier suave rodando em `1s`.

## 5. Instruções Adicionais
- Evitar sombras exageradas (box-shadow) a menos que seja para um botão de destaque ou modal sobreposto, para manter um estilo *flat* e brutalista sofisticado.
- Os paddings e margins de container devem usar escala de 4/8 (ex: `8px`, `16px`, `24px`, `32px`).
