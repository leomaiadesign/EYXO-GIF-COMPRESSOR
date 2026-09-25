#!/bin/bash

# Pega a pasta atual onde o script está salvo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "  Iniciando Servidor - GIF Compressor"
echo "=========================================="
echo "O servidor está rodando. Para desligar, basta fechar esta janela."
echo "Abrindo o navegador..."

# Aguarda 2 segundos e abre o navegador em background
(sleep 2 && open "http://127.0.0.1:5001") &

# Inicia o servidor Python
python3 app.py
