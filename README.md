# KA Compressor (GIF Edition)

Ferramenta interna da EYXO para compressão de GIFs utilizando otimização avançada com limite de KB (Busca Binária via `gifsicle`).

## Como rodar localmente
1. Instale as dependências de sistema: `brew install gifsicle`
2. Instale as dependências Python: `pip install flask werkzeug`
3. Execute o app: `python app.py`

## Últimas Atualizações (Changelog)
- **v2.5.12** - GitHub Ignore: Adicionado `.gitignore` e removidas as pastas `PARA TESTE/` e `backups/` do versionamento do GitHub.
- **v2.5.11** - Script de Atualização: Adicionado script `Atualizar.command` para facilitar envios rápidos para o GitHub e inicializado repositório git.
- **v2.5.10** - Organização de Arquivos: Limpeza da raiz do projeto movendo scripts temporários, documentação e backups para pastas dedicadas (`dev_scripts/`, `docs/` e `backups/`) para melhorar a organização sem afetar o funcionamento do app.
