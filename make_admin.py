#!/usr/bin/env python3
"""
Script para tornar um usuário admin
Uso: python make_admin.py <email_do_usuario>
"""

import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from web.models.database import db, User

def make_admin(email):
    """Torna um usuário admin"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Usuário não encontrado: {email}")
            return False
        
        if user.is_admin:
            print(f"ℹ️  Usuário {email} já é admin")
            return True
        
        user.is_admin = True
        db.session.commit()
        
        print(f"✅ Usuário {email} agora é ADMIN!")
        print(f"   Nome: {user.name}")
        print(f"   ID: {user.id}")
        print(f"\nAcesse: /admin")
        return True

def list_admins():
    """Lista todos os admins"""
    app = create_app()
    
    with app.app_context():
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("Nenhum admin encontrado")
            return
        
        print(f"\n{'ID':<5} {'Nome':<30} {'Email':<40}")
        print("-" * 75)
        for admin in admins:
            print(f"{admin.id:<5} {admin.name:<30} {admin.email:<40}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python make_admin.py <email>")
        print("ou:  python make_admin.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_admins()
    else:
        email = sys.argv[1]
        make_admin(email)
