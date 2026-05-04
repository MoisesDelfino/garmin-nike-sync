#!/usr/bin/env python3
"""
Database Migration Script
Inicializa migrações e aplica alterações no banco de dados
"""

import os
import sys
from flask_migrate import init, migrate, upgrade
from app import create_app
from web.models.database import db

def run_migrations():
    """Executa migrações do banco de dados"""
    
    app = create_app()
    
    with app.app_context():
        migrations_dir = 'migrations'
        
        # Verifica se já existe diretório de migrações
        if not os.path.exists(migrations_dir):
            print("📦 Inicializando Flask-Migrate...")
            try:
                init()
                print("✓ Flask-Migrate inicializado")
            except Exception as e:
                print(f"⚠️  Aviso ao inicializar: {e}")
        
        # Cria migração automática
        print("\n📝 Gerando migração automática...")
        try:
            migrate(message="Add nike_email_enc and nike_password_enc fields")
            print("✓ Migração gerada")
        except Exception as e:
            print(f"⚠️  Aviso ao gerar migração: {e}")
        
        # Aplica migrações
        print("\n🚀 Aplicando migrações ao banco de dados...")
        try:
            upgrade()
            print("✓ Migrações aplicadas com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao aplicar migrações: {e}")
            # Se falhar, tenta criar tabelas diretamente
            print("\n⚠️  Tentando criar tabelas diretamente...")
            try:
                db.create_all()
                print("✓ Tabelas criadas com sucesso!")
                return True
            except Exception as e2:
                print(f"❌ Erro ao criar tabelas: {e2}")
                return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
