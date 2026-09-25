#!/bin/bash

# Pega a pasta atual onde o script está salvo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "  Subindo atualizações para o GitHub..."
echo "=========================================="

# 1. Adiciona todas as modificações
git add .

# 2. Registra a atualização com a hora atual
DATA=$(date +"%d/%m/%Y %H:%M")
git commit -m "Atualização - $DATA"

# Pequena pausa para sincronização (ex: Google Drive)
sleep 3

# 3. Envia para o GitHub
git push origin main

echo "=========================================="
echo "✅ SUCESSO! Código enviado para o GitHub."
echo "=========================================="
echo ""
echo "Você pode fechar esta janela."
