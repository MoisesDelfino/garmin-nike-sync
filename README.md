# 🏃‍♂️ Garmin → Nike Run Club Sync

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Sincronização automática de corridas do Garmin Connect para o Nike Run Club**

[🌐 Web App](#-web-app-recomendado) • [🤖 GitHub Actions](#-github-actions) • [💻 CLI Local](#-cli-local)

</div>

---

## 🎯 Escolha sua versão

### 🌐 Web App (RECOMENDADO)

**✅ APLICAÇÃO 100% FUNCIONAL E ONLINE**

Interface web completa com dashboard, multi-usuário e sincronização automática.

- ✨ **Interface Web** - Dashboard bonito e fácil de usar
- 👥 **Multi-usuário** - Cada pessoa tem sua conta
- 🔐 **Seguro** - Credenciais criptografadas (AES-256)
- 📊 **Estatísticas** - Veja histórico e logs
- 🚀 **Deploy Grátis** - Render, Railway ou Heroku

**📖 Documentação:**
- [STATUS.md](STATUS.md) - **👈 COMECE AQUI! Status completo e guia de uso**
- [README-WEB.md](README-WEB.md) - Documentação técnica completa
- [WEB-DEPLOY-GUIDE.md](WEB-DEPLOY-GUIDE.md) - Guia de deploy
- [QUICKSTART.md](QUICKSTART.md) - Início rápido

**⚡ Quick Start (LOCAL):**
```bash
./setup.sh         # Configura tudo automaticamente
./start.sh         # Inicia servidor + abre navegador
# Acesse: http://localhost:5000
# Login: admin@garmin-nike-sync.com / admin123
```

**🚀 Status:** ✅ **ONLINE e RODANDO EM https://garmin-nike-sync.onrender.com**

---

### 🤖 GitHub Actions
---

### 🤖 GitHub Actions

Sincronização automática rodando na nuvem (GitHub) sem servidor próprio.

- ⏰ **Automático** - A cada 15 minutos
- 💰 **Gratuito** - 2000 min/mês no GitHub
- 🔒 **Seguro** - Secrets do GitHub
- 👥 **Multi-user** - Suporta múltiplas contas

**📖 Documentação:** Ver seção abaixo ou arquivos originais do projeto

---

### 💻 CLI Local

Execute manualmente no seu computador quando quiser sincronizar.

```bash
pip install -r requirements.txt
python main.py
```

**📖 Documentação completa:** Ver código-fonte e comentários

---

## 📋 Comparação

| Recurso | Web App | GitHub Actions | CLI Local |
|---------|---------|----------------|-----------|
| **Interface** | ✅ Dashboard Web | ❌ Apenas logs | ❌ Terminal |
| **Multi-usuário** | ✅ Sim | ⚠️ Config manual | ❌ Não |
| **Automático** | ✅ Sim (15min) | ✅ Sim (15min) | ❌ Manual |
| **Onde roda** | Render/Railway/Heroku | GitHub (nuvem) | Seu PC |
| **Custo** | 🆓 Grátis | 🆓 Grátis | 🆓 Grátis |
| **Setup** | 3 minutos | 5 minutos | 1 minuto |
| **Recomendado** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🔑 Como Obter Token Nike

O Nike Run Club não tem API oficial. Métodos para obter token:

### Método 1: Browser DevTools (Mais Fácil)
1. Acesse [Nike.com](https://www.nike.com) e faça login
2. Pressione `F12` (DevTools)
3. Vá em: **Application** → **Cookies** → `nike.com`
4. Procure: `com.nike.commerce.nikedotcom.access_token`
5. Copie o valor completo

### Método 2: Mobile App + Proxy
1. Instale [HTTP Toolkit](https://httptoolkit.tech/) ou Charles Proxy
2. Configure proxy no celular
3. Abra Nike Run Club app
4. Intercepte requisições para `api.nike.com`
5. Copie header `Authorization: Bearer <TOKEN>`

⚠️ **Importante:** Token expira (~3 meses). Renove quando necessário.

---

## 📊 Histórico de Desenvolvimento

Este projeto evoluiu através de várias versões:

1. **v1.0** - CLI básico (sincronização manual)
2. **v2.0** - GitHub Actions (automático na nuvem)
3. **v3.0** - Multi-user support (múltiplas contas)
4. **v4.0** - **WEB APP** (interface completa) ⭐ **ATUAL**

---

## 🛠️ Tecnologias

- **Python 3.10+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM banco de dados
- **APScheduler** - Tarefas agendadas
- **Cryptography** - Criptografia de credenciais
- **garth** - Cliente Garmin Connect
- **Bootstrap 5** - UI responsivo

---

## 📄 Licença

MIT License - Use livremente!

---

## ⚠️ Disclaimer

Este projeto usa APIs não oficiais:
- Garmin Connect (via biblioteca `garth`)
- Nike Run Club (API reverse engineered)

O uso pode violar os Termos de Serviço. Use por sua conta e risco.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Abra Issues ou Pull Requests.

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela! ⭐**

**🏃‍♂️ Feito com ❤️ para corredores 💨**

[🌐 Web App](STATUS.md) • [📖 Docs](README-WEB.md) • [🚀 Deploy](WEB-DEPLOY-GUIDE.md)

</div>

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
