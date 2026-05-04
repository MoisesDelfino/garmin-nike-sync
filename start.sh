#!/bin/bash

# Script para iniciar a aplicação e abrir no navegador

echo "🚀 Iniciando Garmin → Nike Sync..."
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Execute primeiro: ./setup.sh"
    exit 1
fi

# Ativa ambiente virtual
source venv/bin/activate

# Inicia servidor Flask em background
echo "📡 Iniciando servidor Flask..."
python app.py > /dev/null 2>&1 &
SERVER_PID=$!

# Aguarda servidor iniciar
echo "⏳ Aguardando servidor inicializar..."
sleep 3

# Verifica se está rodando
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Servidor rodando (PID: $SERVER_PID)"
    echo ""
    echo "🌐 Aplicação disponível em:"
    echo "   http://localhost:5000"
    echo "   http://127.0.0.1:5000"
    echo ""
    echo "📝 Credenciais de teste:"
    echo "   Email: admin@garmin-nike-sync.com"
    echo "   Senha: admin123"
    echo ""
    
    # Abre navegador
    echo "🌍 Abrindo navegador..."
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5000 2>/dev/null
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:5000 2>/dev/null
    elif command -v open > /dev/null; then
        open http://localhost:5000 2>/dev/null
    else
        echo "⚠️  Não foi possível abrir o navegador automaticamente"
        echo "   Abra manualmente: http://localhost:5000"
    fi
    
    echo ""
    echo "✋ Para parar o servidor: kill $SERVER_PID"
    echo "   ou pressione CTRL+C e execute: kill $SERVER_PID"
    echo ""
    echo "🎉 Aplicação rodando!"
    
    # Mantém script rodando
    wait $SERVER_PID
else
    echo "❌ Erro ao iniciar servidor"
    exit 1
fi
