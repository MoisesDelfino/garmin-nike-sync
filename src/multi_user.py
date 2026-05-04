"""
Multi-User Manager
Gerencia sincronização para múltiplas contas Garmin/Nike
"""

import json
import os
from typing import List, Dict, Optional
from loguru import logger
from pathlib import Path

from .garmin_client import GarminClient
from .nike_client import NikeClient
from .synchronizer import Synchronizer


class UserConfig:
    """Configuração de um usuário"""
    
    def __init__(self, user_data: Dict):
        self.id = user_data.get('id')
        self.name = user_data.get('name', self.id)
        self.enabled = user_data.get('enabled', True)
        
        credentials = user_data.get('credentials', {})
        self.garmin_email_secret = credentials.get('garmin_email_secret', f'GARMIN_EMAIL_{self.id.upper()}')
        self.garmin_password_secret = credentials.get('garmin_password_secret', f'GARMIN_PASSWORD_{self.id.upper()}')
        self.nike_token_secret = credentials.get('nike_token_secret', f'NIKE_TOKEN_{self.id.upper()}')
        
        settings = user_data.get('settings', {})
        self.historical_sync_days = settings.get('historical_sync_days', 365)
        self.time_tolerance = settings.get('time_tolerance_seconds', 300)
        self.distance_tolerance = settings.get('distance_tolerance_meters', 50)
    
    def get_credentials_from_env(self) -> Dict[str, Optional[str]]:
        """
        Obtém credenciais das variáveis de ambiente
        
        Returns:
            Dicionário com credenciais ou None se não encontradas
        """
        return {
            'garmin_email': os.getenv(self.garmin_email_secret),
            'garmin_password': os.getenv(self.garmin_password_secret),
            'nike_token': os.getenv(self.nike_token_secret)
        }
    
    def has_valid_credentials(self) -> bool:
        """Verifica se as credenciais estão configuradas"""
        creds = self.get_credentials_from_env()
        return all([
            creds['garmin_email'],
            creds['garmin_password'],
            creds['nike_token']
        ])
    
    def get_history_file(self) -> str:
        """Retorna o caminho do arquivo de histórico deste usuário"""
        return f"sync_history_{self.id}.json"


class MultiUserManager:
    """Gerenciador de sincronização multi-usuário"""
    
    CONFIG_FILE = "config/users.json"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa o gerenciador
        
        Args:
            config_file: Caminho para arquivo de configuração (padrão: config/users.json)
        """
        self.config_file = config_file or self.CONFIG_FILE
        self.users: List[UserConfig] = []
        self.global_settings = {}
        self._load_config()
    
    def _load_config(self):
        """Carrega configuração de usuários"""
        if not os.path.exists(self.config_file):
            logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
            logger.info("Usando modo single-user (compatibilidade)")
            self._load_single_user_mode()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.global_settings = config.get('global_settings', {})
            
            users_data = config.get('users', [])
            if not users_data:
                logger.warning("Nenhum usuário configurado no arquivo")
                logger.info("Usando modo single-user (compatibilidade)")
                self._load_single_user_mode()
                return
            
            for user_data in users_data:
                user = UserConfig(user_data)
                if user.enabled:
                    self.users.append(user)
            
            logger.info(f"Carregados {len(self.users)} usuários ativos")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            logger.info("Usando modo single-user (compatibilidade)")
            self._load_single_user_mode()
    
    def _load_single_user_mode(self):
        """
        Modo de compatibilidade: single-user com variáveis de ambiente antigas
        """
        single_user = UserConfig({
            'id': 'default',
            'name': 'Default User',
            'enabled': True,
            'credentials': {
                'garmin_email_secret': 'GARMIN_EMAIL',
                'garmin_password_secret': 'GARMIN_PASSWORD',
                'nike_token_secret': 'NIKE_ACCESS_TOKEN'
            },
            'settings': {
                'historical_sync_days': int(os.getenv('HISTORICAL_SYNC_DAYS', 365)),
                'time_tolerance_seconds': int(os.getenv('DUPLICATE_TIME_TOLERANCE_SECONDS', 300)),
                'distance_tolerance_meters': int(os.getenv('DUPLICATE_DISTANCE_TOLERANCE_METERS', 50))
            }
        })
        
        if single_user.has_valid_credentials():
            self.users.append(single_user)
            logger.info("Modo single-user ativado")
        else:
            logger.warning("Nenhuma credencial encontrada")
    
    def get_enabled_users(self) -> List[UserConfig]:
        """Retorna lista de usuários habilitados com credenciais válidas"""
        valid_users = []
        for user in self.users:
            if user.enabled and user.has_valid_credentials():
                valid_users.append(user)
            elif user.enabled:
                logger.warning(f"Usuário {user.name} ({user.id}) habilitado mas sem credenciais válidas")
        
        return valid_users
    
    def sync_user(self, user: UserConfig, is_first_run: bool = False) -> Dict[str, int]:
        """
        Sincroniza atividades de um usuário específico
        
        Args:
            user: Configuração do usuário
            is_first_run: Se é primeira execução (sincroniza histórico)
            
        Returns:
            Estatísticas da sincronização
        """
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"Sincronizando: {user.name} ({user.id})")
        logger.info("=" * 70)
        
        try:
            # Obtém credenciais
            creds = user.get_credentials_from_env()
            
            # Inicializa clientes
            logger.info("Inicializando clientes...")
            garmin = GarminClient(creds['garmin_email'], creds['garmin_password'])
            nike = NikeClient(creds['nike_token'])
            
            # Testa conexões
            if not garmin.authenticate():
                logger.error(f"Falha na autenticação Garmin para {user.name}")
                return {'total': 0, 'synced': 0, 'skipped_duplicate': 0, 
                       'skipped_already_synced': 0, 'errors': 1}
            
            if not nike.test_connection():
                logger.error(f"Falha na conexão Nike para {user.name}")
                return {'total': 0, 'synced': 0, 'skipped_duplicate': 0,
                       'skipped_already_synced': 0, 'errors': 1}
            
            # Inicializa sincronizador com arquivo de histórico específico do usuário
            sync = Synchronizer(
                garmin,
                nike,
                time_tolerance=user.time_tolerance,
                distance_tolerance=user.distance_tolerance
            )
            
            # Usa arquivo de histórico específico do usuário
            sync.HISTORY_FILE = user.get_history_file()
            sync.history = sync._load_history()
            
            # Verifica se é primeira execução
            stats_before = sync.get_sync_stats()
            user_first_run = is_first_run or stats_before['total_synced'] == 0
            
            # Sincroniza
            if user_first_run:
                logger.info(f"Primeira execução para {user.name} - sincronizando histórico")
                stats = sync.sync_historical(days=user.historical_sync_days)
            else:
                logger.info(f"Sincronizando apenas novas atividades para {user.name}")
                stats = sync.sync_new_activities()
            
            # Exibe resultado
            logger.info("")
            logger.info(f"Resultado para {user.name}:")
            logger.info(f"  Total: {stats['total']}")
            logger.info(f"  ✅ Sincronizadas: {stats['synced']}")
            logger.info(f"  ⏭️  Duplicadas: {stats['skipped_duplicate']}")
            logger.info(f"  ⏭️  Já sincronizadas: {stats['skipped_already_synced']}")
            logger.info(f"  ❌ Erros: {stats['errors']}")
            
            return stats
            
        except Exception as e:
            logger.exception(f"Erro ao sincronizar usuário {user.name}: {e}")
            return {'total': 0, 'synced': 0, 'skipped_duplicate': 0,
                   'skipped_already_synced': 0, 'errors': 1}
    
    def sync_all_users(self, is_first_run: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Sincroniza todos os usuários habilitados
        
        Args:
            is_first_run: Se é primeira execução (sincroniza histórico)
            
        Returns:
            Dicionário com estatísticas por usuário
        """
        users = self.get_enabled_users()
        
        if not users:
            logger.error("Nenhum usuário configurado ou com credenciais válidas")
            return {}
        
        logger.info(f"Iniciando sincronização para {len(users)} usuário(s)")
        
        results = {}
        for user in users:
            results[user.id] = self.sync_user(user, is_first_run)
        
        # Resumo geral
        logger.info("")
        logger.info("=" * 70)
        logger.info("RESUMO GERAL")
        logger.info("=" * 70)
        
        total_synced = sum(r['synced'] for r in results.values())
        total_errors = sum(r['errors'] for r in results.values())
        
        for user_id, stats in results.items():
            user = next(u for u in users if u.id == user_id)
            logger.info(f"{user.name}: {stats['synced']} sincronizadas, {stats['errors']} erros")
        
        logger.info("")
        logger.info(f"Total geral: {total_synced} atividades sincronizadas")
        if total_errors > 0:
            logger.warning(f"Total de erros: {total_errors}")
        
        return results
