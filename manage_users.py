#!/usr/bin/env python3
"""
User Manager CLI
Ferramenta de linha de comando para gerenciar usuários multi-user
"""

import json
import os
import sys
from pathlib import Path


CONFIG_FILE = "config/users.json"
EXAMPLE_FILE = "config/users.example.json"


def load_config():
    """Carrega configuração atual"""
    if not os.path.exists(CONFIG_FILE):
        return {"users": [], "global_settings": {"sync_interval_minutes": 15, "log_level": "INFO"}}
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    """Salva configuração"""
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuração salva em {CONFIG_FILE}")


def list_users():
    """Lista todos os usuários configurados"""
    config = load_config()
    users = config.get('users', [])
    
    if not users:
        print("❌ Nenhum usuário configurado")
        print(f"\nUse: python {sys.argv[0]} add")
        return
    
    print("\n📋 Usuários Configurados:\n")
    print(f"{'ID':<15} {'Nome':<25} {'Status':<10} {'Secrets'}")
    print("-" * 80)
    
    for user in users:
        user_id = user.get('id', 'N/A')
        name = user.get('name', 'N/A')
        enabled = "✅ Ativo" if user.get('enabled', True) else "❌ Inativo"
        
        creds = user.get('credentials', {})
        email_secret = creds.get('garmin_email_secret', 'N/A')
        
        print(f"{user_id:<15} {name:<25} {enabled:<10} {email_secret}")
    
    print(f"\nTotal: {len(users)} usuário(s)")


def add_user():
    """Adiciona novo usuário interativamente"""
    config = load_config()
    
    print("\n➕ Adicionar Novo Usuário\n")
    
    # ID do usuário
    user_id = input("ID do usuário (ex: user1, joao, maria): ").strip()
    if not user_id:
        print("❌ ID não pode estar vazio")
        return
    
    # Verifica se já existe
    existing_ids = [u.get('id') for u in config.get('users', [])]
    if user_id in existing_ids:
        print(f"❌ Usuário com ID '{user_id}' já existe")
        return
    
    # Nome
    name = input("Nome completo: ").strip() or user_id
    
    # Secrets (sugestões automáticas)
    user_id_upper = user_id.upper()
    
    print("\n🔑 Configuração de Secrets:")
    print("(Pressione Enter para usar os valores sugeridos)\n")
    
    email_secret = input(f"Secret Garmin Email [{user_id_upper}_GARMIN_EMAIL]: ").strip()
    if not email_secret:
        email_secret = f"GARMIN_EMAIL_{user_id_upper}"
    
    password_secret = input(f"Secret Garmin Password [{user_id_upper}_GARMIN_PASSWORD]: ").strip()
    if not password_secret:
        password_secret = f"GARMIN_PASSWORD_{user_id_upper}"
    
    nike_secret = input(f"Secret Nike Token [{user_id_upper}_NIKE_TOKEN]: ").strip()
    if not nike_secret:
        nike_secret = f"NIKE_TOKEN_{user_id_upper}"
    
    # Settings
    print("\n⚙️  Configurações:")
    historical_days = input("Dias de histórico [365]: ").strip() or "365"
    time_tolerance = input("Tolerância tempo (segundos) [300]: ").strip() or "300"
    distance_tolerance = input("Tolerância distância (metros) [50]: ").strip() or "50"
    
    # Criar usuário
    new_user = {
        "id": user_id,
        "name": name,
        "enabled": True,
        "credentials": {
            "garmin_email_secret": email_secret,
            "garmin_password_secret": password_secret,
            "nike_token_secret": nike_secret
        },
        "settings": {
            "historical_sync_days": int(historical_days),
            "time_tolerance_seconds": int(time_tolerance),
            "distance_tolerance_meters": int(distance_tolerance)
        }
    }
    
    config['users'].append(new_user)
    save_config(config)
    
    print("\n✅ Usuário adicionado com sucesso!")
    print("\n📝 Próximos passos:")
    print(f"1. Vá em GitHub → Settings → Secrets → Actions")
    print(f"2. Adicione os seguintes secrets:")
    print(f"   - {email_secret}")
    print(f"   - {password_secret}")
    print(f"   - {nike_secret}")
    print(f"3. Se ainda não tiver, adicione: MULTI_USER_MODE = true")
    print(f"4. Commit e push: git add config/users.json && git commit -m 'Add user {user_id}' && git push")


def remove_user():
    """Remove um usuário"""
    config = load_config()
    users = config.get('users', [])
    
    if not users:
        print("❌ Nenhum usuário configurado")
        return
    
    list_users()
    
    print("\n🗑️  Remover Usuário")
    user_id = input("\nID do usuário a remover: ").strip()
    
    # Encontra usuário
    user_to_remove = None
    for user in users:
        if user.get('id') == user_id:
            user_to_remove = user
            break
    
    if not user_to_remove:
        print(f"❌ Usuário '{user_id}' não encontrado")
        return
    
    # Confirmação
    confirm = input(f"Confirma remoção de '{user_to_remove.get('name')}' ({user_id})? (s/N): ").strip().lower()
    if confirm != 's':
        print("❌ Remoção cancelada")
        return
    
    # Remove
    config['users'].remove(user_to_remove)
    save_config(config)
    
    print(f"✅ Usuário '{user_id}' removido")
    print(f"\n📝 Arquivo de histórico 'sync_history_{user_id}.json' pode ser deletado manualmente")


def toggle_user():
    """Ativa/desativa um usuário"""
    config = load_config()
    users = config.get('users', [])
    
    if not users:
        print("❌ Nenhum usuário configurado")
        return
    
    list_users()
    
    print("\n🔄 Ativar/Desativar Usuário")
    user_id = input("\nID do usuário: ").strip()
    
    # Encontra usuário
    user = None
    for u in users:
        if u.get('id') == user_id:
            user = u
            break
    
    if not user:
        print(f"❌ Usuário '{user_id}' não encontrado")
        return
    
    # Toggle
    current_status = user.get('enabled', True)
    user['enabled'] = not current_status
    
    save_config(config)
    
    new_status = "✅ Ativo" if user['enabled'] else "❌ Inativo"
    print(f"✅ Usuário '{user.get('name')}' agora está: {new_status}")


def show_help():
    """Mostra ajuda"""
    print("""
🛠️  User Manager CLI - Gerenciador de Usuários Multi-User

Uso: python manage_users.py [comando]

Comandos:
  list      Lista todos os usuários configurados
  add       Adiciona novo usuário (interativo)
  remove    Remove um usuário
  toggle    Ativa/desativa um usuário
  help      Mostra esta ajuda

Exemplos:
  python manage_users.py list
  python manage_users.py add
  python manage_users.py remove
  python manage_users.py toggle

Documentação completa: MULTI-USER-GUIDE.md
    """)


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_users()
    elif command == 'add':
        add_user()
    elif command == 'remove':
        remove_user()
    elif command == 'toggle':
        toggle_user()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Comando desconhecido: {command}")
        show_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
