# 👥 Guia Multi-User: Múltiplas Contas Garmin/Nike

Este guia explica como configurar o sistema para sincronizar **múltiplas contas** Garmin/Nike simultaneamente.

## 🎯 Quando Usar Multi-User

✅ **Use multi-user quando:**
- Você quer sincronizar contas de família/amigos no mesmo repositório
- Você gerencia múltiplas contas pessoais
- Você quer centralizar a sincronização de várias pessoas

❌ **Não use multi-user quando:**
- Você tem apenas uma conta (use o modo single-user padrão)
- Cada pessoa quer controle total (melhor fazer fork individual)

## 📋 Configuração Multi-User

### Passo 1: Criar Arquivo de Configuração

Copie o template:
```bash
cp config/users.example.json config/users.json
```

### Passo 2: Editar config/users.json

Abra `config/users.json` e configure seus usuários:

```json
{
  "users": [
    {
      "id": "user1",
      "name": "João Silva",
      "enabled": true,
      "credentials": {
        "garmin_email_secret": "GARMIN_EMAIL_USER1",
        "garmin_password_secret": "GARMIN_PASSWORD_USER1",
        "nike_token_secret": "NIKE_TOKEN_USER1"
      },
      "settings": {
        "historical_sync_days": 365,
        "time_tolerance_seconds": 300,
        "distance_tolerance_meters": 50
      }
    },
    {
      "id": "user2",
      "name": "Maria Santos",
      "enabled": true,
      "credentials": {
        "garmin_email_secret": "GARMIN_EMAIL_USER2",
        "garmin_password_secret": "GARMIN_PASSWORD_USER2",
        "nike_token_secret": "NIKE_TOKEN_USER2"
      },
      "settings": {
        "historical_sync_days": 180,
        "time_tolerance_seconds": 300,
        "distance_tolerance_meters": 50
      }
    }
  ],
  "global_settings": {
    "sync_interval_minutes": 15,
    "log_level": "INFO"
  }
}
```

**Campos explicados:**

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `id` | Identificador único do usuário | `user1`, `joao`, `maria` |
| `name` | Nome amigável (para logs) | `João Silva` |
| `enabled` | Se o usuário está ativo | `true` ou `false` |
| `garmin_email_secret` | Nome do Secret do Garmin email | `GARMIN_EMAIL_USER1` |
| `garmin_password_secret` | Nome do Secret do Garmin senha | `GARMIN_PASSWORD_USER1` |
| `nike_token_secret` | Nome do Secret do Nike token | `NIKE_TOKEN_USER1` |
| `historical_sync_days` | Dias de histórico na 1ª exec | `365` (1 ano) |
| `time_tolerance_seconds` | Tolerância tempo duplicação | `300` (±5 min) |
| `distance_tolerance_meters` | Tolerância distância | `50` (±50m) |

### Passo 3: Configurar GitHub Secrets

Para cada usuário, crie 3 secrets no GitHub:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### User 1:
```
GARMIN_EMAIL_USER1      → joao@exemplo.com
GARMIN_PASSWORD_USER1   → senha_do_joao
NIKE_TOKEN_USER1        → token_nike_do_joao
```

#### User 2:
```
GARMIN_EMAIL_USER2      → maria@exemplo.com
GARMIN_PASSWORD_USER2   → senha_da_maria
NIKE_TOKEN_USER2        → token_nike_da_maria
```

#### Secret Especial (Ativa Multi-User):
```
MULTI_USER_MODE         → true
```

⚠️ **IMPORTANTE:** O secret `MULTI_USER_MODE` **deve** ser criado com valor `true` para ativar o modo multi-user!

### Passo 4: Commit e Push

```bash
git add config/users.json
git commit -m "Configure multi-user sync"
git push
```

### Passo 5: Executar no GitHub Actions

1. Vá em **Actions**
2. Clique em **"Garmin → Nike Sync"**
3. Clique em **"Run workflow"**
4. Aguarde a execução

## 📊 Como Funciona

### Execução Multi-User

```
┌────────────────────────────────┐
│   GitHub Actions Trigger       │
│   (a cada 15 minutos)          │
└───────────┬────────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Carrega config/users.json     │
│  - User 1: João (enabled)      │
│  - User 2: Maria (enabled)     │
│  - User 3: Pedro (disabled)    │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Para cada usuário ATIVO:      │
│                                │
│  1. Carrega credenciais        │
│  2. Conecta Garmin/Nike        │
│  3. Sincroniza atividades      │
│  4. Salva histórico individual │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Commit históricos atualizados │
│  - sync_history_user1.json     │
│  - sync_history_user2.json     │
└────────────────────────────────┘
```

### Arquivos Gerados

Cada usuário tem seu próprio arquivo de histórico:

```
sync_history_user1.json  → Histórico do João
sync_history_user2.json  → Histórico da Maria
```

Esses arquivos **não** são versionados (estão no `.gitignore`), mas são commitados automaticamente pelo GitHub Actions.

## 🔧 Gerenciamento de Usuários

### Adicionar Novo Usuário

1. Edite `config/users.json`:
```json
{
  "id": "user3",
  "name": "Pedro Costa",
  "enabled": true,
  "credentials": {
    "garmin_email_secret": "GARMIN_EMAIL_USER3",
    "garmin_password_secret": "GARMIN_PASSWORD_USER3",
    "nike_token_secret": "NIKE_TOKEN_USER3"
  }
}
```

2. Adicione secrets no GitHub:
```
GARMIN_EMAIL_USER3
GARMIN_PASSWORD_USER3
NIKE_TOKEN_USER3
```

3. Commit e execute workflow

### Desativar Usuário (Temporário)

Edite `config/users.json`:
```json
{
  "id": "user2",
  "name": "Maria Santos",
  "enabled": false,  ← Mude para false
  ...
}
```

Esse usuário será pulado na próxima execução.

### Remover Usuário (Permanente)

1. Remova o bloco do usuário de `config/users.json`
2. Delete os secrets do GitHub (opcional)
3. Delete `sync_history_userX.json` (opcional)

## 🧪 Teste Local Multi-User

### Passo 1: Criar .env com Credenciais

Crie um arquivo `.env` com TODAS as credenciais:

```bash
# User 1
GARMIN_EMAIL_USER1=joao@exemplo.com
GARMIN_PASSWORD_USER1=senha_do_joao
NIKE_TOKEN_USER1=token_do_joao

# User 2
GARMIN_EMAIL_USER2=maria@exemplo.com
GARMIN_PASSWORD_USER2=senha_da_maria
NIKE_TOKEN_USER2=token_da_maria
```

### Passo 2: Executar

```bash
python main.py
```

O script detectará automaticamente o modo multi-user se `config/users.json` existir.

## 📋 Logs Multi-User

Os logs mostram claramente cada usuário:

```
===============================================
Sincronizando: João Silva (user1)
===============================================
Inicializando clientes...
✅ Autenticação Garmin: OK
✅ Conexão Nike: OK
Sincronizando apenas novas atividades para João Silva

Resultado para João Silva:
  Total: 5
  ✅ Sincronizadas: 2
  ⏭️  Duplicadas: 3
  ⏭️  Já sincronizadas: 0
  ❌ Erros: 0

===============================================
Sincronizando: Maria Santos (user2)
===============================================
...
```

## ⚙️ Configurações Personalizadas por Usuário

Cada usuário pode ter configurações diferentes:

```json
{
  "id": "user1",
  "settings": {
    "historical_sync_days": 365,      // João: 1 ano
    "time_tolerance_seconds": 300,    // ±5 minutos
    "distance_tolerance_meters": 50   // ±50 metros
  }
},
{
  "id": "user2",
  "settings": {
    "historical_sync_days": 90,       // Maria: 3 meses
    "time_tolerance_seconds": 600,    // ±10 minutos
    "distance_tolerance_meters": 100  // ±100 metros
  }
}
```

## 🔄 Compatibilidade com Single-User

O sistema **mantém compatibilidade** com o modo single-user:

**Se `config/users.json` NÃO existe:**
- Usa modo single-user (variáveis antigas)
- Secrets: `GARMIN_EMAIL`, `GARMIN_PASSWORD`, `NIKE_ACCESS_TOKEN`
- Arquivo: `sync_history.json`

**Se `config/users.json` existe:**
- Usa modo multi-user
- Secrets: `GARMIN_EMAIL_USER1`, etc.
- Arquivos: `sync_history_user1.json`, etc.

## 🐛 Troubleshooting Multi-User

### Erro: "Nenhum usuário configurado"

**Causa:** `config/users.json` está vazio ou todos estão `enabled: false`

**Solução:** 
```json
{
  "users": [
    {
      "id": "user1",
      "enabled": true,  ← Certifique-se de que está true
      ...
    }
  ]
}
```

### Erro: "Credenciais não encontradas"

**Causa:** Secret não configurado no GitHub

**Solução:**
1. Verifique o nome do secret em `config/users.json`
2. Crie o secret correspondente no GitHub
3. O nome deve ser **EXATAMENTE** igual

### Usuário pulado silenciosamente

**Causa:** `enabled: false` ou credenciais inválidas

**Solução:**
```bash
# Veja os logs:
Actions > Última execução > Expandir "Run sync"

# Procure por:
"Usuário Maria Santos (user2) habilitado mas sem credenciais válidas"
```

### Workflow não detecta multi-user

**Causa:** Secret `MULTI_USER_MODE` não configurado

**Solução:**
```
Settings > Secrets > New secret
Name: MULTI_USER_MODE
Value: true
```

## 💡 Dicas Multi-User

✅ **Nomes descritivos**: Use IDs e nomes claros (`joao`, `maria`)  
✅ **Teste local**: Sempre teste com `.env` antes de fazer deploy  
✅ **Um de cada vez**: Adicione usuários gradualmente  
✅ **Desative temporariamente**: Use `enabled: false` em vez de deletar  
✅ **Backup de tokens**: Salve tokens Nike em local seguro (expiram)  

## 📊 Limites

- **GitHub Actions**: 2000 min/mês (gratuito)
- **Tempo por execução**: ~1-2 min por usuário
- **Usuários recomendados**: Até 5-10 usuários
- **Com 5 usuários**: ~10 min/execução = 200 execuções/mês

Se precisar de mais usuários, considere:
- Diminuir frequência (a cada 30 min em vez de 15)
- Usar VPS próprio
- Dividir em múltiplos repositórios

## 🎉 Conclusão

Com o modo multi-user você pode:
- ✅ Sincronizar múltiplas contas no mesmo repo
- ✅ Centralizar gerenciamento
- ✅ Configurações individuais por usuário
- ✅ Históricos separados
- ✅ 100% gratuito (GitHub Actions)

---

**Dúvidas?** Veja também:
- [README.md](README.md) - Documentação principal
- [DEPLOY-GITHUB.md](DEPLOY-GITHUB.md) - Deploy no GitHub
- [NIKE-TOKEN-GUIDE.md](NIKE-TOKEN-GUIDE.md) - Como obter token Nike
