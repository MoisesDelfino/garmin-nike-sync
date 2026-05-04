# 🚀 Deploy no GitHub - Passo a Passo

## ✅ Status Atual

- ✅ Repositório Git inicializado
- ✅ Branch `main` configurada
- ✅ Commit inicial feito (2244 linhas, 16 arquivos)
- ✅ Código completo e funcional

## 📋 Próximos Passos

### 1. Criar Repositório no GitHub (2 minutos)

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `garmin-nike-sync`
   - **Description**: `🏃 Automatic sync from Garmin Connect to Nike Run Club`
   - **Visibility**: Public (ou Private - funciona nos dois)
   - ❌ **NÃO** marque "Add a README" (já temos)
   - ❌ **NÃO** adicione .gitignore (já temos)
   - ❌ **NÃO** adicione license (já temos)
3. Clique em **"Create repository"**

### 2. Enviar Código (1 comando)

Copie e execute no terminal:

```bash
cd "/home/moises-delfino/Área de trabalho/garmin-nike-sync"

# Substitua SEU_USUARIO pelo seu usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/garmin-nike-sync.git

# Envie o código
git push -u origin main
```

**Exemplo:**
```bash
# Se seu usuário for "moises-delfino"
git remote add origin https://github.com/moises-delfino/garmin-nike-sync.git
git push -u origin main
```

### 3. Configurar Secrets (3 secrets)

No GitHub, vá em:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Adicione 3 secrets:

#### Secret 1: GARMIN_EMAIL
```
Name: GARMIN_EMAIL
Secret: seu_email@exemplo.com
```

#### Secret 2: GARMIN_PASSWORD
```
Name: GARMIN_PASSWORD
Secret: sua_senha_garmin
```

#### Secret 3: NIKE_ACCESS_TOKEN
```
Name: NIKE_ACCESS_TOKEN
Secret: seu_token_nike_aqui
```

⚠️ **Como obter o token Nike:**
- Veja instruções completas em: [NIKE-TOKEN-GUIDE.md](NIKE-TOKEN-GUIDE.md)
- Métodos disponíveis: Charles Proxy, HTTP Toolkit, Navegador, API OAuth

### 4. Ativar GitHub Actions (1 minuto)

1. Vá na aba **Actions** do repositório
2. Clique em **"I understand my workflows, go ahead and enable them"**
3. Selecione o workflow **"Garmin → Nike Sync"**
4. ✅ Workflow ativado!

### 5. Executar Primeira Sincronização (2 minutos)

1. Na aba **Actions**, clique no workflow **"Garmin → Nike Sync"**
2. Clique em **"Run workflow"** → **"Run workflow"**
3. Aguarde 2-5 minutos (primeira execução importa histórico)
4. ✅ Verifique os logs para confirmar sucesso

### 6. Verificar Resultados

Após a execução:
1. Abra o app/site Nike Run Club
2. Suas corridas do Garmin devem estar lá!
3. Arquivo `sync_history.json` será atualizado automaticamente

## 🔄 Funcionamento Automático

A partir de agora:
- ✅ Sincronização automática **a cada 15 minutos**
- ✅ Novas corridas aparecem automaticamente no Nike
- ✅ Sem duplicatas
- ✅ Totalmente automático

## 📊 Monitoramento

### Ver execuções
```
GitHub → Actions → Garmin → Nike Sync
```

### Ver histórico de sincronizações
```
Arquivo: sync_history.json (commitado automaticamente)
```

### Ver logs detalhados
```
Actions → Última execução → Expandir step "🔄 Run sync"
```

## 🔧 Personalização (Opcional)

### Mudar frequência de sincronização

Edite `.github/workflows/sync.yml`, linha 6:

```yaml
schedule:
  - cron: '*/30 * * * *'  # A cada 30 minutos
  # - cron: '0 * * * *'   # A cada hora
  # - cron: '0 */6 * * *' # A cada 6 horas
```

### Mudar período histórico

Edite `.github/workflows/sync.yml`, linha ~28:

```yaml
HISTORICAL_SYNC_DAYS: 180  # Últimos 6 meses em vez de 365
```

### Ajustar tolerância de duplicação

Edite `.github/workflows/sync.yml`:

```yaml
DUPLICATE_TIME_TOLERANCE_SECONDS: 600    # ±10 min em vez de 5
DUPLICATE_DISTANCE_TOLERANCE_METERS: 100 # ±100m em vez de 50
```

## 🐛 Troubleshooting

### Erro: "Authentication failed (Garmin)"
- Verifique email/senha nos Secrets
- Desative 2FA temporariamente no Garmin
- Tente login manual no site Garmin Connect

### Erro: "401 Unauthorized (Nike)"
- Token expirou ou é inválido
- Obtenha novo token: [NIKE-TOKEN-GUIDE.md](NIKE-TOKEN-GUIDE.md)
- Atualize o Secret `NIKE_ACCESS_TOKEN`

### Workflow não executa
- Actions podem ser desativadas após 60 dias sem activity
- Solução: Execute manualmente uma vez
- Actions → Run workflow

### Atividades duplicadas
- Ajuste as tolerâncias (veja "Personalização" acima)
- Delete duplicatas manualmente no Nike
- Próximas sincronizações não duplicarão

## 📱 Teste Prático

1. Faça uma corrida/caminhada com seu Garmin
2. Aguarde 15-30 minutos
3. Abra Nike Run Club
4. ✅ Sua atividade estará sincronizada!

## 💡 Dicas

✨ **Primeira execução** importa todo histórico (2-5 min)  
⚡ **Execuções seguintes** são rápidas (30-60 seg)  
🔒 **Credenciais** nunca aparecem nos logs  
🆓 **100% gratuito** com GitHub Actions  
📊 **2000 min/mês** grátis = ~8000 sincronizações  

## 🎉 Conclusão

Após seguir estes passos, você terá:
- ✅ Sincronização automática funcionando
- ✅ Histórico de corridas importado
- ✅ Sistema rodando 24/7 gratuitamente
- ✅ Logs e monitoramento completos

---

**Dúvidas?** Leia o [README.md](README.md) completo ou abra uma issue!

**Funcionou?** ⭐ Dê uma estrela no repositório!
