"""
Sincronizador Garmin → Nike
Gerencia a sincronização de atividades entre Garmin Connect e Nike Run Club
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from .garmin_client import GarminClient
from .nike_client import NikeClient


class Synchronizer:
    """Gerencia sincronização entre Garmin e Nike"""
    
    HISTORY_FILE = "sync_history.json"
    
    def __init__(self, garmin_client: GarminClient, nike_client: NikeClient,
                 time_tolerance: int = 300, distance_tolerance: int = 50):
        """
        Inicializa o sincronizador
        
        Args:
            garmin_client: Cliente Garmin autenticado
            nike_client: Cliente Nike autenticado
            time_tolerance: Tolerância de tempo para deduplicação (segundos)
            distance_tolerance: Tolerância de distância para deduplicação (metros)
        """
        self.garmin = garmin_client
        self.nike = nike_client
        self.time_tolerance = time_tolerance
        self.distance_tolerance = distance_tolerance
        self.history = self._load_history()
        
    def _load_history(self) -> Dict:
        """
        Carrega histórico de sincronizações
        
        Returns:
            Dicionário com histórico
        """
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar histórico: {e}")
                return {'synced_activities': {}, 'last_sync': None}
        
        return {'synced_activities': {}, 'last_sync': None}
    
    def _save_history(self):
        """Salva histórico de sincronizações"""
        try:
            with open(self.HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug("Histórico salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
    
    def is_already_synced(self, garmin_activity_id: str) -> bool:
        """
        Verifica se atividade já foi sincronizada
        
        Args:
            garmin_activity_id: ID da atividade no Garmin
            
        Returns:
            True se já sincronizada
        """
        return garmin_activity_id in self.history['synced_activities']
    
    def mark_as_synced(self, garmin_activity_id: str, nike_activity_id: str,
                      activity_data: Dict):
        """
        Marca atividade como sincronizada
        
        Args:
            garmin_activity_id: ID da atividade no Garmin
            nike_activity_id: ID da atividade no Nike
            activity_data: Dados da atividade
        """
        self.history['synced_activities'][garmin_activity_id] = {
            'nike_id': nike_activity_id,
            'synced_at': datetime.now().isoformat(),
            'name': activity_data.get('name', 'Sem nome'),
            'distance': activity_data.get('distance', 0),
            'date': activity_data.get('start_time')
        }
        self._save_history()
    
    def sync_historical(self, days: int = None, start_date: datetime = None, end_date: datetime = None) -> Dict[str, int]:
        """
        Sincroniza atividades históricas
        
        Args:
            days: Número de dias para buscar no histórico (deprecated, use start_date/end_date)
            start_date: Data inicial para buscar atividades (opcional)
            end_date: Data final para buscar atividades (opcional)
            
        Returns:
            Estatísticas da sincronização
        """
        # Se start_date/end_date não fornecidos, usa days (compatibilidade)
        if start_date is None:
            if days is None:
                days = 365
            start_date = datetime.now() - timedelta(days=days)
            logger.info(f"Iniciando sincronização histórica (últimos {days} dias)")
        else:
            if end_date is None:
                end_date = datetime.now()
            logger.info(f"Iniciando sincronização histórica de {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
        
        stats = {
            'total': 0,
            'synced': 0,
            'skipped_duplicate': 0,
            'skipped_already_synced': 0,
            'errors': 0
        }
        
        # Busca atividades do Garmin
        garmin_activities = self.garmin.get_activities(start_date=start_date, limit=1000)
        
        if not garmin_activities:
            logger.warning("Nenhuma atividade encontrada no Garmin")
            return stats
        
        stats['total'] = len(garmin_activities)
        logger.info(f"Encontradas {stats['total']} atividades no Garmin")
        
        # Sincroniza cada atividade
        for activity in garmin_activities:
            result = self.sync_activity(activity)
            
            if result == 'synced':
                stats['synced'] += 1
            elif result == 'duplicate':
                stats['skipped_duplicate'] += 1
            elif result == 'already_synced':
                stats['skipped_already_synced'] += 1
            elif result == 'error':
                stats['errors'] += 1
        
        # Atualiza timestamp da última sincronização
        self.history['last_sync'] = datetime.now().isoformat()
        self._save_history()
        
        logger.success(
            f"Sincronização histórica concluída: "
            f"{stats['synced']} sincronizadas, "
            f"{stats['skipped_duplicate']} duplicadas, "
            f"{stats['skipped_already_synced']} já sincronizadas, "
            f"{stats['errors']} erros"
        )
        
        return stats
    
    def sync_new_activities(self) -> Dict[str, int]:
        """
        Sincroniza apenas novas atividades (desde última sincronização)
        
        Returns:
            Estatísticas da sincronização
        """
        logger.info("Sincronizando novas atividades...")
        
        # Define data de início baseada na última sincronização
        if self.history.get('last_sync'):
            start_date = datetime.fromisoformat(self.history['last_sync'])
            # Subtrai 1 hora para garantir que não perca nenhuma atividade
            start_date = start_date - timedelta(hours=1)
        else:
            # Se nunca sincronizou, busca últimos 7 dias
            start_date = datetime.now() - timedelta(days=7)
        
        logger.info(f"Buscando atividades desde {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Busca e sincroniza
        garmin_activities = self.garmin.get_activities(start_date=start_date, limit=50)
        
        stats = {
            'total': len(garmin_activities),
            'synced': 0,
            'skipped_duplicate': 0,
            'skipped_already_synced': 0,
            'errors': 0
        }
        
        for activity in garmin_activities:
            result = self.sync_activity(activity)
            
            if result == 'synced':
                stats['synced'] += 1
            elif result == 'duplicate':
                stats['skipped_duplicate'] += 1
            elif result == 'already_synced':
                stats['skipped_already_synced'] += 1
            elif result == 'error':
                stats['errors'] += 1
        
        # Atualiza última sincronização
        self.history['last_sync'] = datetime.now().isoformat()
        self._save_history()
        
        if stats['synced'] > 0:
            logger.success(f"Sincronizadas {stats['synced']} novas atividades")
        else:
            logger.info("Nenhuma atividade nova para sincronizar")
        
        return stats
    
    def sync_activity(self, garmin_activity: Dict) -> str:
        """
        Sincroniza uma atividade específica
        
        Args:
            garmin_activity: Atividade do Garmin
            
        Returns:
            Status: 'synced', 'duplicate', 'already_synced', 'error'
        """
        garmin_id = garmin_activity['id']
        activity_name = garmin_activity.get('name', 'Sem nome')
        
        # Verifica se já foi sincronizada anteriormente
        if self.is_already_synced(garmin_id):
            logger.debug(f"Atividade já sincronizada: {activity_name} ({garmin_id})")
            return 'already_synced'
        
        # Verifica se é duplicata no Nike
        nike_duplicate = self.nike.find_duplicate(
            garmin_activity,
            time_tolerance_seconds=self.time_tolerance,
            distance_tolerance_meters=self.distance_tolerance
        )
        
        if nike_duplicate:
            logger.info(
                f"Atividade duplicada no Nike: {activity_name} "
                f"(Garmin: {garmin_id}, Nike: {nike_duplicate})"
            )
            # Marca como sincronizada mesmo sendo duplicata
            self.mark_as_synced(garmin_id, nike_duplicate, garmin_activity)
            return 'duplicate'
        
        # Sincroniza para o Nike
        try:
            nike_id = self.nike.create_activity(garmin_activity)
            
            if nike_id:
                logger.success(
                    f"Atividade sincronizada: {activity_name} "
                    f"(Garmin: {garmin_id} → Nike: {nike_id})"
                )
                self.mark_as_synced(garmin_id, nike_id, garmin_activity)
                return 'synced'
            else:
                logger.error(f"Falha ao sincronizar atividade: {activity_name}")
                return 'error'
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar {activity_name}: {e}")
            return 'error'
    
    def get_sync_stats(self) -> Dict:
        """
        Retorna estatísticas gerais da sincronização
        
        Returns:
            Dicionário com estatísticas
        """
        total_synced = len(self.history['synced_activities'])
        last_sync = self.history.get('last_sync')
        
        if last_sync:
            last_sync_dt = datetime.fromisoformat(last_sync)
            time_since_sync = datetime.now() - last_sync_dt
            hours_since = int(time_since_sync.total_seconds() / 3600)
        else:
            hours_since = None
        
        return {
            'total_synced': total_synced,
            'last_sync': last_sync,
            'hours_since_last_sync': hours_since
        }
