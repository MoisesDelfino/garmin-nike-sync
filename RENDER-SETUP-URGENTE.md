# INSTRUÇÕES URGENTES - Configurar PostgreSQL no Render

## 🚨 PROBLEMA IDENTIFICADO

DATABASE_URL não está configurado no Render. O serviço está usando SQLite efêmero.

## ✅ SOLUÇÃO (5 minutos)

### 1. Criar PostgreSQL Database

1. Acesse: https://dashboard.render.com
2. Clique em **"New" → "PostgreSQL"**
3. Configure:
   - **Name:** `garmin-nike-sync-db`
   - **Database:** `garmin_nike_sync`  
   - **Region:** Oregon (mesmo que web service)
   - **PostgreSQL Version:** 16
   - **Plan:** **Free**
4. Clique **"Create Database"**
5. Aguarde ~2 minutos (provisionamento)

### 2. Conectar DATABASE_URL ao Web Service

1. **Copie a URL do banco:**
   - No banco criado, vá em aba **"Info"**
   - Copie **"Internal Database URL"** (postgresql://...)

2. **Configure no Web Service:**
   - Vá no serviço **"garmin-nike-sync"**
   - Menu **"Environment"** (lado esquerdo)
   - Clique **"Add Environment Variable"**
   - **Key:** `DATABASE_URL`
   - **Value:** Cole a URL copiada
   - Clique **"Save Changes"**

3. **Aguarde redeploy automático** (~2 minutos)

### 3. Verificar Logs

Após redeploy, deve aparecer:

```
✓ DATABASE_URL: postgresql://...
🔄 Iniciando migração do banco de dados
✓ Migração concluída
```

## 🎯 RESULTADO ESPERADO

- ✅ Contas persistentes (não somem após logout)
- ✅ Banco PostgreSQL gratuito (1GB)
- ✅ Site totalmente funcional

## ⚡ ALTERNATIVA RÁPIDA (Recriar tudo)

Se preferir começar do zero:

1. **Delete serviço atual:**
   - garmin-nike-sync → Settings → Delete Service

2. **Crie via Blueprint:**
   - New → Blueprint
   - Conecte repositório: MoisesDelfino/garmin-nike-sync
   - Render cria automaticamente:
     - Web Service
     - PostgreSQL Database
     - Conecta DATABASE_URL

---

**Escolha uma opção e execute agora!** 🚀
