# 🏃‍♂️ Garmin → Nike Run Club Sync (Web App)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

**Sincronização automática de atividades do Garmin Connect para o Nike Run Club**

[Demo](https://garmin-nike-sync.onrender.com) · [Documentação](#-funcionalidades) · [Deploy](#-deploy)

</div>

---

## 📖 Sobre

Aplicação web que sincroniza automaticamente suas corridas do **Garmin Connect** para o **Nike Run Club**. Configure uma vez e esqueça - suas atividades serão sincronizadas a cada 15 minutos.

### ✨ Principais Funcionalidades

- ✅ **Sincronização Automática** - A cada 15 minutos, sem intervenção manual
- 🔐 **Seguro** - Credenciais criptografadas com AES-256
- 🚫 **Anti-Duplicação** - Detecta e previne atividades duplicadas
- 📊 **Dashboard Completo** - Visualize histórico e estatísticas
- 👥 **Multi-usuário** - Cada pessoa tem sua conta e credenciais
- 🆓 **100% Gratuito** - Deploy em plataformas cloud gratuitas

## 🚀 Quick Start

### 1. Cadastre-se

Acesse a aplicação e crie sua conta gratuita.

### 2. Configure Credenciais

**Garmin Connect:**
- Email e senha da sua conta Garmin

**Nike Run Club:**
- Token de acesso obtido dos cookies do Nike.com

### 3. Pronto!

Ative a sincronização automática e suas corridas serão sincronizadas automaticamente.

## 📸 Screenshots

<details>
<summary>Ver capturas de tela</summary>

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Configuração de Credenciais
![Credentials](docs/screenshots/credentials.png)

### Histórico de Sincronizações
![History](docs/screenshots/history.png)

</details>

## 🛠️ Tecnologias

- **Backend:** Flask 3.0.0
- **Database:** SQLAlchemy + PostgreSQL/SQLite
- **Autenticação:** Flask-Login
- **Criptografia:** Cryptography (Fernet)
- **Scheduler:** APScheduler
- **Frontend:** Bootstrap 5 + Bootstrap Icons
- **APIs:** garth (Garmin), Nike Run Club (reverse engineered)

## 📦 Estrutura do Projeto

```
garmin-nike-sync/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── Procfile              # Deploy Heroku/Render
├── render.yaml           # Configuração Render
├── railway.json          # Configuração Railway
│
├── src/                  # Código fonte core
│   ├── garmin_client.py  # Cliente Garmin Connect
│   ├── nike_client.py    # Cliente Nike Run Club
│   └── synchronizer.py   # Lógica de sincronização
│
├── web/                  # Aplicação web
│   ├── models/
│   │   └── database.py   # Modelos SQLAlchemy
│   ├── templates/        # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── credentials.html
│   │   ├── settings.html
│   │   └── ...
│   ├── static/          # CSS e JavaScript
│   │   ├── css/
│   │   └── js/
│   ├── sync_manager.py  # Gerenciador de sincronização
│   └── scheduler.py     # Scheduler background
│
└── docs/                # Documentação
    └── WEB-DEPLOY-GUIDE.md
```

## 🚀 Deploy

### Opção 1: Render (Recomendado)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork este repositório
2. Conecte ao Render
3. Render detectará `render.yaml` automaticamente
4. Configure variáveis de ambiente (SECRET_KEY, ENCRYPTION_KEY)
5. Deploy!

[Guia completo de deploy →](WEB-DEPLOY-GUIDE.md)

### Opção 2: Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Opção 3: Heroku

```bash
heroku create garmin-nike-sync
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
git push heroku main
heroku open
```

## 🔧 Instalação Local

### Pré-requisitos

- Python 3.10+
- pip

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/garmin-nike-sync.git
cd garmin-nike-sync
```

2. **Crie ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente:**
```bash
export SECRET_KEY=dev-secret-key
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
export DATABASE_URL=sqlite:///garmin_nike_sync.db
```

5. **Execute:**
```bash
python app.py
```

6. **Acesse:**
```
http://localhost:5000
```

## 📝 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório | Padrão |
|----------|-----------|-------------|--------|
| `SECRET_KEY` | Chave secreta Flask | Sim | - |
| `ENCRYPTION_KEY` | Chave Fernet (32 bytes base64) | Sim | - |
| `DATABASE_URL` | URL do banco de dados | Não | SQLite local |
| `SYNC_INTERVAL_MINUTES` | Intervalo de sincronização | Não | 15 |
| `PORT` | Porta do servidor | Não | 5000 |

### Gerar ENCRYPTION_KEY

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## 🔐 Segurança

- **Credenciais Criptografadas:** Todas as credenciais são criptografadas com Fernet (AES-256) antes de serem armazenadas
- **Chave de Criptografia:** Armazenada como variável de ambiente, nunca no código
- **Senhas Hash:** Senhas de usuários usam bcrypt
- **Flask-Login:** Gerenciamento seguro de sessões
- **HTTPS:** Recomendado para produção

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Disclaimer

Este projeto utiliza APIs não oficiais:
- **Garmin Connect:** Via biblioteca `garth` (não oficial)
- **Nike Run Club:** API reverse engineered (não oficial)

O uso dessas APIs pode violar os Termos de Serviço das respectivas plataformas. Use por sua conta e risco.

## 🐛 Problemas Conhecidos

- **Token Nike expira:** O token Nike precisa ser renovado manualmente quando expira (geralmente após alguns meses)
- **Rate Limiting:** APIs podem limitar requisições excessivas
- **Tipos de Atividade:** Atualmente sincroniza apenas corridas (running)

## 📞 Suporte

- 📧 Email: [seu-email@example.com](mailto:seu-email@example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/garmin-nike-sync/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/seu-usuario/garmin-nike-sync/discussions)

## 🎯 Roadmap

- [ ] Suporte para outros tipos de atividade (ciclismo, natação)
- [ ] Renovação automática do token Nike
- [ ] Sincronização bidirecional (Nike → Garmin)
- [ ] API REST para integração com outras apps
- [ ] App mobile (React Native)
- [ ] Webhook notifications
- [ ] Estatísticas avançadas

## 🌟 Agradecimentos

- [garth](https://github.com/matin/garth) - Cliente Garmin Connect
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Bootstrap](https://getbootstrap.com/) - UI Framework
- Comunidade open source ❤️

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela! ⭐**

Feito com ❤️ para corredores

</div>
