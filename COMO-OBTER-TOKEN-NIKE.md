# 🔑 Como Obter o Token do Nike Run Club

Guia passo-a-passo completo para extrair o token de acesso do Nike Run Club, tanto no **PC** quanto no **Celular**.

---

## 💻 **Método 1: PC (Chrome/Firefox/Edge)** ⭐ Recomendado

### **Passo 1: Acesse o Nike.com**

1. Abra seu navegador (Chrome, Firefox, Edge, etc.)
2. Acesse: **https://www.nike.com**
3. Clique em **"Entrar"** (canto superior direito)
4. Faça login com seu email e senha Nike

### **Passo 2: Abra as Ferramentas do Desenvolvedor**

**Chrome/Edge:**
- Pressione `F12` ou
- Clique com botão direito → **"Inspecionar"** ou
- Menu (⋮) → **Mais ferramentas** → **Ferramentas do desenvolvedor**

**Firefox:**
- Pressione `F12` ou
- Menu (☰) → **Mais ferramentas** → **Ferramentas de desenvolvimento**

### **Passo 3: Vá para a Aba "Application"**

1. Nas ferramentas do desenvolvedor, procure a aba **"Application"** (Chrome/Edge) ou **"Storage"** (Firefox)
2. Se não estiver visível, clique em **"»"** para ver mais abas

### **Passo 4: Encontre os Cookies**

1. No painel esquerdo, expanda a seção **"Cookies"**
2. Clique em **`https://www.nike.com`**
3. Você verá uma lista de cookies

### **Passo 5: Copie o Token**

Procure por um cookie chamado:
- **`access_token`** ou
- **`nike_access_token`** ou
- Qualquer cookie com nome contendo `token`

**Copie o valor completo** (coluna "Value"):
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IjdFQzY4...
```

### **💡 Dica: Se não encontrar nos Cookies**

1. Ainda nas ferramentas do desenvolvedor, vá para a aba **"Console"**
2. Cole e execute este comando:
   ```javascript
   console.log(document.cookie)
   ```
3. Procure por `access_token=` no resultado
4. Copie tudo após o `=` até o próximo `;`

### **🎯 Alternativa: Usar Comando Direto**

Na aba **Console**, cole e execute:
```javascript
// Tenta extrair do cookie
let token = document.cookie.split(';').find(c => c.includes('access_token'));
if (token) {
    token = token.split('=')[1];
    console.log('Token encontrado:', token);
    copy(token); // Copia automaticamente
    alert('Token copiado!');
} else {
    console.log('Token não encontrado nos cookies');
}
```

---

## 📱 **Método 2: Celular (Android/iPhone)**

### **Android - Chrome**

#### **Opção A: Usar Chrome Remote Debugging**

1. **No PC:**
   - Abra Chrome e acesse `chrome://inspect`
   - Em "Discover network targets", marque a caixa

2. **No Celular:**
   - Ative **Opções do desenvolvedor**:
     - Vá em **Configurações** → **Sobre o telefone**
     - Toque 7 vezes em **Número da versão**
   - Ative **Depuração USB**:
     - **Configurações** → **Sistema** → **Opções do desenvolvedor**
   - Conecte o celular ao PC via USB
   - Abra Chrome no celular e acesse `nike.com`

3. **No PC:**
   - Em `chrome://inspect`, clique em **"inspect"** na aba do Nike.com
   - Siga os passos do Método 1 (PC)

#### **Opção B: Usar App Desenvolvedor**

1. Instale o app **"Web Inspector"** ou **"HTTP Debugger"** da Play Store
2. Configure para capturar tráfego do navegador
3. Abra Nike.com no navegador do celular
4. Faça login
5. No app debugger, procure por requisições para `api.nike.com`
6. Procure pelo header `Authorization: Bearer ...`
7. Copie o token após `Bearer `

### **iPhone - Safari**

#### **Opção A: Usar Safari Web Inspector (requer Mac)**

1. **No iPhone:**
   - Vá em **Ajustes** → **Safari** → **Avançado**
   - Ative **Web Inspector**

2. **No Mac:**
   - Conecte iPhone via USB
   - Abra Safari no Mac
   - Menu **Desenvolver** → Selecione seu iPhone → Escolha a aba Nike.com
   - Siga os passos do Método 1 (PC)

#### **Opção B: Copiar de um Computador** ⭐ Mais Fácil

1. Use o **Método 1 (PC)** para obter o token
2. Envie o token para seu celular via:
   - WhatsApp (mande para você mesmo)
   - E-mail
   - Notes sincronizado (iCloud/Google Keep)
3. Cole no app do celular

---

## 🖥️ **Método 3: Capturar Requisições de Rede** (Avançado)

### **Para Usuários Técnicos**

1. Abra as ferramentas do desenvolvedor (`F12`)
2. Vá para a aba **"Network"** (Rede)
3. Faça login no Nike.com
4. Procure por requisições para:
   - `api.nike.com`
   - `unite.nike.com`
   - Qualquer endpoint com `/login` ou `/token`
5. Clique na requisição
6. Na aba **"Headers"**, procure por:
   - **Request Headers** → `Authorization: Bearer ...`
   - **Response** → Pode conter o token no JSON

---

## 📝 **Como Identificar o Token Correto**

Um token válido do Nike:

✅ **Formato:**
```
eyJhbGciOiJSUzI1NiIsImtpZCI6Ij...
```

✅ **Características:**
- Começa com `eyJ` (JWT token)
- Muito longo (200-500+ caracteres)
- Contém letras maiúsculas, minúsculas, números e símbolos
- Separado por pontos (.) em 3 partes: `xxxxx.yyyyy.zzzzz`

❌ **NÃO é o token se:**
- Muito curto (menos de 50 caracteres)
- Contém apenas números
- É o seu email ou nome

---

## 🔄 **Depois de Obter o Token**

1. **Acesse:** https://garmin-nike-sync.onrender.com
2. Faça **login** ou **registre-se**
3. Vá em **"Credenciais"**
4. Cole o token no campo **"Nike Access Token"**
5. Clique em **"Salvar Credenciais"**
6. Pronto! Suas sincronizações estão configuradas

---

## ⚠️ **Token Expira?**

**Sim!** O token do Nike geralmente expira após **3-6 meses**.

**O que fazer quando expirar:**
1. Faça login no Nike.com novamente
2. Extraia um novo token usando este guia
3. Atualize nas credenciais do app

**Como saber se expirou:**
- Sincronizações começam a falhar
- Você verá erro "401 Unauthorized" nos logs

---

## 🆘 **Problemas Comuns**

### **"Não consigo encontrar o cookie access_token"**

**Solução 1:** Tente fazer logout e login novamente no Nike.com

**Solução 2:** Acesse uma página que use a API:
- https://www.nike.com/membership
- https://www.nike.com/nike-app

**Solução 3:** Use o Método 3 (Network) para capturar durante o login

### **"O token não funciona no app"**

- Verifique se copiou o token completo (sem espaços extras)
- Certifique-se de que está logado no Nike.com
- Tente gerar um token novo
- O token pode ter expirado

### **"Não tenho como usar ferramentas de desenvolvedor"**

Use a **Opção B do iPhone** ou peça ajuda para alguém com PC fazer a extração e enviar o token para você.

---

## 📸 **Screenshots Disponíveis**

Se precisar de imagens ilustrativas dos passos, me avise! Posso gerar:
- Screenshot das ferramentas do desenvolvedor
- Localização dos cookies
- Exemplo de token válido (censurado)

---

## 💡 **Dica Final**

**O método mais fácil é sempre usar um PC com Chrome!**

1. Abra Nike.com
2. Pressione `F12`
3. Aba "Application" → "Cookies" → Procure `access_token`
4. Copie o valor
5. Cole no app

**Leva menos de 2 minutos! ⚡**

---

**Dúvidas?** Entre em contato ou consulte a [documentação completa](STATUS.md)! 📚
