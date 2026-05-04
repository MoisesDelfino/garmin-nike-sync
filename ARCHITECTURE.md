# 📐 Arquitetura do Projeto

Documentação técnica da estrutura e funcionamento do Garmin → Nike Sync.

## 🗂️ Estrutura de Arquivos

```
garmin-nike-sync/
├── .github/
│   └── workflows/
│       └── sync.yml              # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── garmin_client.py          # Cliente Garmin Connect API
│   ├── nike_client.py            # Cliente Nike Run Club API
│   └── synchronizer.py           # Lógica de sincronização
├── logs/                         # Logs gerados (ignorado pelo git)
├── .env                          # Credenciais locais (ignorado)
├── .env.example                  # Template de credenciais
├── .gitignore
├── LICENSE
├── main.py                       # Script principal
├── requirements.txt              # Dependências Python
├── sync_history.json             # Histórico de sincronizações
├── test_credentials.py           # Validação de credenciais
├── README.md                     # Documentação principal
├── QUICKSTART.md                 # Guia rápido
└── NIKE-TOKEN-GUIDE.md          # Como obter token Nike
```

## 🔧 Componentes

### 1. GarminClient (`src/garmin_client.py`)

**Responsabilidades:**
- Autenticação no Garmin Connect
- Busca de atividades
- Cache de sessão (`.garth/`)
- Parse de dados para formato padronizado

**Métodos principais:**
```python
authenticate() → bool
get_activities(start_date, limit) → List[Dict]
get_activity_details(activity_id) → Dict
get_activity_splits(activity_id) → List[Dict]
```

**Dependências:**
- `garth` - Biblioteca não-oficial Garmin API

**Dados retornados:**
```python
{
    'id': '12345678',
    'name': 'Corrida Matinal',
    'type': 'running',
    'start_time': '2026-05-04T06:30:00Z',
    'distance': 5000,  # metros
    'duration': 1800,  # segundos
    'calories': 350,
    'average_hr': 145,
    'elevation_gain': 50,
    ...
}
```

### 2. NikeClient (`src/nike_client.py`)

**Responsabilidades:**
- Autenticação via Bearer token
- Busca de atividades Nike
- Criação de novas atividades
- Detecção de duplicatas

**Métodos principais:**
```python
test_connection() → bool
get_activities(start_date, limit) → List[Dict]
create_activity(activity_data) → str
find_duplicate(garmin_activity, tolerances) → Optional[str]
```

**API Endpoints (reverse engineered):**
```
GET  https://api.nike.com/sport/v3/me/activities
POST https://api.nike.com/sport/v3/me/activity
```

**Formato de payload:**
```python
{
    'type': 'run',
    'start_epoch_ms': 1715000000000,
    'end_epoch_ms': 1715001800000,
    'summaries': [
        {'metric': 'distance', 'value': 5000, 'unit': 'METER'},
        {'metric': 'duration', 'value': 1800, 'unit': 'SECOND'},
        {'metric': 'calories', 'value': 350, 'unit': 'CALORIE'}
    ],
    'tags': {'com.nike.name': 'Corrida Matinal'}
}
```

### 3. Synchronizer (`src/synchronizer.py`)

**Responsabilidades:**
- Orquestração da sincronização
- Gerenciamento de histórico
- Detecção de duplicatas
- Estatísticas de sincronização

**Métodos principais:**
```python
sync_historical(days) → Dict[stats]
sync_new_activities() → Dict[stats]
sync_activity(garmin_activity) → str
is_already_synced(id) → bool
mark_as_synced(garmin_id, nike_id)
```

**Lógica de deduplicação:**
```python
# Critérios:
1. Tempo: ±5 minutos (300 segundos)
2. Distância: ±50 metros

# Algoritmo:
for nike_activity in nike_activities:
    time_diff = abs(garmin_time - nike_time)
    distance_diff = abs(garmin_distance - nike_distance)
    
    if time_diff <= 300 and distance_diff <= 50:
        return True  # É duplicata
```

**Formato do histórico (`sync_history.json`):**
```json
{
  "synced_activities": {
    "garmin_id_123": {
      "nike_id": "nike_id_456",
      "synced_at": "2026-05-04T10:30:00",
      "name": "Corrida Matinal",
      "distance": 5000,
      "date": "2026-05-04T06:30:00Z"
    }
  },
  "last_sync": "2026-05-04T10:30:00"
}
```

### 4. Main Script (`main.py`)

**Fluxo de execução:**

```
┌─────────────────────┐
│  Setup Logging      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Load Config        │
│  (.env ou secrets)  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Initialize Clients │
│  - Garmin           │
│  - Nike             │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Test Connections   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Create Sync        │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ First run?  │
    └──┬───────┬──┘
  Yes  │       │  No
       │       │
   ┌───▼──┐ ┌──▼──────┐
   │Hist. │ │ New     │
   │Sync  │ │ Only    │
   └───┬──┘ └──┬──────┘
       │       │
    ┌──▼───────▼──┐
    │  Show Stats │
    └─────────────┘
```

### 5. GitHub Actions (`sync.yml`)

**Triggers:**
- Schedule: `*/15 * * * *` (a cada 15 minutos)
- Manual: `workflow_dispatch`
- Push: Para testes

**Steps:**
1. **Checkout** - Clona repositório
2. **Setup Python** - Instala Python 3.10 + cache pip
3. **Install deps** - `pip install -r requirements.txt`
4. **Run sync** - Executa `main.py` com secrets
5. **Commit history** - Commita `sync_history.json` e `.garth/`
6. **Upload logs** - Salva logs como artifact (7 dias)

**Variáveis de ambiente:**
```yaml
GARMIN_EMAIL              # Secret
GARMIN_PASSWORD           # Secret
NIKE_ACCESS_TOKEN         # Secret
SYNC_INTERVAL_MINUTES     # 15 (config)
HISTORICAL_SYNC_DAYS      # 365 (config)
...
```

## 🔄 Fluxo de Sincronização

### Primeira Execução (Histórico)

```
1. Busca atividades Garmin (últimos 365 dias)
2. Busca atividades Nike (mesma janela)
3. Para cada atividade Garmin:
   a. Verifica se já foi sincronizada (histórico local)
   b. Se não, busca duplicata no Nike (tempo + distância)
   c. Se não duplicada, cria no Nike
   d. Registra no histórico
4. Salva histórico atualizado
```

### Execuções Subsequentes (Incremental)

```
1. Lê última sincronização do histórico
2. Busca atividades Garmin desde (última_sync - 1h)
3. Para cada nova atividade:
   a. Verifica histórico local
   b. Verifica duplicata Nike
   c. Sincroniza se necessário
4. Atualiza timestamp última sincronização
```

## 📊 Estatísticas e Monitoramento

### Logs

**Níveis:**
- `DEBUG` - Detalhes técnicos (apenas arquivo)
- `INFO` - Progresso normal
- `SUCCESS` - Operações bem-sucedidas
- `WARNING` - Problemas não-críticos
- `ERROR` - Erros que requerem atenção

**Localizações:**
- Console: Nível INFO+
- Arquivo: `logs/sync_YYYY-MM-DD.log` (DEBUG+)
- GitHub Actions: Artifacts (7 dias)

### Métricas de Sincronização

```python
{
    'total': 10,                    # Total de atividades encontradas
    'synced': 3,                    # Novas sincronizadas
    'skipped_duplicate': 5,         # Já existiam no Nike
    'skipped_already_synced': 2,    # Já sincronizadas antes
    'errors': 0                     # Erros
}
```

## 🔐 Segurança

### Credenciais

**Local (desenvolvimento):**
- `.env` - Nunca commitado (no `.gitignore`)
- Carregado via `python-dotenv`

**GitHub Actions:**
- GitHub Secrets (criptografados)
- Injetados como variáveis de ambiente
- **Nunca** aparecem nos logs

### Sessões Garmin

- Cache em `.garth/` (commitado)
- Evita login a cada execução
- Auto-renovação quando expira

### Token Nike

- Armazenado apenas em Secret
- Expira após ~30-90 dias
- Precisa renovação manual

## 🧪 Testes

### Local

```bash
# Testar credenciais
python test_credentials.py

# Executar sincronização
python main.py
```

### GitHub Actions

```bash
# Execução manual
Actions > Run workflow

# Verificar logs
Actions > Última execução > Expandir steps
```

## 🐛 Debug

### Garmin não conecta

```python
# Verificar logs
tail -f logs/sync_*.log

# Problemas comuns:
- Email/senha incorretos
- 2FA ativado
- IP bloqueado (muitas tentativas)
```

### Nike retorna 401

```python
# Token expirado ou inválido
# Solução: Renovar token

# Verificar token:
curl -H "Authorization: Bearer $TOKEN" \
  https://api.nike.com/sport/v3/me/activities?limit=1
```

### Atividades duplicadas

```python
# Ajustar tolerâncias em sync.yml:
DUPLICATE_TIME_TOLERANCE_SECONDS: 600    # ±10 min
DUPLICATE_DISTANCE_TOLERANCE_METERS: 100 # ±100m
```

## 🚀 Performance

### Otimizações Implementadas

1. **Cache de sessão Garmin** - Evita re-autenticação
2. **Sincronização incremental** - Apenas novas atividades
3. **Histórico local** - Evita buscar Nike desnecessariamente
4. **Pip cache** - GitHub Actions reutiliza dependências

### Limites

- **GitHub Actions**: 2000 min/mês (gratuito)
- **Execuções**: ~15seg cada = ~8000 execuções/mês
- **APIs**: Sem limite conhecido (usar com moderação)

## 📈 Melhorias Futuras

### Possíveis Features

- [ ] Sincronização bidirecional (Nike → Garmin)
- [ ] Suporte a outras plataformas (Strava, Runkeeper)
- [ ] Dashboard web de estatísticas
- [ ] Notificações (Telegram, Email) em erros
- [ ] Renovação automática de token Nike
- [ ] Upload de arquivos GPX completos
- [ ] Sincronização de fotos de atividades

### Otimizações

- [ ] Webhook Garmin (se disponível)
- [ ] Cache de atividades Nike
- [ ] Rate limiting inteligente
- [ ] Retry exponencial em falhas

---

**Dúvidas?** Abra uma issue no GitHub!
