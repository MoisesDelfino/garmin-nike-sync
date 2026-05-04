"""
Garmin Connect API Client
Usa a biblioteca garth para autenticação e busca de atividades
"""

import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import garth
from requests.exceptions import HTTPError

# Rate limiter global para controlar requisições ao Garmin
try:
    from web.rate_limiter import rate_limiter
except ImportError:
    # Fallback se não estiver em ambiente web
    rate_limiter = None


class GarminClient:
    """Cliente para interagir com Garmin Connect API"""
    
    def __init__(self, email: str, password: str):
        """
        Inicializa o cliente Garmin
        
        Args:
            email: Email da conta Garmin
            password: Senha da conta Garmin
        """
        self.email = email
        self.password = password
        self.client = None
        self._authenticated = False
        
    def authenticate(self, max_retries: int = 3) -> bool:
        """
        Autentica no Garmin Connect com retry inteligente
        
        Args:
            max_retries: Número máximo de tentativas
            
        Returns:
            True se autenticado com sucesso
            
        Raises:
            Exception: Com mensagem específica do erro
        """
        logger.info(f"Autenticando no Garmin Connect com email: {self.email}")
        
        # Rate limiting global
        if rate_limiter:
            if not rate_limiter.wait_if_needed():
                raise Exception("RATE_LIMIT: Garmin em cooldown após muitas requisições. Aguarde alguns minutos.")
        
        # Tenta carregar sessão salva
        session_dir = ".garth"
        if os.path.exists(session_dir):
            try:
                garth.resume(session_dir)
                # Testa se a sessão ainda é válida
                garth.connectapi("/userprofile-service/userprofile")
                logger.success("✓ Sessão Garmin restaurada do cache e válida")
                self._authenticated = True
                return True
            except Exception as e:
                # Verifica se é erro 429
                error_str = str(e)
                if "429" in error_str or "Too Many Requests" in error_str:
                    logger.warning(f"⚠️ Garmin rate limit atingido ao validar sessão. Aguardando...")
                    raise Exception("RATE_LIMIT: O Garmin está temporariamente bloqueando requisições. Aguarde 15-30 minutos e tente novamente.")
                logger.warning(f"Sessão expirada ou inválida, tentando novo login: {e}")
        
        # Nova autenticação com retry e exponential backoff
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    # Exponential backoff: 5s, 15s, 45s
                    wait_time = 5 * (3 ** (attempt - 2))
                    logger.info(f"⏳ Tentativa {attempt}/{max_retries} - Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                
                logger.info(f"Fazendo login no Garmin Connect... (tentativa {attempt}/{max_retries})")
                garth.login(self.email, self.password)
                garth.save(session_dir)
                
                logger.success("✓ Autenticado com sucesso no Garmin Connect")
                self._authenticated = True
                return True
                
            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                
                # Detecta erro 429 (Rate Limit)
                if "429" in error_str or "Too Many Requests" in error_str:
                    logger.error(f"❌ Garmin Rate Limit (429) - Tentativa {attempt}/{max_retries}")
                    # Registra erro 429 no rate limiter global
                    if rate_limiter:
                        rate_limiter.report_429_error()
                    if attempt == max_retries:
                        raise Exception("RATE_LIMIT: O Garmin está temporariamente bloqueando requisições devido a muitas tentativas. Aguarde 15-30 minutos antes de tentar novamente.")
                    continue
                
                # Detecta credenciais inválidas
                if "401" in error_str or "403" in error_str or "Unauthorized" in error_str:
                    logger.error(f"❌ Credenciais inválidas - Email: {self.email}")
                    raise Exception("INVALID_CREDENTIALS: Email ou senha incorretos. Verifique suas credenciais na página de Configurações.")
                
                # Outros erros
                logger.error(f"❌ Erro ao autenticar (tentativa {attempt}/{max_retries}): {error_type}: {e}")
                if attempt == max_retries:
                    logger.error(f"Email tentado: {self.email}")
                    raise Exception(f"Erro ao conectar com Garmin Connect: {error_str}")
        
        self._authenticated = False
        raise Exception("Falha na autenticação após múltiplas tentativas.")
    
    def get_activities(self, start_date: Optional[datetime] = None, 
                       limit: int = 100) -> List[Dict]:
        """
        Busca atividades do Garmin Connect
        
        Args:
            start_date: Data inicial para buscar atividades (padrão: últimos 30 dias)
            limit: Número máximo de atividades a buscar
            
        Returns:
            Lista de atividades
        """
        if not self._authenticated:
            if not self.authenticate():
                return []
        
        # Rate limiting global antes de buscar atividades
        if rate_limiter:
            if not rate_limiter.wait_if_needed():
                logger.warning("Garmin em cooldown - pulando busca de atividades")
                return []
        
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            
            logger.info(f"Buscando atividades desde {start_date.strftime('%Y-%m-%d')}")
            
            # Busca atividades usando garth
            activities = garth.connectapi(
                f"/activitylist-service/activities/search/activities",
                params={
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "limit": limit
                }
            )
            
            if not activities:
                logger.info("Nenhuma atividade encontrada")
                return []
            
            # Filtra apenas atividades de corrida/caminhada
            running_activities = []
            for activity in activities:
                activity_type = activity.get('activityType', {}).get('typeKey', '')
                
                if activity_type in ['running', 'street_running', 'track_running', 
                                     'trail_running', 'treadmill_running', 'walking']:
                    running_activities.append(self._parse_activity(activity))
            
            logger.info(f"Encontradas {len(running_activities)} atividades de corrida/caminhada")
            return running_activities
            
        except Exception as e:
            logger.error(f"Erro ao buscar atividades do Garmin: {e}")
            return []
    
    def get_activity_details(self, activity_id: str) -> Optional[Dict]:
        """
        Busca detalhes completos de uma atividade específica
        
        Args:
            activity_id: ID da atividade no Garmin
            
        Returns:
            Detalhes da atividade ou None
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            logger.debug(f"Buscando detalhes da atividade {activity_id}")
            
            # Busca detalhes completos
            details = garth.connectapi(f"/activity-service/activity/{activity_id}")
            
            # Busca dados de GPS (se disponível)
            try:
                gps_data = garth.connectapi(
                    f"/activity-service/activity/{activity_id}/details"
                )
                details['gps_data'] = gps_data
            except:
                details['gps_data'] = None
            
            return details
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes da atividade {activity_id}: {e}")
            return None
    
    def _parse_activity(self, activity: Dict) -> Dict:
        """
        Parse os dados da atividade para formato padronizado
        
        Args:
            activity: Dados brutos da atividade
            
        Returns:
            Atividade formatada
        """
        return {
            'id': str(activity.get('activityId')),
            'name': activity.get('activityName', 'Corrida'),
            'type': activity.get('activityType', {}).get('typeKey', 'running'),
            'start_time': activity.get('startTimeLocal'),
            'start_time_gmt': activity.get('startTimeGMT'),
            'distance': activity.get('distance', 0),  # em metros
            'duration': activity.get('duration', 0),  # em segundos
            'moving_duration': activity.get('movingDuration', 0),
            'elevation_gain': activity.get('elevationGain', 0),
            'elevation_loss': activity.get('elevationLoss', 0),
            'average_speed': activity.get('averageSpeed', 0),  # m/s
            'max_speed': activity.get('maxSpeed', 0),
            'calories': activity.get('calories', 0),
            'average_hr': activity.get('averageHR'),
            'max_hr': activity.get('maxHR'),
            'average_running_cadence': activity.get('averageRunningCadenceInStepsPerMinute'),
            'location_name': activity.get('locationName'),
            'raw_data': activity
        }
    
    def get_activity_splits(self, activity_id: str) -> List[Dict]:
        """
        Busca splits (divisões por km) da atividade
        
        Args:
            activity_id: ID da atividade
            
        Returns:
            Lista de splits
        """
        try:
            splits = garth.connectapi(
                f"/activity-service/activity/{activity_id}/splits"
            )
            return splits.get('lapDTOs', [])
        except Exception as e:
            logger.warning(f"Não foi possível buscar splits: {e}")
            return []
