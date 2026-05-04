#!/usr/bin/env python3
"""
Script de teste para criar usuário e validar funcionalidades
"""

import os
import sys
from app import create_app
from web.models.database import db, User

def test_database():
    """Testa conexão com banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    
    app = create_app({'TESTING': True})
    
    with app.app_context():
        # Verifica se as tabelas foram criadas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"✅ Tabelas encontradas: {', '.join(tables)}")
        
        return True

def create_test_user(email="test@example.com", password="test123", name="Test User"):
    """Cria um usuário de teste"""
    print(f"\n👤 Criando usuário de teste: {email}")
    
    app = create_app({'TESTING': True})
    
    with app.app_context():
        # Verifica se já existe
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"⚠️  Usuário {email} já existe")
            return existing
        
        # Cria novo usuário
        user = User(email=email, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.name}")
        
        return user

def list_users():
    """Lista todos os usuários"""
    print("\n📋 Listando usuários...")
    
    app = create_app({'TESTING': True})
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("   Nenhum usuário encontrado")
        else:
            for user in users:
                print(f"   - {user.email} ({user.name}) - ID: {user.id}")
                print(f"     Criado em: {user.created_at}")
                print(f"     Último sync: {user.last_sync or 'Nunca'}")
                print(f"     Total sincronizado: {user.total_synced}")
                print(f"     Sync ativo: {'Sim' if user.sync_enabled else 'Não'}")
                print()

def test_user_credentials():
    """Testa criptografia de credenciais"""
    print("\n🔐 Testando criptografia de credenciais...")
    
    app = create_app({'TESTING': True})
    
    with app.app_context():
        user = User.query.first()
        
        if not user:
            print("❌ Nenhum usuário encontrado")
            return False
        
        # Testa Garmin
        print(f"   Testando credenciais Garmin...")
        user.set_garmin_credentials("test@garmin.com", "garmin_password_123")
        db.session.commit()
        
        email, password = user.get_garmin_credentials()
        
        if email == "test@garmin.com" and password == "garmin_password_123":
            print(f"   ✅ Garmin: Criptografia funcionando")
        else:
            print(f"   ❌ Garmin: Erro na criptografia")
            return False
        
        # Testa Nike
        print(f"   Testando token Nike...")
        user.set_nike_token("nike_token_abc123xyz")
        db.session.commit()
        
        token = user.get_nike_token()
        
        if token == "nike_token_abc123xyz":
            print(f"   ✅ Nike: Criptografia funcionando")
        else:
            print(f"   ❌ Nike: Erro na criptografia")
            return False
        
        print(f"✅ Todas as credenciais criptografadas corretamente")
        return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🧪 Garmin → Nike Sync - Suite de Testes")
    print("=" * 60)
    
    try:
        # 1. Testa banco de dados
        test_database()
        
        # 2. Cria usuário de teste
        create_test_user(
            email="admin@garmin-nike-sync.com",
            password="admin123",
            name="Admin"
        )
        
        # 3. Lista usuários
        list_users()
        
        # 4. Testa criptografia
        test_user_credentials()
        
        print("\n" + "=" * 60)
        print("✅ Todos os testes passaram!")
        print("=" * 60)
        print("\n📝 Credenciais de teste:")
        print("   Email: admin@garmin-nike-sync.com")
        print("   Senha: admin123")
        print("\n🚀 Acesse: http://localhost:5000")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
