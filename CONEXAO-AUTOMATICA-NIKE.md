# ⚡ Conexão Automática Nike - Guia Rápido

## 🎯 O Novo Fluxo (Super Simples!)

### **Antes (Complicado):**
1. ❌ Abrir Nike.com
2. ❌ Pressionar F12
3. ❌ Navegar pelas ferramentas
4. ❌ Procurar cookie
5. ❌ Copiar manualmente
6. ❌ Colar no app

### **Agora (Automático!):**
1. ✅ Clicar em "Conectar Nike"
2. ✅ Fazer login no Nike.com
3. ✅ Copiar e executar código (1 clique)
4. ✅ **PRONTO!** Token salvo automaticamente

---

## 🚀 Como Usar

### **Passo 1: Acesse a Página de Credenciais**

```
https://garmin-nike-sync.onrender.com/credentials
```

### **Passo 2: Clique no Botão "Conectar"**

Você verá um botão azul grande:
```
🔌 Conexão Automática
Faça login no Nike e o token será capturado automaticamente
[Conectar →]
```

### **Passo 3: Faça Login no Nike**

- Abrirá uma nova aba do Nike.com
- Faça login normalmente com suas credenciais
- Aguarde carregar completamente

### **Passo 4: Execute o Código**

Na página do app, você verá um código JavaScript.

**Copie o código** (botão "Copiar") e:

1. Volte para a aba do **Nike.com**
2. Pressione **F12** (abre o Console do desenvolvedor)
3. Clique na aba **"Console"**
4. **Cole o código** e pressione Enter
5. Aguarde a mensagem de sucesso

### **Passo 5: Pronto! ✅**

Você será redirecionado automaticamente para o Dashboard com a mensagem:
```
✅ Nike Conectado com Sucesso!
```

---

## 🎨 Interface

A nova página tem 3 etapas visuais:

### **Etapa 1: Conectar**
- Botão grande "Fazer Login no Nike"
- Instruções claras
- Design limpo e moderno

### **Etapa 2: Código**
- Código pré-formatado pronto para copiar
- Botão de cópia com 1 clique
- Instruções passo-a-passo

### **Etapa 3: Sucesso**
- Ícone de check verde
- Confirmação visual
- Redirecionamento automático

---

## 🔧 Como Funciona (Técnico)

### **Fluxo de Dados:**

```
1. Usuário clica "Conectar"
   ↓
2. App abre Nike.com em nova aba
   ↓
3. Usuário faz login no Nike.com
   ↓
4. Bookmarklet JavaScript roda na página Nike
   ↓
5. Extrai token de:
   - document.cookie
   - localStorage
   - sessionStorage
   ↓
6. Envia token via POST para /nike/callback
   ↓
7. Backend valida e salva token criptografado
   ↓
8. Retorna sucesso + redireciona usuário
```

### **Segurança:**

- ✅ Token trafega via HTTPS
- ✅ Validação de tamanho mínimo (50 chars)
- ✅ Armazenamento com AES-256
- ✅ CORS protegido
- ✅ Sessão autenticada obrigatória
- ✅ Nenhum dado sensível exposto

### **Métodos de Extração:**

O bookmarklet tenta 3 métodos:

1. **Cookies** - Procura `access_token`, `nike_access_token`
2. **localStorage** - Busca chaves comuns
3. **sessionStorage** - Fallback adicional

---

## 📱 Funciona no Celular?

**Sim!** Mas com algumas limitações:

### **Android (Chrome/Firefox):**
1. Copie o código no celular
2. Abra Nike.com no navegador
3. Faça login
4. Abra o console (pode ser mais difícil)
5. Execute o código

### **iPhone (Safari):**
1. Use um Mac para debug remoto, ou
2. Use o método manual tradicional

**Recomendação:** Use PC para melhor experiência

---

## ❓ FAQ

### **Por que não é 100% automático (sem executar código)?**

Por segurança! Navegadores bloqueiam acesso entre domínios diferentes (CORS).
Nike.com e nosso app não podem compartilhar cookies automaticamente.

O código JavaScript é necessário porque:
- Roda **dentro** da página Nike.com
- Tem acesso aos cookies daquele domínio
- É executado **por você**, então é seguro

### **O código expira?**

Não! O código é sempre o mesmo e pode ser usado múltiplas vezes.

### **Preciso fazer isso toda vez?**

Não! Apenas quando:
- Configurar pela primeira vez
- Token Nike expirar (3-6 meses)
- Trocar de conta

### **É seguro executar código no Console?**

Sim, **ESTE** código é seguro porque:
- Você pode ler o código completo
- Não modifica nada no Nike.com
- Apenas lê informações públicas (cookies)
- Envia apenas para o seu app autenticado

⚠️ **MAS CUIDADO:** Nunca execute códigos de fontes desconhecidas!

### **Posso continuar usando o método manual?**

**Sim!** O método manual ainda está disponível na mesma página.
Clique em "Prefere inserir o token manualmente?" no rodapé.

---

## 🎯 Vantagens do Novo Método

| Aspecto | Método Manual | Novo Método Automático |
|---------|---------------|------------------------|
| **Passos** | 6 etapas | 3 etapas |
| **Dificuldade** | Médio/Difícil | Fácil |
| **Tempo** | ~5 minutos | ~1 minuto |
| **Erros comuns** | Copiar incompleto | Quase nenhum |
| **Mobile friendly** | Difícil | Médio |
| **Guia visual** | Não | Sim |

---

## 🆘 Problemas?

### **"Token não encontrado"**

**Causas:**
- Não está logado no Nike.com
- Página não carregou completamente
- Cookies bloqueados

**Solução:**
1. Faça logout e login novamente
2. Aguarde 5 segundos após login
3. Execute o código novamente

### **"Erro ao enviar token"**

**Causas:**
- Conexão internet
- Sessão expirada no app

**Solução:**
1. Verifique sua internet
2. Faça login novamente no app
3. Tente o processo novamente

### **Console não abre (F12 não funciona)**

**Alternativas:**
- Chrome: Menu (⋮) → Mais ferramentas → Ferramentas do desenvolvedor
- Firefox: Menu (☰) → Mais ferramentas → Ferramentas de desenvolvimento
- Edge: Menu (...) → Mais ferramentas → Ferramentas do desenvolvedor

### **Ainda não funciona?**

Use o [método manual](COMO-OBTER-TOKEN-NIKE.md) ou entre em contato!

---

## 🎉 Feedback

Gostou do novo recurso? Tem sugestões?

- ⭐ Deixe uma estrela no GitHub
- 💬 Abra uma issue com feedback
- 🐛 Reporte bugs encontrados

---

**Made with ❤️ for runners** 🏃‍♂️
