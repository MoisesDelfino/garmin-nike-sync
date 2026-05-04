# 🔌 Nike Token Extractor - Extensão do Navegador

Extensão para Chrome/Edge/Brave que extrai automaticamente o token de acesso do Nike Run Club.

## 📥 Instalação

### Chrome/Edge/Brave (Modo Desenvolvedor)

1. **Abra as extensões:**
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
   - Brave: `brave://extensions/`

2. **Ative o Modo Desenvolvedor** (canto superior direito)

3. **Clique em "Carregar sem compactação"**

4. **Selecione a pasta `browser-extension`**

5. **Pronto!** A extensão aparecerá na barra de ferramentas

### Firefox

1. Abra `about:debugging#/runtime/this-firefox`
2. Clique em "Carregar extensão temporária"
3. Selecione o arquivo `manifest.json` da pasta `browser-extension`

## 🎯 Como Usar

### Passo 1: Faça login no Nike.com
- Acesse [nike.com](https://www.nike.com)
- Faça login com sua conta Nike

### Passo 2: Extraia o token
- Clique no ícone da extensão na barra de ferramentas
- Clique em **"Extrair Token"**
- O token será exibido automaticamente

### Passo 3: Copie e use
- Clique em **"Copiar"**
- Cole o token no aplicativo Garmin-Nike Sync
- Pronto! Suas sincronizações estão configuradas

## 🔒 Segurança

- ✅ A extensão **NÃO envia** seus dados para nenhum servidor
- ✅ O token fica armazenado **apenas localmente** no seu navegador
- ✅ Você tem controle total sobre quando extrair e usar o token
- ✅ Código aberto - você pode auditar todo o código

## 🛠️ Troubleshooting

### "Token não encontrado"
- Certifique-se de estar **logado** no Nike.com
- Tente acessar [nike.com/membership](https://www.nike.com/membership)
- Faça logout e login novamente

### Extensão não aparece
- Verifique se o **Modo Desenvolvedor** está ativado
- Tente recarregar a extensão nas configurações

### Token expira rápido
- Tokens Nike geralmente duram 3-6 meses
- Quando expirar, simplesmente extraia um novo

## 📝 Notas Técnicas

### Onde o token é armazenado?

A extensão procura o token em (em ordem):
1. Cookies do domínio `.nike.com`
2. `localStorage` da página
3. `sessionStorage` da página
4. Variáveis globais do JavaScript

### Compatibilidade

- ✅ Chrome 88+
- ✅ Edge 88+
- ✅ Brave
- ✅ Firefox 109+
- ✅ Opera 74+

## 🎨 Ícones Necessários

A extensão precisa de ícones PNG nas seguintes dimensões:
- `icons/icon16.png` (16x16)
- `icons/icon48.png` (48x48)
- `icons/icon128.png` (128x128)

### Gerar ícones automaticamente:

Use um serviço como [favicon.io](https://favicon.io) ou crie com este emoji: ⚡

Ou use este comando para criar ícones temporários:
```bash
# Requer ImageMagick
convert -size 16x16 xc:purple icons/icon16.png
convert -size 48x48 xc:purple icons/icon48.png
convert -size 128x128 xc:purple icons/icon128.png
```

## 🔄 Atualizações

Para atualizar a extensão:
1. Baixe a nova versão
2. Vá em extensões (`chrome://extensions/`)
3. Clique em ⟳ (recarregar) na extensão

## 📄 Licença

MIT License - Use livremente!

## 🤝 Contribuindo

Encontrou um bug? Tem uma sugestão?
- Abra uma issue no GitHub
- Ou envie um PR com melhorias

---

**Made with ❤️ for runners** 🏃‍♂️
