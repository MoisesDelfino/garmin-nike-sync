# 🎨 Como Gerar os Ícones da Extensão

A extensão precisa de 3 ícones PNG. Escolha uma das opções abaixo:

## Opção 1: Online (Mais Fácil) ⭐

### Usando CloudConvert (Gratuito)

1. Acesse: https://cloudconvert.com/svg-to-png
2. Faça upload do arquivo `icon.svg`
3. Configure cada tamanho:
   - **16x16** → Salve como `icon16.png`
   - **48x48** → Salve como `icon48.png`
   - **128x128** → Salve como `icon128.png`
4. Coloque todos os arquivos na pasta `icons/`

### Usando Favicon.io (Recomendado)

1. Acesse: https://favicon.io/favicon-generator/
2. Configure:
   - **Text:** ⚡ (ou use letra N)
   - **Background:** `Linear gradient` (roxo para roxo escuro)
   - **Font:** Escolha uma fonte moderna
3. Clique em **"Download"**
4. Extraia e renomeie os arquivos para a pasta `icons/`:
   - `favicon-16x16.png` → `icon16.png`
   - `favicon-32x32.png` → (ignore)
   - `android-chrome-192x192.png` → redimensione para 48x48 e 128x128

## Opção 2: Comando ImageMagick (Linux/Mac)

Se você tem ImageMagick instalado:

```bash
cd browser-extension/icons

# Converte SVG para PNG em diferentes tamanhos
convert icon.svg -resize 16x16 icon16.png
convert icon.svg -resize 48x48 icon48.png
convert icon.svg -resize 128x128 icon128.png
```

## Opção 3: Python com Pillow

```bash
# Instalar Pillow
pip install pillow

# Executar gerador
cd browser-extension
python3 generate_icons.py
```

## Opção 4: Ícones Temporários (Para Testes)

Crie arquivos PNG simples de cor sólida:

```bash
cd browser-extension/icons

# Usando ImageMagick
convert -size 16x16 xc:'#667eea' icon16.png
convert -size 48x48 xc:'#667eea' icon48.png
convert -size 128x128 xc:'#667eea' icon128.png

# Ou usando Python
python3 -c "from PIL import Image; [Image.new('RGB', (s,s), '#667eea').save(f'icon{s}.png') for s in [16,48,128]]"
```

## ✅ Verificação

Após gerar os ícones, você deve ter:
```
browser-extension/
├── icons/
│   ├── icon16.png   ✓
│   ├── icon48.png   ✓
│   └── icon128.png  ✓
```

## 🎨 Design Recomendado

- **Cores:** Gradiente roxo (#667eea → #764ba2)
- **Símbolo:** Raio ⚡ ou logo Nike
- **Estilo:** Moderno, flat design
- **Formato:** PNG com fundo transparente ou colorido

---

**Dica:** A extensão funciona mesmo com ícones simples/temporários. Você pode melhorar o design depois! 🚀
