# Regras do Projeto: KA Compressor

## Versionamento Automático (SemVer)
Sempre que você (Gemini/Antigravity) realizar qualquer alteração nos arquivos de código deste projeto (especialmente `app.py` ou `templates/index.html`), você **DEVE** atualizar automaticamente a versão do projeto.

Onde encontrar:
- A versão atual fica localizada no final do arquivo `templates/index.html`, dentro de uma `<div class="mono-font" ...>vX.Y.Z</div>`.

Como atualizar (vX.Y.Z):
Ao final de cada pedido, avalie a complexidade e o impacto das mudanças feitas e pondere qual dígito alterar:
- **X (Major / Primeiro Dígito):** Mude este número apenas quando houver mudanças drásticas na arquitetura ou refatorações completas que alterem todo o fluxo de uso da ferramenta (Ex: `v4.1.2` -> `v5.0.0`).
- **Y (Minor / Segundo Dígito):** Mude este número para novas funcionalidades claras e adições de comportamento (Ex: `v4.1.2` -> `v4.2.0`).
- **Z (Patch / Terceiro Dígito):** Mude este número para pequenos ajustes visuais (CSS), correções de bugs rápidos, pequenos ajustes de margem/cor, etc (Ex: `v4.1.2` -> `v4.1.3`).

Você não precisa pedir permissão ao usuário para fazer essa alteração de versão, apenas inclua o bump de versão silenciosamente junto com a sua edição de código, e avise no resumo da resposta.

## Changelog Automático no README
Além de atualizar o `index.html`, sempre que você (Gemini/Antigravity) finalizar uma alteração no código que resulte em uma mudança de versão, você **DEVE** atualizar o arquivo `README.md`.
Na seção "Últimas Atualizações (Changelog)" do `README.md`, adicione uma linha no formato:
`- **vX.Y.Z** - Resumo curto e direto da alteração feita.`
Mantenha sempre **apenas as 3 últimas atualizações** na lista (apague as mais antigas para não poluir o arquivo).
