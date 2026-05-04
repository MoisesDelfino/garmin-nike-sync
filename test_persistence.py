#!/usr/bin/env python3
"""
Teste de persistência de contas: registro → login → logout → login
"""
import requests
from requests import Session

BASE_URL = "http://localhost:5000"

def test_account_persistence():
    session = Session()
    
    print("=" * 60)
    print("TESTE DE PERSISTÊNCIA DE CONTAS")
    print("=" * 60)
    
    # 1. Criar nova conta
    print("\n1. Criando nova conta...")
    test_email = "testuser@example.com"
    test_password = "senha123"
    
    response = session.post(f"{BASE_URL}/register", data={
        "name": "Test User",
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password
    }, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.headers.get('Location', 'N/A')}")
    
    # 2. Fazer login
    print("\n2. Fazendo login...")
    response = session.post(f"{BASE_URL}/login", data={
        "email": test_email,
        "password": test_password,
        "remember": "on"
    }, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.headers.get('Location', 'N/A')}")
    print(f"   Cookies: {len(session.cookies)} cookie(s)")
    
    # 3. Acessar dashboard
    print("\n3. Acessando dashboard...")
    response = session.get(f"{BASE_URL}/dashboard")
    
    if "Dashboard" in response.text:
        print("   ✓ Dashboard acessível (usuário logado)")
    else:
        print("   ✗ Dashboard não acessível")
    
    # 4. Fazer logout
    print("\n4. Fazendo logout...")
    response = session.get(f"{BASE_URL}/logout", allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.headers.get('Location', 'N/A')}")
    
    # 5. Tentar acessar dashboard (deve redirecionar)
    print("\n5. Tentando acessar dashboard após logout...")
    response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    
    if response.status_code == 302:
        print(f"   ✓ Redirecionado para: {response.headers.get('Location')}")
    else:
        print(f"   ✗ Ainda acessível (status {response.status_code})")
    
    # 6. NOVA SESSÃO - simular fechar e reabrir navegador
    print("\n6. Nova sessão (simulando fechar navegador)...")
    new_session = Session()
    
    # 7. Fazer login novamente
    print("\n7. Fazendo login novamente com nova sessão...")
    response = new_session.post(f"{BASE_URL}/login", data={
        "email": test_email,
        "password": test_password
    }, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.headers.get('Location', 'N/A')}")
    
    # 8. Acessar dashboard com nova sessão
    print("\n8. Acessando dashboard com nova sessão...")
    response = new_session.get(f"{BASE_URL}/dashboard")
    
    if "Dashboard" in response.text:
        print("   ✓ SUCESSO! Conta persiste após logout")
    else:
        print("   ✗ FALHA! Não conseguiu acessar dashboard")
        print(f"   Página: {response.text[:200]}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_account_persistence()
