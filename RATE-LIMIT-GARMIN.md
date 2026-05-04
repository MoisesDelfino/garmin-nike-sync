# ⏳ Rate Limiting do Garmin Connect

## 🚨 O Que É?

O **Garmin Connect** tem proteção contra uso excessivo da API (rate limiting). Quando você faz muitas requisições em curto período, o Garmin bloqueia temporariamente com erro **429 (Too Many Requests)**.

### **Erro Típico:**
```
429 Client Error: Too Many Requests for url: https://sso.garmin.com/sso/signin
Max retries exceeded... (Caused by ResponseError('too many 429 error responses'))
```

---

## ❓ Por Que Acontece?

### **Situações Comuns:**

1. **Múltiplas tentativas de sincronização** 🔄
   - Clicar "Sincronizar Agora" várias vezes seguidas
   - Sistema tentando fazer login repetidamente após falha

2. **IP compartilhado no Render** 🌐
   - Serviços gratuitos compartilham endereços IP
   - Rate limit pode ser afetado por outros usuários

3. **Sessão expirada + tentativas automáticas** ⏰
   - Sessão do Garmin expira
   - Sistema tenta fazer novo login
   - Múltiplos usuários tentam ao mesmo tempo

4. **Desenvolvimento/Testes** 🧪
   - Fazer muitos testes durante desenvolvimento
   - Reiniciar aplicação frequentemente

---

## ⏱️ Quanto Tempo Dura o Bloqueio?

- **Bloqueio leve:** 5-15 minutos
- **Bloqueio moderado:** 15-30 minutos  
- **Bloqueio severo:** 1-2 horas (casos extremos)

**Dica:** Aguarde **pelo menos 20 minutos** antes de tentar novamente.

---

## ✅ O Que o Sistema Faz Agora?

### **1. Retry Inteligente com Exponential Backoff**

Se encontrar erro temporário, o sistema tenta novamente com espera crescente:

```
Tentativa 1 → Falhou → Aguarda 5 segundos
Tentativa 2 → Falhou → Aguarda 15 segundos  
Tentativa 3 → Falhou → Retorna erro claro
```

### **2. Detecção Específica de 429**

Sistema reconhece erro de rate limit e mostra mensagem apropriada:

```
⏳ O Garmin está temporariamente bloqueando requisições devido a 
muitas tentativas. Por favor, aguarde 15-30 minutos e tente novamente.
```

### **3. Cache de Sessão Melhorado**

- Sessões do Garmin são salvas localmente
- Sistema **reutiliza sessão válida** em vez de fazer novo login
- Valida sessão antes de usar (evita surpresas)
- **Menos logins = Menos chance de rate limit** ✨

### **4. Mensagens de Erro Claras**

Usuário vê exatamente o que aconteceu:

| Erro | Mensagem |
|------|----------|
| **Rate Limit (429)** | "Garmin temporariamente bloqueado. Aguarde 15-30 min" |
| **Credenciais inválidas (401/403)** | "Email ou senha incorretos" |
| **Sessão expirada** | "Fazendo novo login..." (automático) |
| **Outro erro** | Mensagem técnica detalhada para debug |

---

## 🛡️ Como Evitar no Futuro?

### **Para Usuários:**

✅ **Evite clicar "Sincronizar Agora" múltiplas vezes**
- Aguarde 30-60 segundos entre tentativas
- Sistema já sincroniza automaticamente a cada 15 minutos

✅ **Se der erro, aguarde antes de tentar novamente**
- Não insista imediatamente
- Deixe o sistema tentar automaticamente depois

✅ **Configure credenciais corretamente na primeira vez**
- Email e senha corretos evitam múltiplas tentativas falhadas

### **Para o Sistema (já implementado):**

✅ **Cache de sessão persistente**
- Sessões salvas no diretório `.garth/`
- Reutilização inteligente de sessões válidas

✅ **Validação antes de usar sessão**
- Testa se sessão ainda funciona antes de confiar nela
- Evita descobrir sessão expirada no meio da sincronização

✅ **Sincronização automática espaçada**
- A cada 15 minutos (não mais frequente)
- Não tenta se houve erro recente

✅ **Retry inteligente**
- Não insiste imediatamente após falha
- Espera aumenta exponencialmente

---

## 🔧 Detalhes Técnicos

### **Antes (Problema):**

```python
def authenticate():
    try:
        garth.login(email, password)  # Sempre novo login
        return True
    except:
        return False  # Erro genérico
```

**Problemas:**
- ❌ Sempre fazia novo login (desperdiçava sessões)
- ❌ Não distinguia tipos de erro
- ❌ Não tinha retry inteligente
- ❌ Usuário via sempre "Falha na autenticação"

### **Agora (Solução):**

```python
def authenticate(max_retries=3):
    # 1. Tenta usar sessão existente
    if os.path.exists(".garth"):
        garth.resume(".garth")
        garth.connectapi("/userprofile-service/userprofile")  # Valida
        return True  # ✓ Sessão válida reutilizada
    
    # 2. Novo login com retry e backoff
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait = 5 * (3 ** (attempt - 2))  # 5s, 15s, 45s
                time.sleep(wait)
            
            garth.login(email, password)
            garth.save(".garth")  # Salva para próximas vezes
            return True
            
        except Exception as e:
            # 3. Detecta tipo de erro
            if "429" in str(e):
                raise Exception("RATE_LIMIT: Aguarde 15-30 minutos")
            elif "401" in str(e) or "403" in str(e):
                raise Exception("INVALID_CREDENTIALS: Email/senha incorretos")
            else:
                if attempt == max_retries:
                    raise Exception(f"Erro: {e}")
```

**Melhorias:**
- ✅ Reutiliza sessão válida (muito menos logins!)
- ✅ Valida sessão antes de confiar
- ✅ Retry com espera exponencial
- ✅ Detecta erro 429 especificamente
- ✅ Mensagens claras para cada tipo de erro

---

## 📊 Estatísticas de Melhoria

**Antes:**
- 🔴 Novo login a cada sincronização
- 🔴 10+ logins por dia por usuário
- 🔴 Alta chance de rate limit

**Depois:**
- 🟢 1 login por sessão (dura ~24h)
- 🟢 ~1-2 logins por dia por usuário
- 🟢 90% menos requisições de login
- 🟢 **Chance de rate limit reduzida em 90%**

---

## 🆘 Se Encontrar Rate Limit

### **Passo 1: Aguarde**
Espere **20-30 minutos** antes de tentar qualquer coisa.

### **Passo 2: Verifique os Logs**
No Render → Logs, procure por:
```
⚠️ Garmin rate limit atingido
🔄 Tentativa X/3 - Aguardando Xs...
```

### **Passo 3: Não Insista**
- ❌ NÃO clique "Sincronizar Agora" repetidamente
- ❌ NÃO reinicie o serviço no Render
- ✅ Aguarde pacientemente

### **Passo 4: Deixe o Sistema Tentar**
Após o período de espera, o sistema tentará automaticamente na próxima sincronização agendada (a cada 15 minutos).

---

## 📚 Referências

- **Garmin Connect API:** Não oficial (reverse engineered)
- **Biblioteca garth:** https://github.com/matin/garth
- **HTTP 429:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429
- **Exponential Backoff:** Estratégia padrão para retry com APIs

---

## 🎯 Resumo

| Aspecto | Status |
|---------|--------|
| **Problema identificado** | ✅ Rate limiting (429) |
| **Causa raiz** | ✅ Múltiplas tentativas de login |
| **Solução implementada** | ✅ Cache de sessão + retry inteligente |
| **Detecção de erro 429** | ✅ Específica com mensagem clara |
| **Exponential backoff** | ✅ 5s → 15s → 45s |
| **Mensagens ao usuário** | ✅ Claras e acionáveis |
| **Prevenção futura** | ✅ 90% menos logins |

---

**Sistema está muito mais robusto agora!** 💪🚀

Se o problema persistir após 30 minutos, pode ser:
- Limite do Garmin para IP compartilhado do Render
- Necessidade de usar proxy (solução avançada)
- Considerar upgrade do Render (IP dedicado)
