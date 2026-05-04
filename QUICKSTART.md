# 🚀 Deploy em 3 Passos

Guia super rápido para colocar a sincronização funcionando.

## 📋 Pré-requisitos

- [ ] Conta GitHub
- [ ] Conta Garmin Connect
- [ ] Conta Nike Run Club

## ⚡ Setup Rápido

### 1. Fork e Secrets (2 min)

```bash
# 1. Clique em "Fork" neste repositório

# 2. No seu fork, vá em Settings > Secrets > Actions > New secret

# 3. Adicione 3 secrets:
GARMIN_EMAIL          → seu_email@exemplo.com
GARMIN_PASSWORD       → sua_senha_garmin
NIKE_ACCESS_TOKEN     → token_nike (veja NIKE-TOKEN-GUIDE.md)
```

### 2. Ativar Actions (1 min)

```bash
# 1. Vá na aba "Actions" do seu repositório
# 2. Clique em "I understand my workflows, go ahead and enable them"
# 3. Selecione "Garmin → Nike Sync"
# 4. Clique em "Enable workflow"
```

### 3. Primeira Execução (2 min)

```bash
# 1. Em Actions > "Garmin → Nike Sync"
# 2. Clique em "Run workflow" > "Run workflow"
# 3. Aguarde 2-5 minutos
# 4. ✅ Pronto! Suas atividades foram sincronizadas
```

## 🎯 Próximos Passos

A partir de agora:
- ✅ Sincronização automática a cada 15 minutos
- ✅ Novas corridas no Garmin → aparecem no Nike
- ✅ Sem duplicatas
- ✅ 100% automático

## 🔧 Personalizar

### Mudar frequência

Edite `.github/workflows/sync.yml`:

```yaml
# Linha 6
schedule:
  - cron: '*/30 * * * *'  # A cada 30 minutos
```

### Mudar período histórico

Edite `.github/workflows/sync.yml`:

```yaml
# Linha ~30
HISTORICAL_SYNC_DAYS: 180  # Últimos 6 meses
```

## 📊 Monitorar

### Ver última execução
```
Actions > Garmin → Nike Sync > Última execução
```

### Ver quantas atividades foram sincronizadas
```
Arquivo: sync_history.json (atualizado automaticamente)
```

## 🐛 Problemas?

### Workflow não executa

```bash
# Actions podem ser desativadas após 60 dias sem commit
# Solução: Execute manualmente uma vez

Actions > Run workflow
```

### Token Nike expirado

```bash
# Sintoma: Erro "401 Unauthorized"
# Solução:

1. Obtenha novo token (NIKE-TOKEN-GUIDE.md)
2. Settings > Secrets > NIKE_ACCESS_TOKEN > Update
3. Pronto!
```

### Erro Garmin

```bash
# Sintoma: "Authentication failed"
# Soluções:

1. Verifique email/senha nos Secrets
2. Desative 2FA temporariamente no Garmin
3. Tente login manual no Garmin Connect
```

## 💡 Dicas

**Primeira execução**: Pode demorar 3-5 minutos (importa histórico)

**Execuções seguintes**: 30-60 segundos (apenas novas atividades)

**Desativar**: Actions > Workflow > ⋯ > Disable

**Reativar**: Actions > Workflow > Enable

## 📱 Testar Agora

1. Faça uma corrida/caminhada no Garmin
2. Aguarde 15-30 minutos
3. Abra Nike Run Club
4. ✅ Sua atividade estará lá!

---

**Deu certo? ⭐ Dê uma estrela no projeto!**

**Problemas? 🐛 Abra uma issue.**
