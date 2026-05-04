# 🚨 SOLUÇÃO: Internal Server Error no Render

## Problema
O site está dando **Internal Server Error** porque as novas colunas do banco de dados (nike_status, is_admin, etc) não foram criadas.

## ✅ Solução Implementada

### 1️⃣ Auto-Migração Automática
Agora o app adiciona as colunas automaticamente ao iniciar! 🎉

Arquivo: `web/auto_migrate.py`
- Verifica colunas faltantes
- Adiciona automaticamente no PostgreSQL/SQLite
- Não precisa mais rodar migrate.sh manualmente

### 2️⃣ Rota /setup (Sem Shell!)
Como você não tem acesso ao Shell no Render gratuito, criamos uma solução melhor:

**URL:** `https://garmin-nike-sync.onrender.com/setup`

**Passos:**

1. **Registre sua conta** normalmente:
   - Vá em `/register`
   - Crie sua conta com email/senha

2. **Configure a chave de setup no Render:**
   - Dashboard Render → Environment
   - Adicione variável:
     ```
     ADMIN_SETUP_PASSWORD=SUA_SENHA_SECRETA_AQUI
     ```
   - Exemplo: `ADMIN_SETUP_PASSWORD=MinhaSenha123!`
   - Clique "Save Changes"

3. **Acesse /setup:**
   - Vá em `https://garmin-nike-sync.onrender.com/setup`
   - Digite seu email
   - Digite a senha que você configurou no passo 2
   - Clique "Criar Admin"

4. **Pronto! 🎉**
   - Faça login
   - O link "Admin" aparecerá no menu
   - Configure tokens Nike dos usuários

---

## 📋 Checklist Pós-Deploy

Após o próximo deploy (2-3 minutos), faça:

- [ ] Site carrega sem erro?
- [ ] Consegue registrar conta?
- [ ] Página /setup funciona?
- [ ] Consegue tornar-se admin?
- [ ] Painel /admin aparece?

---

## 🔍 O Que Foi Corrigido

### Auto-Migração (`web/auto_migrate.py`)
```python
# Adiciona automaticamente:
- nike_email_enc
- nike_password_enc  
- nike_status (pending/active/error)
- nike_status_message
- nike_configured_at
- is_admin (boolean)
```

### Rota /setup (`app.py`)
```python
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # Só funciona se não houver admin
    # Pede email + chave de setup
    # Torna usuário admin
```

---

## 🎯 Fluxo Completo Agora

1. **Deploy automático** → Auto-migração roda
2. **Você registra** → Conta criada
3. **Você acessa /setup** → Vira admin
4. **Usuários registram** → Credenciais pendentes
5. **Você configura tokens** → Painel admin
6. **Sincronização funciona!** 🚀

---

## ⚠️ Se Ainda Tiver Erro

Verifique os logs do Render:
```
Dashboard → Logs → Procurar por:
- "Auto-migração concluída"
- "Error" ou "Exception"
```

Se ver erro de coluna faltando, o problema será resolvido no próximo deploy! ✨

---

**Pronto para deploy!** 🚀
