"""
Garmin Connect API Client
Usa a biblioteca garth para autenticação e busca de atividades
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import garth


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
        
    def authenticate(self) -> bool:
        """
        Autentica no Garmin Connect
        
        Returns:
            True se autenticado com sucesso
        """
        try:
            logger.info("Autenticando no Garmin Connect...")
            
            # Tenta carregar sessão salva
            session_dir = ".garth"
            if os.path.exists(session_dir):
                try:
                    garth.resume(session_dir)
                    logger.info("Sessão Garmin restaurada do cache")
                    self._authenticated = True
                    return True
                except Exception as e:
                    logger.warning(f"Não foi possível restaurar sessão: {e}")
            
            # Nova autenticação
            garth.login(self.email, self.password)
            garth.save(session_dir)
            
            logger.success("Autenticado com sucesso no Garmin Connect")
            self._authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao autenticar no Garmin: {e}")
            self._authenticated = False
            return False
    
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
