#!/bin/bash
# Script para criar ícones temporários usando apenas ferramentas padrão

# Verifica se ImageMagick está disponível
if command -v convert &> /dev/null; then
    echo "✓ ImageMagick encontrado, gerando ícones..."
    cd "$(dirname "$0")/icons"
    
    # Converte SVG para PNG
    convert icon.svg -resize 16x16 icon16.png
    convert icon.svg -resize 48x48 icon48.png
    convert icon.svg -resize 128x128 icon128.png
    
    echo "✅ Ícones gerados com sucesso!"
    ls -lh *.png
    
elif python3 -c "from PIL import Image" 2>/dev/null; then
    echo "✓ Python Pillow encontrado, gerando ícones..."
    cd "$(dirname "$0")"
    python3 generate_icons.py
    
else
    echo "⚠️  Nenhuma ferramenta de geração de imagem encontrada."
    echo ""
    echo "Por favor, escolha uma opção:"
    echo ""
    echo "1. Instalar ImageMagick:"
    echo "   Ubuntu/Debian: sudo apt install imagemagick"
    echo "   macOS: brew install imagemagick"
    echo ""
    echo "2. Instalar Pillow:"
    echo "   pip install pillow"
    echo ""
    echo "3. Gerar online (recomendado):"
    echo "   Acesse: https://favicon.io/favicon-generator/"
    echo "   Configure com emoji ⚡ e baixe os ícones"
    echo ""
    echo "4. Usar ícones temporários simples (funciona, mas não fica bonito):"
    echo "   Rode: ./create_simple_icons.sh"
    echo ""
    echo "📖 Veja ICONS-GUIDE.md para mais detalhes"
fi
