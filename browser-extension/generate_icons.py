#!/usr/bin/env python3
"""
Gera ícones para a extensão do navegador
Requer: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Cria um ícone com o símbolo de raio"""
    # Cria imagem com fundo gradiente roxo
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # Desenha círculo de fundo
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#764ba2')
    
    # Tenta adicionar emoji (se falhar, usa texto)
    try:
        # Emoji de raio
        font_size = int(size * 0.6)
        text = "⚡"
        
        # Tenta diferentes fontes
        font = None
        for font_name in ['Arial', 'DejaVuSans', 'FreeSans']:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                pass
        
        if font is None:
            font = ImageFont.load_default()
        
        # Centraliza o texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        draw.text((x, y), text, fill='white', font=font)
    except Exception as e:
        print(f"Aviso ao adicionar emoji: {e}")
        # Fallback: desenha um raio simples
        draw.polygon([
            (size*0.55, size*0.2),
            (size*0.35, size*0.5),
            (size*0.45, size*0.5),
            (size*0.3, size*0.8),
            (size*0.5, size*0.55),
            (size*0.4, size*0.55)
        ], fill='white')
    
    img.save(output_path, 'PNG')
    print(f"✓ Criado: {output_path} ({size}x{size})")

def main():
    # Cria diretório de ícones
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Gera ícones em diferentes tamanhos
    sizes = {
        'icon16.png': 16,
        'icon48.png': 48,
        'icon128.png': 128
    }
    
    print("🎨 Gerando ícones da extensão...")
    
    for filename, size in sizes.items():
        output_path = os.path.join(icons_dir, filename)
        create_icon(size, output_path)
    
    print("\n✅ Todos os ícones foram gerados com sucesso!")
    print(f"📁 Localização: {icons_dir}")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("❌ Erro: Pillow não está instalado")
        print("Execute: pip install pillow")
    except Exception as e:
        print(f"❌ Erro: {e}")
