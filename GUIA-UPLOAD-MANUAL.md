# 📤 Guia de Upload Manual de Atividades

## 🎯 O Que É?

Uma alternativa ao sincronização automática que **não usa a API do Garmin**, evitando completamente o problema de rate limit (erro 429).

## 🔄 Como Funciona?

```
Você Manualmente → Garmin Connect → Exporta Arquivo → Upload na Ferramenta → Nike Run Club
```

**Zero requisições ao Garmin API = Zero bloqueios!** ✅

## 📋 Passo a Passo

### 1. Exportar do Garmin Connect

1. Acesse [connect.garmin.com](https://connect.garmin.com)
2. Clique em uma atividade que deseja sincronizar
3. Clique no ícone **⚙️** (configurações) no canto superior direito
4. Selecione uma das opções:
   - **"Exportar Original"** (recomendado - formato .FIT)
   - **"Exportar para TCX"**
   - **"Exportar para GPX"**
5. O arquivo será baixado no seu computador

### 2. Upload na Ferramenta

1. Acesse a ferramenta e faça login
2. Clique em **"📤 Upload Manual"** no menu
3. Arraste os arquivos para a área indicada OU clique para selecionar
4. Você pode selecionar **múltiplos arquivos** de uma vez
5. Clique em **"Enviar para Nike Run Club"**
6. Aguarde o processamento
7. ✅ Pronto! Suas atividades estão no Nike!

## 📁 Formatos Suportados

| Formato | Extensão | Descrição |
|---------|----------|-----------|
| **FIT** | `.fit` | Formato nativo Garmin (recomendado) |
| **TCX** | `.tcx` | Training Center XML |
| **GPX** | `.gpx` | GPS Exchange Format |

## 📊 Dados Sincronizados

A ferramenta extrai automaticamente:

- ✅ Tipo de atividade (corrida, ciclismo, caminhada)
- ✅ Data e hora de início
- ✅ Duração total
- ✅ Distância percorrida
- ✅ Calorias queimadas (se disponível)
- ✅ Frequência cardíaca média (se disponível)
- ✅ Dados de GPS/rota (se disponível)

## 💡 Dicas

### Upload em Lote

Você pode exportar várias atividades do Garmin e fazer upload de todas de uma vez:

1. Exporte múltiplas atividades (uma por uma, infelizmente)
2. Selecione todos os arquivos `.fit` baixados
3. Arraste todos de uma vez para a ferramenta
4. Clique em "Enviar" - todas serão processadas

### Quando Usar?

**Use Upload Manual quando:**
- 🚫 A sincronização automática está em cooldown (erro 429)
- 📅 Quer sincronizar atividades antigas específicas
- ⚡ Precisa de resultado imediato
- 🎯 Quer controle total sobre o que sincroniza

**Use Sincronização Automática quando:**
- 🔄 Quer que novas atividades sejam sincronizadas sozinhas
- ⏰ Não se importa em esperar até 60 minutos
- 😌 Prefere não fazer nada manualmente

### Vantagens vs Desvantagens

| Upload Manual | Sincronização Automática |
|---------------|--------------------------|
| ✅ Nunca dá erro 429 | ❌ Pode dar erro 429 |
| ✅ Resultado imediato | ⏰ Espera até 60 min |
| ✅ Você escolhe o que sync | 🔄 Sincroniza tudo automaticamente |
| ⚠️ Trabalho manual | ✅ Zero trabalho |
| ⚠️ Precisa exportar do Garmin | ✅ Não precisa fazer nada |

## 🔒 Segurança

- Os arquivos são processados **temporariamente**
- Não são armazenados no servidor
- Apenas os metadados vão para o banco de dados
- Seus dados de GPS não são salvos

## ❓ Problemas Comuns

### "Arquivo com dados inválidos"

**Causa:** Arquivo corrompido ou incompleto

**Solução:**
1. Exporte novamente do Garmin
2. Use "Exportar Original" ao invés de outros formatos
3. Verifique se o download completou

### "Token Nike não configurado"

**Causa:** Você não configurou suas credenciais Nike

**Solução:**
1. Vá em "Credenciais"
2. Configure seu token Nike primeiro
3. Volte ao Upload Manual

### "Atividade já existe no Nike"

**Causa:** A ferramenta detectou que essa atividade já foi sincronizada

**Solução:**
- Isso é normal! O Nike evita duplicatas automaticamente
- Você pode ignorar essa atividade

## 🎨 Interface

A página de upload tem:

1. **Área de Instruções:** Como funciona o processo
2. **Drop Zone:** Arraste arquivos ou clique para selecionar
3. **Lista de Arquivos:** Mostra os arquivos selecionados com tamanho
4. **Barra de Progresso:** Feedback visual durante upload
5. **Resultados:** Status de cada arquivo (sucesso/erro)

## 🚀 Performance

- Upload de 1 arquivo: ~2-5 segundos
- Upload de 10 arquivos: ~20-50 segundos
- Tamanho típico: 30-50 KB por atividade

## 📞 Suporte

Se tiver problemas:

1. Verifique se o arquivo foi baixado corretamente
2. Tente usar formato .FIT ao invés de .TCX/.GPX
3. Teste com uma atividade por vez primeiro
4. Verifique os logs de erro na página de resultado

---

**💡 DICA FINAL:** Combine as duas estratégias!

- Use **automática** para novas atividades do dia-a-dia
- Use **manual** para atividades antigas ou quando der erro 429

Melhor dos dois mundos! 🎯
