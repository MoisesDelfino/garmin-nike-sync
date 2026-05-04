#!/bin/bash

# Script de Setup - Garmin → Nike Sync Web App

set -e

echo "🚀 Garmin → Nike Sync - Web App Setup"
echo "======================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo ""
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo ""
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependências instaladas"

# Configurar variáveis de ambiente
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Criando arquivo .env..."
    
    # Gerar SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Gerar ENCRYPTION_KEY
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=development
FLASK_DEBUG=True

# Database (SQLite local)
DATABASE_URL=sqlite:///garmin_nike_sync.db

# Encryption Key (gerada automaticamente)
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Sync Configuration
SYNC_INTERVAL_MINUTES=15

# Server
PORT=5000
EOF
    
    echo "✅ Arquivo .env criado com chaves geradas"
else
    echo "✅ Arquivo .env já existe"
fi

# Criar diretórios necessários
mkdir -p web/templates web/static/css web/static/js web/models

echo ""
echo "✅ Setup completo!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Execute: source venv/bin/activate"
echo "   2. Execute: python app.py"
echo "   3. Acesse: http://localhost:5000"
echo ""
echo "🎉 Pronto para começar!"
