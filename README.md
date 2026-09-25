# KA Compressor (GIF Edition)

Ferramenta interna da EYXO para compressão de GIFs utilizando otimização avançada com limite de KB (Busca Binária via `gifsicle`).

## Como rodar localmente
1. Instale as dependências de sistema: `brew install gifsicle`
2. Instale as dependências Python: `pip install flask werkzeug`
3. Execute o app: `python app.py`

## Últimas Atualizações (Changelog)
- **v2.7.0** - Segurança Avançada: Proteção contra Path Traversal, nomes de arquivo imprevisíveis (UUID), limite de 50MB, validação de extensão .gif e autolimpeza (1 hora) na pasta outputs.
- **v2.6.2** - GitHub Ignore: Adicionado `.gitignore` e removidas as pastas `PARA TESTE/` e `backups/` do versionamento do GitHub.
- **v2.6.1** - Script de Atualização: Adicionado script `Atualizar.command` para facilitar envios rápidos para o GitHub e inicializado repositório git.
