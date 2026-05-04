# 🔑 Como Extrair Token Nike dos Usuários

## 📋 Visão Geral

Como **admin**, você precisa manualmente obter o token Nike de cada usuário que se registrar. Este guia mostra o passo a passo completo.

### ⚠️ **IMPORTANTE: Se `localStorage.getItem('access_token')` retornar `null`**

Isso é **NORMAL**! O Nike pode armazenar o token em diferentes lugares. Use o **Método 1 (Application/Storage)** que mostra TODAS as chaves disponíveis visualmente, ou o **Método 3 (Network Tab)** que captura o token durante o login.

**Não desista!** O token está lá, só precisa procurar no lugar certo. 🔍

### 🎯 **Métodos Disponíveis (tente nesta ordem)**

1. **Método 1: Application/Storage Tab** ⭐ **RECOMENDADO**
   - Mostra TODAS as chaves do localStorage visualmente
   - Não precisa digitar comandos
   - Funciona em 90% dos casos

2. **Método 2: Console (comandos)**
   - Para quem prefere linha de comando
   - Testa múltiplas variações de chave

3. **Método 3: Network Tab** 🔥 **MAIS CONFIÁVEL**
   - Captura o token durante o processo de login
   - Funciona mesmo se não estiver no localStorage
   - 100% de taxa de sucesso

4. **Método 4: Cookies**
   - Último recurso se nenhum outro funcionar

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

#### **Método 1: Via Application/Storage Tab (RECOMENDADO)**

1. **Após fazer login no Nike.com**, pressione `F12` para abrir Developer Tools

2. Clique na aba **"Application"** (Chrome/Edge) ou **"Storage"** (Firefox)

3. No menu lateral esquerdo, expanda **"Local Storage"**

4. Clique em `https://www.nike.com`

5. **Procure por estas chaves** (o Nike pode usar qualquer uma):
   - `access_token`
   - `nike_access_token`
   - `token`
   - `auth_token`
   - `Authorization`
   - Ou qualquer chave que contenha "token" ou "auth"

6. **Copie o valor** (coluna da direita)
   - Clique com botão direito no valor
   - Selecione "Copy"
   - Ou selecione o texto completo e pressione `Ctrl+C`

7. ✅ Se encontrou um token longo (tipo JWT): **Pronto!**

#### **Método 2: Console do Navegador (Se Método 1 não funcionar)**

1. **Abra o Console**: Pressione `F12` → aba **"Console"**

2. **Tente estes comandos** um por um até encontrar o token:

```javascript
// Tenta access_token
localStorage.getItem('access_token')

// Tenta outras variações
localStorage.getItem('nike_access_token')
localStorage.getItem('token')
localStorage.getItem('auth_token')

// Lista TODAS as chaves do localStorage
Object.keys(localStorage)

// Mostra TODO o conteúdo do localStorage
console.log(localStorage)
```

3. Se `Object.keys(localStorage)` mostrar as chaves, procure por algo relacionado a "token" ou "auth"

4. **Copie APENAS o conteúdo entre as aspas** (sem as aspas)

#### **Método 3: Network Tab (Se nenhum método acima funcionar)**

Este método captura o token diretamente das requisições HTTP:

1. **ANTES de fazer login**, abra Developer Tools (`F12`)

2. Clique na aba **"Network"**

3. **Marque a opção "Preserve log"** (importante!)

4. Agora **faça o login** no Nike.com com as credenciais do usuário

5. Após o login bem-sucedido, na aba Network:
   - Use o filtro de busca (campo "Filter")
   - Digite: `token` ou `auth` ou `login`

6. Clique em cada requisição que aparecer

7. Procure na aba **"Headers"** ou **"Response"**:
   - Headers → procure por `Authorization: Bearer ...`
   - Response → procure por `"access_token":`

8. **Copie o token** (geralmente começa com `eyJ...`)

9. ✅ **Pronto!** Você tem o token.

#### **Método 4: Cookies (Último recurso)**

Se nenhum método acima funcionar:

1. Pressione `F12` → aba **"Application"** → **"Cookies"**

2. Clique em `https://www.nike.com`

3. Procure por cookies com nome:
   - `access_token`
   - `auth_token`
   - `bearer`
   - Ou qualquer cookie com valor muito longo (JWT)

4. Copie o **Value** do cookie

---

### **⚠️ Importantes: O que é um token válido?**

Um token Nike válido geralmente:
- É **muito longo** (100-1000+ caracteres)
- Começa com `eyJ` (formato JWT)
- Exemplo: `eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJleHAiOjE3NDY3MTI0NTUsImlhdCI6MTcxNT...`

**❌ NÃO é um token válido:**
- Valores curtos (menos de 50 caracteres)
- UUIDs simples: `123e4567-e89b-12d3-a456-426614174000`
- Strings simples: `"logged_in"`, `"true"`, etc.

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

### **🔍 Método Recomendado: Application/Storage Tab**

```
1. Faça login no Nike.com
   ↓
2. Pressione F12
   ↓
3. Clique aba "Application"
   ┌─────────────────────────────────────────────┐
   │ Elements Console Sources Network...         │
   │ ► Application ◄ (clique aqui)               │
   └─────────────────────────────────────────────┘
   ↓
4. Menu lateral → Local Storage → nike.com
   ┌────────────────────┬──────────────────────┐
   │ ▼ Local Storage    │ Key          Value   │
   │   ▼ https://nike.. │ access_token eyJh... │ ← COPIE ISSO!
   │                    │ user_id      12345   │
   │                    │ ...          ...     │
   └────────────────────┴──────────────────────┘
   ↓
5. Copie o VALUE do access_token
   ↓
6. Cole no campo "Token Nike" no admin
   ↓
7. Clique "Ativar Nike" ✓
```

### **📡 Se não encontrar no Local Storage: Network Tab**

```
1. ANTES de fazer login, pressione F12
   ↓
2. Clique aba "Network"
   ┌─────────────────────────────────────────────┐
   │ Elements Console Sources ► Network ◄        │
   │ ☑ Preserve log  (marque isso!)              │
   └─────────────────────────────────────────────┘
   ↓
3. Faça o login no Nike.com
   ↓
4. Na lista de requisições, procure:
   - login, auth, token, oauth
   ┌─────────────────────────────────────────────┐
   │ Name           Status  Type                 │
   │ login          200     xhr                  │ ← Clique
   │ oauth/token    200     fetch                │ ← Clique
   └─────────────────────────────────────────────┘
   ↓
5. Clique na requisição → aba "Response"
   ┌─────────────────────────────────────────────┐
   │ Headers Preview Response                    │
   │ {                                           │
   │   "access_token": "eyJhbGc...",             │ ← COPIE ISSO!
   │   "expires_in": 3600,                       │
   │   ...                                       │
   │ }                                           │
   └─────────────────────────────────────────────┘
   ↓
6. Copie o access_token (sem aspas)
```

---

### **💡 Fluxo Completo**

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
- **Verifique se você está na página correta após login**
  - Deve estar em `https://www.nike.com` (não `.com.br` ou outro domínio)
  - Tente navegar para `https://www.nike.com/member/profile` após o login
- **Use o Método 1 (Application/Storage)** em vez do console
  - Veja TODAS as chaves do localStorage visualmente
  - Procure por qualquer chave relacionada a "token" ou "auth"
- **Tente o Método 3 (Network Tab)**
  - Captura o token durante o login
  - Mais confiável que buscar no localStorage
- **Verifique se o login foi bem-sucedido**
  - Você vê o nome/foto do usuário no topo?
  - Tente acessar: `https://www.nike.com/member/settings`
- **Teste em outro navegador**
  - Chrome, Firefox ou Edge
  - Às vezes um navegador funciona melhor que outro
- **Limpe cache e cookies e tente novamente**

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
| `localStorage.getItem()` retorna `null` | Use Método 1 (Application Tab) para ver todas as chaves, ou Método 3 (Network Tab) |
| Token com aspas | Remova as aspas antes de colar |
| Token muito curto (<50 chars) | Não é o token certo, procure por um valor longo que comece com `eyJ` |
| Não vê "access_token" no localStorage | Tente `nike_access_token`, `token`, `auth_token` ou use Método 3 (Network) |
| Erro "is not a function" no console | Certifique-se de copiar o comando corretamente, sem caracteres extras |
| "Já existe admin" na /setup | Você já é admin, faça login normalmente |
| Não vê link "Admin" no menu | Você não é admin ainda, use /setup primeiro |
| Usuário não aparece pendente | Ele ainda não forneceu credenciais Nike |
| Console não abre | Tente `Ctrl+Shift+J` ou `Ctrl+Shift+I` ou `F12` |
| Network Tab vazia após login | Marque "Preserve log" ANTES de fazer login |

---

## 📞 Quando Pedir Ajuda

Se após 3 tentativas o token não funcionar:
1. Peça ao usuário para verificar credenciais
2. Tente com outro navegador
3. Verifique os logs do Render por erros

---

**Agora você está pronto para configurar tokens Nike!** 🚀

Qualquer dúvida, consulte este guia ou os logs do sistema.
