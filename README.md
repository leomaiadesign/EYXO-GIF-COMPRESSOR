# KA Compressor (GIF Edition)

Ferramenta interna da EYXO para compressão de GIFs utilizando otimização avançada com limite de KB (Busca Binária via `gifsicle`).

## Como rodar localmente
1. Dê um duplo clique no arquivo **`Iniciar_Servidor.command`** na pasta do projeto. Ele abrirá o terminal e o navegador automaticamente.

*(Se preferir via terminal)*:
1. Instale as dependências de sistema: `brew install gifsicle`
2. Instale as dependências Python: `pip install flask werkzeug numpy`
3. Execute o app: `python app.py`

## Últimas Atualizações (Changelog)
- **v2.8.8** - UI Design System: Ajuste visual do feedback em tempo real para respeitar o Design System.
- **v2.8.7** - Correção de Interface (Hotfix): Solucionado um erro de Javascript (FormData Undefined).
