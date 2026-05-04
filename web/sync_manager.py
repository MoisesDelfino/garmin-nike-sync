"""
Sync Manager para aplicação Web
Gerencia sincronização de atividades para usuários web
"""

from datetime import datetime, timedelta
from loguru import logger

from web.models.database import db, User, SyncHistory, SyncLog
from src.garmin_client import GarminClient
from src.nike_client import NikeClient
from src.synchronizer import Synchronizer


class SyncManager:
    """Gerenciador de sincronização para aplicação web"""
    
    def __init__(self, app):
        """
        Inicializa gerenciador
        
        Args:
            app: Instância Flask app
        """
        self.app = app
    
    def sync_user(self, user_id):
        """
        Sincroniza atividades de um usuário específico
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com estatísticas
        """
        with self.app.app_context():
            user = User.query.get(user_id)
            
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            if not user.sync_enabled:
                logger.info(f"Sync disabled for user {user.email}")
                return {'status': 'disabled'}
            
            if not user.has_credentials():
                logger.warning(f"User {user.email} has no credentials")
                return {'status': 'no_credentials'}
            
            # Cria log de execução
            sync_log = SyncLog(
                user_id=user.id,
                status='running'
            )
            db.session.add(sync_log)
            db.session.commit()
            
            try:
                logger.info(f"Starting sync for user: {user.email}")
                
                # Obtém credenciais
                logger.debug(f"🔐 Recuperando credenciais do banco de dados...")
                garmin_email, garmin_password = user.get_garmin_credentials()
                nike_token = user.get_nike_token()
                
                logger.debug(f"📧 Garmin email recuperado: {garmin_email[:3] if garmin_email else 'NONE'}***")
                logger.debug(f"🔑 Garmin password existe: {bool(garmin_password)}")
                logger.debug(f"🏃 Nike token existe: {bool(nike_token)}")
                logger.debug(f"📊 Nike status: {user.nike_status}")
                
                if garmin_email:
                    logger.info(f"✓ Email Garmin: {garmin_email[:3]}***{garmin_email[-10:] if len(garmin_email) > 13 else ''}")
                if garmin_password:
                    logger.info(f"✓ Senha Garmin: {len(garmin_password)} caracteres")
                else:
                    logger.error(f"❌ Senha Garmin VAZIA ou NULA")
                
                # Verifica se credenciais existem
                if not garmin_email or not garmin_password:
                    raise Exception("Credenciais Garmin não configuradas")
                
                if not nike_token:
                    raise Exception("Token Nike não configurado. Aguarde configuração do administrador.")
                
                if user.nike_status != 'active':
                    raise Exception(f"Nike status: {user.nike_status}. Aguarde ativação pelo administrador.")
                
                # Inicializa clientes
                logger.info("Inicializando cliente Garmin...")
                garmin = GarminClient(garmin_email, garmin_password)
                
                logger.info("Inicializando cliente Nike...")
                nike = NikeClient(nike_token)
                
                # Testa conexões
                logger.info("Testando autenticação Garmin...")
                try:
                    garmin.authenticate()
                except Exception as garmin_error:
                    error_msg = str(garmin_error)
                    
                    # Erro de rate limit (429)
                    if "RATE_LIMIT" in error_msg:
                        raise Exception("⏳ O Garmin está temporariamente bloqueando requisições devido a muitas tentativas. Por favor, aguarde 15-30 minutos e tente novamente.")
                    
                    # Credenciais inválidas
                    elif "INVALID_CREDENTIALS" in error_msg:
                        raise Exception("🔑 Email ou senha do Garmin incorretos. Verifique suas credenciais na página de Configurações.")
                    
                    # Outros erros
                    else:
                        raise Exception(f"Erro ao conectar com Garmin: {error_msg}")
                
                logger.info("Testando conexão Nike...")
                if not nike.test_connection():
                    user.nike_status = 'error'
                    user.nike_status_message = "Token Nike inválido ou expirado. Entre em contato com o administrador para renovar o token."
                    db.session.commit()
                    raise Exception("Token Nike inválido ou expirado. Por favor, entre em contato com o administrador para que ele renove seu token Nike.")
                
                logger.info("Autenticações OK, iniciando sincronização...")
                
                # Cria sincronizador
                sync = Synchronizer(
                    garmin,
                    nike,
                    time_tolerance=user.time_tolerance,
                    distance_tolerance=user.distance_tolerance
                )
                
                # Determina se é primeira sincronização
                is_first_sync = user.last_sync is None
                
                if is_first_sync:
                    logger.info(f"First sync for {user.email} - syncing history")
                    stats = sync.sync_historical(days=user.historical_days)
                else:
                    logger.info(f"Syncing new activities for {user.email}")
                    stats = sync.sync_new_activities()
                
                # Salva atividades sincronizadas no banco
                self._save_sync_history(user, stats, sync)
                
                # Atualiza usuário
                user.last_sync = datetime.utcnow()
                user.last_sync_status = 'success'
                user.last_sync_message = f"{stats['synced']} atividades sincronizadas"
                user.total_synced += stats['synced']
                
                # Atualiza log
                sync_log.finished_at = datetime.utcnow()
                sync_log.status = 'success'
                sync_log.total_found = stats['total']
                sync_log.total_synced = stats['synced']
                sync_log.total_duplicates = stats['skipped_duplicate']
                sync_log.total_errors = stats['errors']
                sync_log.message = f"Sincronizadas {stats['synced']} de {stats['total']} atividades"
                
                db.session.commit()
                
                logger.success(f"Sync completed for {user.email}: {stats}")
                
                return stats
                
            except Exception as e:
                logger.error(f"Sync error for user {user.email}: {e}")
                
                # Atualiza usuário
                user.last_sync_status = 'error'
                user.last_sync_message = str(e)
                
                # Atualiza log
                sync_log.finished_at = datetime.utcnow()
                sync_log.status = 'error'
                sync_log.message = str(e)
                
                db.session.commit()
                
                raise
    
    def _save_sync_history(self, user, stats, synchronizer):
        """
        Salva histórico de atividades sincronizadas no banco
        
        Args:
            user: Usuário
            stats: Estatísticas da sincronização
            synchronizer: Instância do Synchronizer
        """
        # Carrega histórico do sincronizador
        history = synchronizer.history.get('synced_activities', {})
        
        # Filtra apenas atividades sincronizadas nesta execução
        # (as que foram adicionadas recentemente)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for garmin_id, sync_data in history.items():
            # Verifica se já existe no banco
            existing = SyncHistory.query.filter_by(
                user_id=user.id,
                garmin_activity_id=garmin_id
            ).first()
            
            if not existing:
                # Cria novo registro
                sync_history = SyncHistory(
                    user_id=user.id,
                    garmin_activity_id=garmin_id,
                    nike_activity_id=sync_data.get('nike_id'),
                    activity_name=sync_data.get('name', 'Atividade'),
                    activity_type='running',  # TODO: pegar do sync_data
                    distance=sync_data.get('distance', 0),
                    duration=0,  # TODO: pegar do sync_data
                    activity_date=datetime.fromisoformat(sync_data['date'].replace('Z', '+00:00')) 
                                   if sync_data.get('date') else None,
                    sync_status='synced'
                )
                
                db.session.add(sync_history)
        
        db.session.commit()
    
    def sync_all_users(self):
        """
        Sincroniza todos os usuários ativos
        
        Returns:
            Dicionário com resultados por usuário
        """
        with self.app.app_context():
            users = User.query.filter_by(
                is_active=True,
                sync_enabled=True
            ).all()
            
            logger.info(f"Starting sync for {len(users)} users")
            
            results = {}
            for user in users:
                if user.has_credentials():
                    try:
                        results[user.id] = self.sync_user(user.id)
                    except Exception as e:
                        logger.error(f"Error syncing user {user.id}: {e}")
                        results[user.id] = {'status': 'error', 'message': str(e)}
                else:
                    logger.warning(f"User {user.email} has no credentials")
                    results[user.id] = {'status': 'no_credentials'}
            
            logger.info(f"Sync completed for {len(results)} users")
            
            return results
