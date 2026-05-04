# 🎯 Sistema Admin - Guia Rápido

## Para Você (Admin)

### 1️⃣ Tornar-se Admin (Primeiro Acesso)

```bash
# No servidor ou localmente
python make_admin.py seu@email.com
```

Ou se estiver no Render, use o Shell:
```bash
python make_admin.py seu@email.com
```

### 2️⃣ Acessar Painel Admin

- URL: https://garmin-nike-sync.onrender.com/admin
- Aparece link "Admin" no menu (amarelo)

### 3️⃣ Quando Novo Usuário Registrar

Você verá no log do Render:
```
⚠️ ADMIN ACTION REQUIRED - Nike credentials pending for user: usuario@email.com (ID: 5)
```

### 4️⃣ Configurar Nike do Usuário

1. Acesse **/admin**
2. Veja usuário na seção **"Pendentes"**
3. Clique **"Configurar Nike"**
4. **Copie** as credenciais Nike do usuário
5. Clique **"Abrir Nike.com"**
6. Faça login com as credenciais copiadas
7. Abra Console (F12)
8. Digite: `localStorage.getItem('access_token')`
9. **Copie o token** (sem as aspas)
10. Cole no campo **"Token Nike"**
11. Clique **"Ativar Nike"**
12. ✅ Pronto! Usuário será notificado

### 5️⃣ Se Credenciais Inválidas

1. No painel do usuário, clique **"Marcar como Erro"**
2. Digite mensagem: "Credenciais inválidas. Verifique seu email e senha Nike."
3. Usuário verá alerta vermelho no dashboard

---

## Para Usuários Finais

### Fluxo Simples:

1. **Registrar** conta
2. **Informar** credenciais Garmin e Nike
3. **Aguardar** configuração (até 24h)
4. **Receber notificação** verde no dashboard
5. **Pronto!** Sincronização automática ativa ✨

### Status no Dashboard:

- 🟡 **Pendente**: Aguardando configuração
- 🟢 **Ativo**: Funcionando! 
- 🔴 **Erro**: Verificar credenciais

---

## Comandos Úteis

```bash
# Listar todos os admins
python make_admin.py --list

# Ver logs do Render (para encontrar novos usuários)
# Render Dashboard → Logs → Procurar por "ADMIN ACTION REQUIRED"
```

---

## ⚠️ Importante

- Mantenha as credenciais dos usuários **seguras**
- Tokens Nike são **criptografados** no banco
- Não compartilhe tokens com terceiros
- Configure PostgreSQL no Render (DATABASE_URL) para persistência

---

## 🚀 Deploy Automatizado

Cada push no GitHub:
1. Render faz pull automático
2. Executa `migrate.sh` (adiciona colunas SQL se necessário)
3. Inicia gunicorn
4. ✅ Pronto!

---

**Agora está 100% funcional!** 🎉
