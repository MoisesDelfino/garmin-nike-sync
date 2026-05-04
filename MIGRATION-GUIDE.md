# 🔄 Migração para Multi-User

Guia rápido para migrar de single-user para multi-user.

## 🤔 Devo migrar?

### NÃO migre se:
- ❌ Você tem apenas uma conta Garmin/Nike
- ❌ Está satisfeito com o modo atual
- ❌ Não precisa gerenciar múltiplas contas

**→ Continue usando o modo single-user atual!**

### Migre se:
- ✅ Você quer sincronizar múltiplas contas (família/amigos)
- ✅ Precisa de configurações diferentes por usuário
- ✅ Quer centralizar gerenciamento de várias contas

## 🚀 Migração Rápida (5 minutos)

### Passo 1: Pull das Atualizações

```bash
cd garmin-nike-sync
git pull
```

### Passo 2: Escolher Modo

#### Opção A: Continuar Single-User (Recomendado)

**Não faça nada!** O sistema detecta automaticamente:

- Se `config/users.json` **NÃO existe** → Modo single-user
- Seus secrets atuais continuam funcionando
- Zero mudanças necessárias

✅ **Vantagem:** Simplicidade

#### Opção B: Migrar para Multi-User

**1. Copie o template:**
```bash
cp config/users.example.json config/users.json
```

**2. Use o CLI para adicionar usuário:**
```bash
python manage_users.py add
```

Responda as perguntas:
```
ID do usuário: user1
Nome completo: Seu Nome
Secret Garmin Email [GARMIN_EMAIL_USER1]: (Enter)
Secret Garmin Password [GARMIN_PASSWORD_USER1]: (Enter)
Secret Nike Token [NIKE_TOKEN_USER1]: (Enter)
Dias de histórico [365]: (Enter)
...
```

**3. Renomeie seus secrets no GitHub:**

Vá em **Settings** → **Secrets** → **Actions**

**Antes (single-user):**
```
GARMIN_EMAIL
GARMIN_PASSWORD
NIKE_ACCESS_TOKEN
```

**Depois (multi-user):**
```
GARMIN_EMAIL_USER1    (renomeie GARMIN_EMAIL)
GARMIN_PASSWORD_USER1 (renomeie GARMIN_PASSWORD)
NIKE_TOKEN_USER1      (renomeie NIKE_ACCESS_TOKEN)
MULTI_USER_MODE = true (NOVO - crie este)
```

**4. Commit e push:**
```bash
git add config/users.json
git commit -m "Migrate to multi-user mode"
git push
```

**5. Teste:**
```bash
# No GitHub Actions
Actions → Run workflow
```

✅ **Pronto!** Agora você pode adicionar mais usuários.

## 📊 Comparação

| Feature | Single-User | Multi-User |
|---------|-------------|------------|
| Contas | 1 Garmin → 1 Nike | N Garmin → N Nike |
| Setup | 3 secrets | 3N secrets + 1 config |
| Complexidade | ⭐ Simples | ⭐⭐ Média |
| Arquivo config | Não | config/users.json |
| Histórico | sync_history.json | sync_history_<user>.json |
| CLI tool | Não | manage_users.py |

## 🛠️ Ferramenta CLI

Após migração, use o CLI para gerenciar usuários:

```bash
# Listar usuários
python manage_users.py list

# Adicionar usuário
python manage_users.py add

# Remover usuário
python manage_users.py remove

# Ativar/desativar
python manage_users.py toggle
```

## 🔄 Voltar para Single-User

Se mudou de ideia:

**1. Delete o arquivo de configuração:**
```bash
rm config/users.json
```

**2. Restaure os secrets originais:**
```
GARMIN_EMAIL        (de volta)
GARMIN_PASSWORD     (de volta)
NIKE_ACCESS_TOKEN   (de volta)
```

**3. Delete o secret:**
```
MULTI_USER_MODE (delete)
```

**4. Commit:**
```bash
git rm config/users.json
git commit -m "Revert to single-user mode"
git push
```

✅ **Pronto!** Voltou ao modo single-user.

## 📝 Exemplo Prático: Família

**Cenário:** Pai, mãe e filho querem sincronizar.

**1. Criar usuários:**
```bash
python manage_users.py add
# ID: pai, Nome: João Silva

python manage_users.py add
# ID: mae, Nome: Maria Silva

python manage_users.py add
# ID: filho, Nome: Pedro Silva
```

**2. Arquivo gerado (`config/users.json`):**
```json
{
  "users": [
    {"id": "pai", "name": "João Silva", "enabled": true, ...},
    {"id": "mae", "name": "Maria Silva", "enabled": true, ...},
    {"id": "filho", "name": "Pedro Silva", "enabled": true, ...}
  ]
}
```

**3. Secrets no GitHub (9 secrets):**
```
GARMIN_EMAIL_PAI, GARMIN_PASSWORD_PAI, NIKE_TOKEN_PAI
GARMIN_EMAIL_MAE, GARMIN_PASSWORD_MAE, NIKE_TOKEN_MAE
GARMIN_EMAIL_FILHO, GARMIN_PASSWORD_FILHO, NIKE_TOKEN_FILHO
```

**4. Históricos separados:**
```
sync_history_pai.json
sync_history_mae.json
sync_history_filho.json
```

## 💡 Dicas

✅ **Teste local primeiro:**
```bash
# Crie .env com todas as credenciais
GARMIN_EMAIL_USER1=...
GARMIN_PASSWORD_USER1=...
NIKE_TOKEN_USER1=...

# Execute
python main.py
```

✅ **Adicione usuários gradualmente:**
- Comece com 1 usuário
- Teste
- Adicione mais

✅ **Use IDs descritivos:**
- ✅ Bom: `joao`, `maria`, `pedro`
- ❌ Ruim: `user1`, `user2`, `user3`

✅ **Desative temporariamente:**
```bash
python manage_users.py toggle
# Em vez de deletar
```

## 🆘 Suporte

**Documentação completa:**
- [MULTI-USER-GUIDE.md](MULTI-USER-GUIDE.md) - Guia detalhado
- [README.md](README.md) - Documentação principal

**Problemas?**
- Abra uma issue no GitHub
- Veja logs em: Actions → Última execução

---

**Resumo:**
- 👤 Single-user: Continua funcionando como antes
- 👥 Multi-user: Opcional, para quem precisa
- 🔄 Migração: Reversível e não-destrutiva
- ⚙️ Escolha: Você decide quando/se migrar
