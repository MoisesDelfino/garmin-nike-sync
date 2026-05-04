# 🚀 Guia Rápido de Instalação - Nike Token Extractor

## ⚡ Instalação em 3 Passos

### 1️⃣ Gerar os Ícones (Escolha uma opção)

#### Opção A: Online - Favicon.io (Mais Fácil) ⭐
1. Acesse: https://favicon.io/favicon-generator/
2. Configure:
   - **Text:** ⚡
   - **Shape:** Circle
   - **Font:** Bold
   - **Background:** Gradient
   - **Cor 1:** `#667eea`
   - **Cor 2:** `#764ba2`
3. Clique em **"Download"**
4. Extraia o ZIP e renomeie os arquivos:
   ```
   favicon-16x16.png → icon16.png
   favicon-32x32.png → icon48.png (redimensione)
   android-chrome-192x192.png → icon128.png (redimensione)
   ```
5. Coloque na pasta `browser-extension/icons/`

#### Opção B: Instalar ImageMagick
```bash
# Ubuntu/Debian
sudo apt install imagemagick

# Execute o script
cd browser-extension
./create_icons.sh
```

### 2️⃣ Instalar a Extensão no Chrome

1. Abra o Chrome e acesse: `chrome://extensions/`

2. Ative o **"Modo do desenvolvedor"** (canto superior direito)

3. Clique em **"Carregar sem compactação"**

4. Selecione a pasta:
   ```
   garmin-nike-sync/browser-extension/
   ```

5. ✅ A extensão aparecerá na lista!

### 3️⃣ Usar a Extensão

1. **Faça login no Nike.com:**
   - Acesse https://www.nike.com
   - Clique em "Entrar" e faça login

2. **Extraia o token:**
   - Clique no ícone da extensão (⚡) na barra de ferramentas
   - Clique em **"Extrair Token"**
   - O token será exibido automaticamente

3. **Copie e use:**
   - Clique em **"Copiar"**
   - Acesse https://garmin-nike-sync.onrender.com
   - Vá em **"Credenciais"**
   - Cole o token no campo **"Nike Access Token"**
   - Clique em **"Salvar Credenciais"**

## 🎉 Pronto!

Agora você pode sincronizar seus treinos do Garmin para o Nike automaticamente!

---

## 🔧 Troubleshooting

### Extensão não carrega
- Verifique se os ícones estão na pasta `icons/`
- Se não tiver ícones, use a Opção A acima para gerá-los

### "Token não encontrado"
- Certifique-se de estar **logado** no Nike.com
- Tente acessar https://www.nike.com/membership primeiro
- Faça logout e login novamente

### Token copiado mas não funciona
- O token pode ter expirado
- Extraia um novo token
- Tokens geralmente duram 3-6 meses

---

## 📚 Mais Informações

- **README completo:** [README.md](README.md)
- **Guia de ícones:** [ICONS-GUIDE.md](ICONS-GUIDE.md)
- **Aplicação web:** https://garmin-nike-sync.onrender.com

---

**Dúvidas?** Entre em contato! 💬
