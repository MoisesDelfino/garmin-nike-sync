# 🔑 Como Obter o Token Nike Run Club

O Nike Run Club não oferece API pública oficial. Este guia mostra como extrair seu token de acesso pessoal para uso na sincronização.

## ⚠️ Avisos Importantes

- **Use apenas SEU próprio token** (da sua conta Nike)
- **Não compartilhe** seu token com ninguém
- Token expira após ~30-90 dias (precisará renovar)
- Este método é para uso pessoal apenas

## Método 1: Charles Proxy (iOS) - Mais Fácil

### Requisitos
- iPhone/iPad com Nike Run Club instalado
- [Charles Proxy](https://www.charlesproxy.com/) (trial gratuito)
- Computador na mesma rede Wi-Fi

### Passo a Passo

1. **Instale Charles Proxy no computador**
   ```
   https://www.charlesproxy.com/download/
   ```

2. **Configure o iPhone**
   - Abra Ajustes > Wi-Fi
   - Toque no (i) da sua rede
   - Role até "Proxy HTTP"
   - Selecione "Manual"
   - Servidor: IP do seu computador
   - Porta: 8888

3. **Instale certificado SSL**
   - No iPhone, abra Safari
   - Vá para: `chls.pro/ssl`
   - Instale o certificado
   - Ajustes > Geral > Sobre > Certificados Confiáveis
   - Ative "Charles Proxy CA"

4. **Capture o token**
   - Abra Charles Proxy no computador
   - No iPhone, abra Nike Run Club
   - Faça logout e login novamente
   - No Charles, procure por requisições para `api.nike.com`
   - Expanda uma requisição
   - Na aba "Request", procure header `Authorization`
   - Copie o valor após `Bearer `

5. **Limpe configurações**
   - Volte proxy do iPhone para "Desligado"

## Método 2: HTTP Toolkit (Android/iOS) - Gratuito

### Requisitos
- [HTTP Toolkit](https://httptoolkit.tech/) (gratuito)
- Celular Android ou iOS

### Passo a Passo

1. **Instale HTTP Toolkit**
   ```bash
   # Linux/Mac
   wget https://github.com/httptoolkit/httptoolkit-desktop/releases/latest/download/HttpToolkit.AppImage
   chmod +x HttpToolkit.AppImage
   ./HttpToolkit.AppImage
   ```

2. **Configure o dispositivo móvel**
   - Abra HTTP Toolkit
   - Clique em "Android Device via ADB" ou "iOS Device"
   - Siga as instruções na tela

3. **Capture o token**
   - Com HTTP Toolkit interceptando
   - Abra Nike Run Club
   - Faça login
   - Na interface do HTTP Toolkit, filtre por `api.nike.com`
   - Procure header `Authorization: Bearer ...`
   - Copie o token

## Método 3: Navegador (Desktop) - Menos Confiável

### Para Nike.com

1. Abra [nike.com](https://www.nike.com/)
2. Faça login
3. Pressione **F12** para abrir DevTools
4. Vá na aba **Application** (Chrome) ou **Storage** (Firefox)
5. Expanda **Cookies** > `https://www.nike.com`
6. Procure por cookies como:
   - `nike_access_token`
   - `access_token`
   - `authorization`
7. Copie o valor

⚠️ **Nota**: Token do site pode não funcionar com a API mobile

## Método 4: API OAuth (Programático)

### Requisitos
- Python 3 ou Node.js
- Credenciais Nike

### Script Python

```python
import requests

# IDs de cliente conhecidos da Nike
CLIENT_ID = "HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH"  # Nike Run Club iOS
UX_ID = "com.nike.sport.running.ios.5.44"

def get_nike_token(email, password):
    """Obtém token Nike via OAuth"""
    
    url = "https://unite.nike.com/loginWithSetCookie"
    
    payload = {
        "client_id": CLIENT_ID,
        "ux_id": UX_ID,
        "grant_type": "password",
        "username": email,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Nike/5.44.0 (iPhone; iOS 15.0)"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        print(f"✅ Token obtido com sucesso!")
        print(f"\nAccess Token:\n{access_token}\n")
        print(f"Expires in: {data.get('expires_in')} segundos")
        return access_token
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return None

# Uso
if __name__ == "__main__":
    email = input("Email Nike: ")
    password = input("Senha Nike: ")
    
    token = get_nike_token(email, password)
```

Salve como `get_nike_token.py` e execute:
```bash
python get_nike_token.py
```

## Método 5: Usar Token de Outra Ferramenta

Se você já usa outra ferramenta de sincronização (ex: Strava, Runalyze), ela pode ter o token Nike armazenado:

### No Linux/Mac
```bash
# Procura por tokens em arquivos de configuração
grep -r "nike.*token\|access.*token" ~/.config/ 2>/dev/null
grep -r "nike.*token\|access.*token" ~/.local/share/ 2>/dev/null
```

## 🔄 Renovar Token Expirado

Quando o token expirar (você verá erro `401 Unauthorized`):

1. Use um dos métodos acima para obter novo token
2. Atualize no GitHub:
   - Vá em **Settings** > **Secrets and variables** > **Actions**
   - Clique em `NIKE_ACCESS_TOKEN`
   - Clique em **Update secret**
   - Cole o novo token
3. Próxima execução usará o novo token automaticamente

## 📱 Apps que Facilitam

Alguns apps podem facilitar a extração:

- **[Requestly](https://requestly.io/)** - Intercepta requisições no navegador
- **[Proxyman](https://proxyman.io/)** - Proxy nativo para Mac
- **[Fiddler](https://www.telerik.com/fiddler)** - Proxy para Windows

## 🆘 Ajuda

### Token não funciona

- Certifique-se de copiar **apenas** o token, sem `Bearer `
- Remova espaços ou quebras de linha
- Verifique se copiou o token completo

### Nike pede 2FA

- Complete verificação no app/site
- Token só funcionará após verificar identidade

### API retorna 403 Forbidden

- Token pode estar expirado
- Nike pode ter detectado uso não-oficial
- Aguarde algumas horas e tente novamente

---

**💡 Dica**: Salve o token em local seguro (gerenciador de senhas) para facilitar renovação futura.
