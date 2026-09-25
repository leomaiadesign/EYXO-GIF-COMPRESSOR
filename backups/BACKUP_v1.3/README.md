# KA Compressor (GIF Edition)

Ferramenta interna da EYXO para compressão de GIFs utilizando otimização avançada com limite de KB (Busca Binária via `gifsicle`).

## Como rodar localmente
1. Instale as dependências de sistema: `brew install gifsicle`
2. Instale as dependências Python: `pip install flask werkzeug`
3. Execute o app: `python app.py`

## Últimas Atualizações (Changelog)
- **v1.3.0** - Lançamento da "Magia": Motor `gifski` de altíssima qualidade com decimação inteligente de frames (FPS) e dropdown de seleção de modo pelo usuário.
- **v1.2.0** - Adicionado suporte a Redução de Escala (Resize) opcional para evitar banding e garantir o cumprimento de metas de KB agressivas.
- **v1.1.0** - Adicionado preview dinâmico de GIFs (original e resultado), correção de layout (overflow e versionamento) e melhorias visuais no botão de download.
