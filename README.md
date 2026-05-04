# 🏃 Garmin → Nike Run Club Sync

Sincronização automática de atividades do **Garmin Connect** para o **Nike Run Club** usando GitHub Actions.

[![Sync Status](https://github.com/SEU_USUARIO/garmin-nike-sync/actions/workflows/sync.yml/badge.svg)](https://github.com/SEU_USUARIO/garmin-nike-sync/actions)

## 🎯 Características

- ✅ **100% Gratuito** - Roda no GitHub Actions (2000 min/mês grátis)
- ⏰ **Automático** - Sincroniza a cada 15 minutos
- 🔄 **Sincronização Histórica** - Importa atividades antigas (até 365 dias)
- 🚫 **Anti-Duplicação** - Detecta e evita atividades duplicadas
- 📊 **Logs Detalhados** - Histórico completo de sincronizações
- 🔒 **Seguro** - Credenciais armazenadas em GitHub Secrets
- 👥 **Multi-User** - Suporta múltiplas contas no mesmo repositório ([guia](MULTI-USER-GUIDE.md))

## 👤 Single-User vs 👥 Multi-User

### Single-User (Padrão)
✅ Uma conta Garmin → Uma conta Nike  
✅ Setup mais simples (3 secrets)  
✅ Ideal para uso pessoal  

**Setup:** [QUICKSTART.md](QUICKSTART.md)

### Multi-User (Avançado)
✅ Múltiplas contas Garmin → Múltiplas contas Nike  
✅ Configuração por arquivo JSON  
✅ Ideal para família/amigos  
✅ Históricos e configurações separadas  

**Setup:** [MULTI-USER-GUIDE.md](MULTI-USER-GUIDE.md)

## 📋 Como Funciona

```
┌──────────────┐      ┌─────────────────┐      ┌──────────────┐
│   Garmin     │──────>│  GitHub Actions │──────>│  Nike Run    │
│   Connect    │ A cada│  (Python Script)│ Envia │  Club        │
└──────────────┘ 15min└─────────────────┘ treino└──────────────┘
```

1. **A cada 15 minutos**, o GitHub Actions executa automaticamente
2. **Busca** novas atividades no Garmin Connect
3. **Verifica** se já existem no Nike Run Club (data/hora + distância)
4. **Sincroniza** apenas atividades novas
5. **Salva** histórico no próprio repositório

## 🚀 Setup Rápido (5 minutos)

### 1️⃣ Fork este Repositório

Clique em **Fork** no canto superior direito desta página.

### 2️⃣ Configure os Secrets

Vá em **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

Adicione 3 secrets:

| Secret | Descrição | Onde obter |
|--------|-----------|------------|
| `GARMIN_EMAIL` | Seu email do Garmin | Email da sua conta Garmin Connect |
| `GARMIN_PASSWORD` | Sua senha do Garmin | Senha da sua conta Garmin Connect |
| `NIKE_ACCESS_TOKEN` | Token Nike Run Club | 👉 [Veja tutorial abaixo](#obter-token-nike) |

### 3️⃣ Ative o GitHub Actions

1. Vá na aba **Actions**
2. Clique em **"I understand my workflows, go ahead and enable them"**
3. Selecione o workflow **"Garmin → Nike Sync"**
4. Clique em **"Enable workflow"**

### 4️⃣ Execute Manualmente (Primeira Vez)

1. Na aba **Actions**, clique no workflow **"Garmin → Nike Sync"**
2. Clique em **"Run workflow"** > **"Run workflow"**
3. Aguarde ~2-5 minutos
4. ✅ Suas atividades foram sincronizadas!

## 🔑 Obter Token Nike

O Nike Run Club não tem API oficial. Use um dos métodos:

### Método 1: Inspecionar App Mobile (iOS/Android)

1. Instale um proxy HTTP no seu celular (ex: [Charles Proxy](https://www.charlesproxy.com/), [HTTP Toolkit](https://httptoolkit.tech/))
2. Configure para interceptar tráfego HTTPS
3. Abra o app Nike Run Club
4. Faça login
5. Procure requisições para `api.nike.com`
6. Copie o header `Authorization: Bearer YOUR_TOKEN_HERE`
7. Use apenas a parte `YOUR_TOKEN_HERE`

### Método 2: Navegador Desktop

1. Abra [Nike.com](https://www.nike.com/)
2. Faça login
3. Pressione **F12** (DevTools)
4. Vá na aba **Application** > **Cookies** > `nike.com`
5. Procure cookie chamado `access_token` ou similar
6. Copie o valor

### Método 3: API Reversa (Avançado)

```bash
# Exemplo de como obter token via API
curl -X POST https://unite.nike.com/loginWithSetCookie \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH",
    "ux_id": "com.nike.sport.running.ios.5.44",
    "grant_type": "password",
    "username": "seu_email@exemplo.com",
    "password": "sua_senha"
  }'
```

⚠️ **Importante**: O token Nike expira. Você precisará renová-lo periodicamente (a cada 30-90 dias).

## ⚙️ Configuração Avançada

Edite o arquivo [.github/workflows/sync.yml](.github/workflows/sync.yml):

```yaml
env:
  SYNC_INTERVAL_MINUTES: 15        # Intervalo de sincronização
  HISTORICAL_SYNC_DAYS: 365        # Dias de histórico (primeira execução)
  DUPLICATE_TIME_TOLERANCE_SECONDS: 300    # ±5 minutos
  DUPLICATE_DISTANCE_TOLERANCE_METERS: 50  # ±50 metros
```

### Mudar Frequência de Sincronização

No arquivo `sync.yml`, linha 6:

```yaml
schedule:
  - cron: '*/15 * * * *'  # A cada 15 minutos
  # - cron: '0 * * * *'   # A cada hora
  # - cron: '0 */6 * * *' # A cada 6 horas
```

## 📊 Monitoramento

### Ver Logs de Execução

1. Vá na aba **Actions**
2. Clique na execução desejada
3. Expanda **"🔄 Run sync"**

### Ver Histórico

O arquivo `sync_history.json` é automaticamente commitado:
- Lista todas as atividades sincronizadas
- Mapeia ID Garmin → ID Nike
- Registra data/hora da sincronização

## 🛠️ Execução Local (Desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/garmin-nike-sync.git
cd garmin-nike-sync

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
nano .env  # Edite com suas credenciais

# Execute
python main.py
```

## 🤔 FAQ

### Por que usar GitHub Actions?

- ✅ Totalmente gratuito (2000 min/mês)
- ✅ Não precisa deixar PC ligado
- ✅ Execução agendada confiável
- ✅ Logs e histórico automáticos

### As credenciais são seguras?

Sim! GitHub Secrets são criptografados e **nunca** aparecem nos logs.

### Quanto tempo demora cada sincronização?

- Primeira execução (histórico): 2-5 minutos
- Execuções subsequentes: 30-60 segundos

### Quais atividades são sincronizadas?

Apenas corridas e caminhadas:
- Running (todos os tipos)
- Trail running
- Treadmill
- Walking

### Como desativar?

1. Vá em **Actions** > **"Garmin → Nike Sync"**
2. Clique nos 3 pontos `...` > **"Disable workflow"**

### Token Nike expirou, e agora?

1. Obtenha novo token (veja [tutorial acima](#obter-token-nike))
2. Atualize o secret `NIKE_ACCESS_TOKEN` no GitHub
3. Pronto! Próxima execução usará novo token

## 🐛 Troubleshooting

### Erro: "Authentication failed (Garmin)"

- Verifique email/senha nos Secrets
- Garmin pode ter pedido verificação de 2 fatores
- Tente fazer login manual no Garmin Connect

### Erro: "Invalid token (Nike)"

- Token expirou, obtenha um novo
- Certifique-se de copiar o token completo
- Não inclua `Bearer ` no secret, apenas o token

### Sincronização não está rodando

- Verifique se workflow está ativado em **Actions**
- GitHub pode desativar workflows após 60 dias de inatividade
- Execute manualmente uma vez para reativar

### Atividades duplicadas

Ajuste as tolerâncias no `sync.yml`:
```yaml
DUPLICATE_TIME_TOLERANCE_SECONDS: 600    # ±10 min em vez de 5
DUPLICATE_DISTANCE_TOLERANCE_METERS: 100 # ±100m em vez de 50
```

## 📝 Licença

MIT License - Sinta-se livre para usar e modificar!

## 🤝 Contribuições

Pull requests são bem-vindos!

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
