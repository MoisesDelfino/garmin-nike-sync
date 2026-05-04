# 🔑 Como Extrair Token Nike dos Usuários

## 📋 Visão Geral

Como **admin**, você precisa manualmente obter o token Nike de cada usuário que se registrar. Este guia mostra o passo a passo completo.

---

## 🎯 Processo Completo (5-10 minutos por usuário)

### **Passo 1: Acesse o Painel Admin**

1. Faça login no sistema
2. Clique no link **"Admin"** (amarelo) no menu superior
3. Ou acesse diretamente: `https://garmin-nike-sync.onrender.com/admin`

Você verá 3 seções:
- 🟡 **Usuários Pendentes** (precisam configuração)
- 🟢 **Usuários Ativos** (funcionando)
- 🔴 **Usuários com Erro** (credenciais inválidas)

---

### **Passo 2: Selecione Usuário Pendente**

1. Na seção **"Usuários Pendentes"**
2. Clique no botão **"Configurar Nike"** do usuário

Você será levado para a página de detalhes do usuário.

---

### **Passo 3: Copie as Credenciais Nike**

Na página do usuário, você verá:

```
┌─────────────────────────────────────┐
│ Credenciais Nike do Usuário         │
├─────────────────────────────────────┤
│ Email: usuario@email.com      [📋]  │
│ Senha: senhaDoUsuario123      [📋]  │
└─────────────────────────────────────┘
```

1. Clique no botão **📋** ao lado do **Email** para copiar
2. Clique no botão **📋** ao lado da **Senha** para copiar

---

### **Passo 4: Faça Login no Nike.com**

1. Clique no botão **"🌐 Abrir Nike.com"**
   - Abre uma nova aba em: `https://www.nike.com/login`

2. **Cole as credenciais** que você copiou:
   - Email: `Ctrl+V` (ou `Cmd+V` no Mac)
   - Senha: `Ctrl+V` (ou `Cmd+V` no Mac)

3. Clique em **"Sign In"**

4. ⚠️ **Se der erro de credenciais inválidas:**
   - Volte para a página do admin
   - Clique em **"Marcar como Erro"**
   - Digite mensagem: "Credenciais Nike inválidas. Verifique seu email e senha."
   - O usuário verá alerta vermelho no dashboard
   - **Pare aqui** e vá para o próximo usuário

---

### **Passo 5: Extraia o Token**

Se o login funcionou, agora você precisa extrair o token:

#### **Método 1: Console do Navegador (Mais fácil)**

1. **Abra o Console** do navegador:
   - **Chrome/Edge/Brave**: Pressione `F12` ou `Ctrl+Shift+J` (Windows/Linux) ou `Cmd+Option+J` (Mac)
   - **Firefox**: Pressione `F12` ou `Ctrl+Shift+K` (Windows/Linux) ou `Cmd+Option+K` (Mac)
   - **Safari**: Pressione `Cmd+Option+C`

2. Clique na aba **"Console"** (se não estiver selecionada)

3. **Cole este comando** e pressione Enter:
   ```javascript
   localStorage.getItem('access_token')
   ```

4. O token aparecerá assim (exemplo):
   ```
   "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJleHAiOjE3NDY..."
   ```

5. **Copie APENAS o conteúdo entre as aspas** (sem as aspas):
   ```
   eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJleHAiOjE3NDY...
   ```

6. ✅ **Pronto!** Você tem o token.

#### **Método 2: Application/Storage (Alternativo)**

1. Pressione `F12` para abrir Developer Tools

2. Clique na aba **"Application"** (Chrome) ou **"Storage"** (Firefox)

3. No menu lateral esquerdo:
   - Expanda **"Local Storage"**
   - Clique em `https://www.nike.com`

4. Procure pela chave **`access_token`**

5. Copie o **valor** (coluna da direita)

---

### **Passo 6: Insira o Token no Sistema**

1. **Volte para a aba do admin** (página de detalhes do usuário)

2. Encontre o campo **"Token Nike"**:
   ```
   ┌─────────────────────────────────────┐
   │ Token Nike                          │
   │ [                                  ]│
   │                                     │
   │  (Cole o token aqui)                │
   └─────────────────────────────────────┘
   ```

3. **Cole o token** (`Ctrl+V` ou `Cmd+V`)

4. Clique no botão verde **"✓ Ativar Nike"**

5. ✅ **Pronto!** Você verá mensagem de sucesso:
   ```
   ✓ Token Nike configurado com sucesso!
   ```

---

### **Passo 7: Usuário é Notificado Automaticamente**

O usuário verá no dashboard dele:

```
┌─────────────────────────────────────────────┐
│ ✓ Nike Run Club ativo!                      │
│ Seu Nike foi configurado em XX/XX/XXXX.     │
│ A sincronização automática está funcionando.│
└─────────────────────────────────────────────┘
```

E a sincronização automática começará a funcionar! 🎉

---

## 🎬 Demonstração Visual

```
ADMIN                                    NIKE.COM
┌──────────────────┐                   ┌──────────────────┐
│ 1. Ver pendente  │                   │                  │
│ 2. Copiar creds  │──────────────────>│ 3. Fazer login   │
│                  │                   │                  │
│                  │<──────────────────│ 4. Extrair token │
│                  │    (token)        │    (F12 console) │
│ 5. Colar token   │                   │                  │
│ 6. Ativar ✓      │                   └──────────────────┘
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ USUÁRIO          │
│ Vê notificação ✓ │
│ Sync automático! │
└──────────────────┘
```

---

## ⚡ Dicas Rápidas

### Atalhos Úteis

- **Copiar credenciais**: Clique nos botões 📋
- **Abrir console**: `F12` → aba "Console"
- **Copiar token**: Selecione o texto entre aspas, `Ctrl+C`
- **Colar no admin**: `Ctrl+V` no campo "Token Nike"

### Se Algo Der Errado

**❌ "Credenciais inválidas" no Nike.com**
- Marque como erro no admin
- Usuário receberá notificação para atualizar

**❌ Token não aparece no localStorage**
- Certifique-se de que fez login com sucesso
- Tente fazer logout e login novamente
- Verifique se está em `https://www.nike.com` (não `.com.br`)

**❌ Token inválido/expirado**
- Extraia um novo token
- Cole no campo e clique "Ativar Nike" novamente

---

## 📊 Tempo Estimado

- **Primeiro token**: ~10 minutos (aprendendo o processo)
- **Tokens seguintes**: ~3-5 minutos cada
- **Com prática**: ~2 minutos por usuário

---

## 🔐 Segurança

✅ **Boas Práticas:**
- Use navegador em modo anônimo/privado
- Limpe cache após cada configuração
- Nunca salve as credenciais dos usuários
- Feche todas as abas após copiar o token

⚠️ **IMPORTANTE:**
- Os tokens são criptografados no banco (AES-256)
- Você não verá os tokens após inserir
- Credenciais são usadas apenas para extração
- Faça logout do Nike.com após cada configuração

---

## 🎯 Checklist Por Usuário

- [ ] Acessar /admin
- [ ] Clicar "Configurar Nike"
- [ ] Copiar email Nike
- [ ] Copiar senha Nike
- [ ] Abrir Nike.com
- [ ] Fazer login
- [ ] Abrir console (F12)
- [ ] Executar: `localStorage.getItem('access_token')`
- [ ] Copiar token (sem aspas)
- [ ] Voltar para admin
- [ ] Colar token
- [ ] Clicar "Ativar Nike"
- [ ] ✅ Confirmar mensagem de sucesso
- [ ] Fazer logout do Nike.com
- [ ] Limpar navegador

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| Token com aspas | Remova as aspas antes de colar |
| Token muito curto | Certifique-se de copiar completo |
| "Já existe admin" na /setup | Você já é admin, faça login |
| Não vê link "Admin" | Você não é admin ainda, use /setup |
| Usuário não aparece pendente | Ele não forneceu credenciais Nike |
| Console não abre | Tente Ctrl+Shift+J ou F12 |

---

## 📞 Quando Pedir Ajuda

Se após 3 tentativas o token não funcionar:
1. Peça ao usuário para verificar credenciais
2. Tente com outro navegador
3. Verifique os logs do Render por erros

---

**Agora você está pronto para configurar tokens Nike!** 🚀

Qualquer dúvida, consulte este guia ou os logs do sistema.
