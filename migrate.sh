#!/bin/bash
# Script de migração do banco de dados para Render.com

set -e

echo "=========================================="
echo "🔄 Iniciando migração do banco de dados"
echo "=========================================="

# Verifica se DATABASE_URL está configurado
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL não configurado - usando SQLite local"
    python migrate_db.py
    exit 0
fi

echo "✓ DATABASE_URL configurado"
echo ""

# Tenta executar script Python de migração
echo "📦 Executando Flask-Migrate..."
if python migrate_db.py; then
    echo "✓ Migração via Flask-Migrate concluída"
    exit 0
fi

# Se falhar, tenta SQL direto (fallback)
echo ""
echo "⚠️  Flask-Migrate falhou, tentando SQL direto..."

# Extrai componentes da DATABASE_URL
DB_URL="$DATABASE_URL"

# SQL para adicionar colunas se não existirem
SQL_MIGRATION="
DO \$\$ 
BEGIN
    -- Adiciona nike_email_enc se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_email_enc'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_email_enc TEXT;
        RAISE NOTICE 'Coluna nike_email_enc adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_email_enc já existe';
    END IF;
    
    -- Adiciona nike_password_enc se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_password_enc'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_password_enc TEXT;
        RAISE NOTICE 'Coluna nike_password_enc adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_password_enc já existe';
    END IF;
    
    -- Adiciona nike_status se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_status'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_status VARCHAR(20) DEFAULT 'pending';
        RAISE NOTICE 'Coluna nike_status adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_status já existe';
    END IF;
    
    -- Adiciona nike_status_message se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_status_message'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_status_message TEXT;
        RAISE NOTICE 'Coluna nike_status_message adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_status_message já existe';
    END IF;
    
    -- Adiciona nike_configured_at se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_configured_at'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_configured_at TIMESTAMP;
        RAISE NOTICE 'Coluna nike_configured_at adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_configured_at já existe';
    END IF;
    
    -- Adiciona is_admin se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='is_admin'
    ) THEN
        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Coluna is_admin adicionada';
    ELSE
        RAISE NOTICE 'Coluna is_admin já existe';
    END IF;
END \$\$;
"
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='nike_password_enc'
    ) THEN
        ALTER TABLE users ADD COLUMN nike_password_enc TEXT;
        RAISE NOTICE 'Coluna nike_password_enc adicionada';
    ELSE
        RAISE NOTICE 'Coluna nike_password_enc já existe';
    END IF;
END \$\$;
"

# Executa SQL via psql (se disponível) ou Python
if command -v psql &> /dev/null; then
    echo "Executando via psql..."
    echo "$SQL_MIGRATION" | psql "$DB_URL"
    echo "✓ Migração SQL concluída"
else
    echo "Executando via Python..."
    python -c "
import os
import psycopg2
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'])
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    user=url.username,
    password=url.password,
    database=url.path[1:]
)
cur = conn.cursor()
cur.execute('''$SQL_MIGRATION''')
conn.commit()
cur.close()
conn.close()
print('✓ Migração SQL concluída')
    "
fi

echo ""
echo "=========================================="
echo "✅ Migração concluída com sucesso!"
echo "=========================================="
