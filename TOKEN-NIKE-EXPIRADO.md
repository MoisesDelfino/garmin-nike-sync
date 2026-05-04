# 🔧 Token Nike Inválido ou Expirado - Como Resolver

## 🚨 Erro Resolvido

**Problema:** `Unexpected token '<', "<html>... is not valid JSON"`

**Causa:** O token Nike estava inválido ou expirado, e a Nike retornou uma página HTML de erro em vez de dados JSON.

---

## ✅ Correção Implementada

O sistema agora:

1. **Detecta automaticamente** quando o token está inválido
2. **Marca a conta** com status de erro
3. **Mostra mensagem clara** para o usuário
4. **Não trava** mais com erros confusos

---

## 🎯 O Que Acontece Agora

### **Para o Usuário:**

Quando o token expira, você verá um **alerta vermelho** no dashboard:

```
❌ Erro no Nike Run Club
Seu token Nike expirou ou está inválido.
Entre em contato com o administrador para renovar.
→ Atualizar credenciais
```

### **Para o Admin:**

Você receberá uma notificação e poderá:

1. Acessar `/admin`
2. Ver o usuário na seção **"Usuários com Erro"**
3. Clicar em **"Reconfigu rar"**
4. Extrair novo token Nike
5. Inserir e ativar

---

## 🔄 Como Renovar o Token Nike

### **Passo a Passo Rápido:**

1. **Acesse o painel admin**: `/admin`

2. **Encontre o usuário** na lista de erros

3. **Clique "Reconfigurar"**

4. **Faça login no Nike.com** com as credenciais do usuário

5. **Extraia novo token** (F12 → Application → Local Storage → oidc.user:...)

6. **Cole o novo token** e clique "Ativar Nike"

7. ✅ **Pronto!** Status volta para "Ativo"

---

## ⏱️ Validade do Token Nike

Os tokens Nike geralmente **expiram após**:
- **30-90 dias** (depende do tipo de token)
- Logout manual do usuário
- Mudança de senha
- Atualização de segurança da Nike

### **Renovação Automática:**

⚠️ Atualmente, a renovação **não é automática** - requer intervenção manual do admin.

**Possível melhoria futura:** Sistema de notificação quando token está próximo de expirar.

---

## 🔍 Logs para Diagnóstico

Agora os logs do Render mostram mensagens claras:

### **Token Inválido:**
```
❌ Nike retornou HTML em vez de JSON - Token inválido ou expirado
Status: 401
O token Nike precisa ser renovado pelo administrador
```

### **Token Expirado:**
```
❌ Token Nike não autorizado (401) - Token inválido ou expirado
```

### **Token Bloqueado:**
```
❌ Acesso negado pela Nike (403) - Token pode estar bloqueado
```

---

## 📊 Status da Conta Nike

O sistema agora rastreia 3 estados:

| Status | Cor | Significado | Ação |
|--------|-----|-------------|------|
| **Pendente** 🟡 | Amarelo | Aguardando configuração inicial | Admin deve configurar token |
| **Ativo** 🟢 | Verde | Funcionando normalmente | Nenhuma ação necessária |
| **Erro** 🔴 | Vermelho | Token inválido/expirado | Admin deve renovar token |

---

## ✨ Melhorias Técnicas

### **src/nike_client.py:**
- ✅ Verifica `Content-Type` antes de parsear JSON
- ✅ Detecta HTML e retorna mensagem clara
- ✅ Tratamento específico para 401/403
- ✅ Timeout de 15s nas requisições
- ✅ Try/catch ao fazer `response.json()`

### **web/sync_manager.py:**
- ✅ Atualiza `nike_status = 'error'` automaticamente
- ✅ Salva mensagem detalhada em `nike_status_message`
- ✅ Commit no DB para persistir estado
- ✅ Usuário vê alerta no dashboard

---

## 🎯 Próximos Passos

### **Quando o Deploy Finalizar (2-3 min):**

1. **Aguarde** o Render completar o deploy
2. **Acesse** `/admin` 
3. **Veja seu usuário** na lista de erros
4. **Clique "Reconfigurar"**
5. **Extraia novo token Nike** (veja guia completo em [COMO-EXTRAIR-TOKEN-NIKE.md](COMO-EXTRAIR-TOKEN-NIKE.md))
6. **Ative** e pronto! ✨

---

## 🛡️ Prevenção

### **Para Evitar Expiração Frequente:**

1. Use tokens de longa duração (se disponível)
2. Configure notificações de expiração
3. Documente quando foi a última renovação
4. Teste periodicamente a sincronização

---

## 📚 Documentação Relacionada

- [COMO-EXTRAIR-TOKEN-NIKE.md](COMO-EXTRAIR-TOKEN-NIKE.md) - Guia completo de extração
- [ADMIN-GUIDE.md](ADMIN-GUIDE.md) - Guia do painel admin
- [FIX-INTERNAL-ERROR.md](FIX-INTERNAL-ERROR.md) - Soluções de problemas gerais

---

**Sistema agora é robusto e não trava mais!** 🎉

O erro será detectado automaticamente e você receberá notificações claras quando precisar renovar tokens.
