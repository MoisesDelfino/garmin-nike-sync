# 🚀 Guia de Deploy - Garmin → Nike Sync Web App

Este guia explica como fazer deploy da aplicação web em plataformas cloud gratuitas.

## 📋 Pré-requisitos

- Conta no Render, Heroku, Railway ou similar
- Repositório Git (GitHub, GitLab, etc.)
- Python 3.10+

## 🔑 Variáveis de Ambiente Necessárias

Configure estas variáveis antes do deploy:

```bash
SECRET_KEY=<chave-secreta-aleatória>
ENCRYPTION_KEY=<chave-fernet-32-bytes-base64>
DATABASE_URL=<url-do-banco-postgresql>
SYNC_INTERVAL_MINUTES=15  # Opcional, padrão é 15
PORT=5000  # Geralmente configurado automaticamente
```

### Gerando ENCRYPTION_KEY

Execute no terminal:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Ou use este comando:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Exemplo de saída:
```
aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789ABCD=
```

## 🎯 Opção 1: Deploy no Render (Recomendado)

### 1. Preparação

Certifique-se de que o arquivo `render.yaml` existe no repositório (já incluído).

### 2. Deploy

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório GitHub
4. Render detectará automaticamente o `render.yaml`
5. Clique em "Apply"
6. Aguarde o deploy (5-10 minutos)

### 3. Configurar Variáveis

Após o deploy:

1. Vá para o serviço criado
2. "Environment" → "Environment Variables"
3. Adicione/edite:
   - `SECRET_KEY` - gere uma chave aleatória
   - `ENCRYPTION_KEY` - use o comando acima
4. Salve e aguarde reinicialização

### 4. Banco de Dados

O Render criará automaticamente um PostgreSQL gratuito (500MB).

## 🎯 Opção 2: Deploy no Railway

### 1. Preparação

O arquivo `railway.json` já está configurado.

### 2. Deploy

1. Acesse [Railway](https://railway.app/)
2. "New Project" → "Deploy from GitHub repo"
3. Selecione o repositório
4. Railway detectará automaticamente Python

### 3. Adicionar Banco de Dados

1. No projeto, clique em "New" → "Database" → "PostgreSQL"
2. Railway criará automaticamente a variável `DATABASE_URL`

### 4. Configurar Variáveis

1. Clique no serviço web
2. "Variables" tab
3. Adicione:
   - `SECRET_KEY`
   - `ENCRYPTION_KEY`
4. Salve (deploy automático)

## 🎯 Opção 3: Deploy no Heroku

### 1. Instalação do CLI

```bash
# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# macOS
brew tap heroku/brew && brew install heroku
```

### 2. Login

```bash
heroku login
```

### 3. Criar App

```bash
cd garmin-nike-sync
heroku create garmin-nike-sync-<seu-nome>
```

### 4. Adicionar PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### 5. Configurar Variáveis

```bash
# Gerar SECRET_KEY
heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Gerar ENCRYPTION_KEY
heroku config:set ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Intervalo de sincronização (opcional)
heroku config:set SYNC_INTERVAL_MINUTES=15
```

### 6. Deploy

```bash
git push heroku main
```

### 7. Abrir App

```bash
heroku open
```

## 🎯 Opção 4: Deploy Local (Desenvolvimento)

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis

Crie arquivo `.env`:

```bash
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
DATABASE_URL=sqlite:///garmin_nike_sync.db
SYNC_INTERVAL_MINUTES=15
```

### 3. Iniciar App

```bash
python app.py
```

Acesse: http://localhost:5000

## 📊 Monitoramento

### Logs

**Render:**
```bash
# Via dashboard ou CLI
render logs <service-name>
```

**Railway:**
```bash
# Via dashboard
```

**Heroku:**
```bash
heroku logs --tail
```

### Verificar Sincronização

1. Faça login no app
2. Vá para Dashboard
3. Verifique "Última Sincronização"
4. Acesse a aba "Logs" para detalhes

## 🔧 Troubleshooting

### Erro: "ENCRYPTION_KEY not set"

Configure a variável de ambiente:

```bash
# Gerar nova chave
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Configurar no Render/Railway/Heroku
```

### Erro: "Database connection failed"

Verifique se `DATABASE_URL` está configurado corretamente:

```bash
# Render/Railway - geralmente automático
# Heroku
heroku config:get DATABASE_URL
```

### Sincronização não está rodando

1. Verifique se o scheduler está ativo (logs)
2. Verifique se há usuários com `sync_enabled=True`
3. Verifique se as credenciais estão configuradas

### Token Nike expirou

1. Faça login no app
2. Vá para "Credenciais"
3. Atualize o Nike Access Token

## 📈 Limites das Plataformas Gratuitas

### Render
- ✅ 750 horas/mês
- ✅ 500MB PostgreSQL
- ❌ Sleep após 15min inativo
- ❌ Reinicia a cada mês

### Railway
- ✅ $5 crédito/mês grátis
- ✅ Banco PostgreSQL incluído
- ✅ Sempre ativo
- ❌ Limite de $5/mês

### Heroku
- ✅ 1000 horas/mês (com cartão)
- ✅ PostgreSQL 10K linhas
- ❌ Sleep após 30min inativo
- ❌ Pago após limite

## 🔄 Atualização do App

### Via Git

```bash
git pull origin main
git push heroku main  # ou railway/render via git
```

### Via Dashboard

Render e Railway fazem deploy automático ao detectar mudanças no repositório.

## 🎉 Pronto!

Seu app está no ar! Acesse a URL fornecida pela plataforma e comece a sincronizar suas corridas.

**Próximos passos:**
1. Cadastre-se no app
2. Configure credenciais Garmin e Nike
3. Ative a sincronização automática
4. Faça uma corrida e veja a mágica acontecer! 🏃‍♂️
