"""
Sync Manager para aplicação Web
Gerencia sincronização de atividades para usuários web
"""

import time
from datetime import datetime, timedelta
from loguru import logger

from web.models.database import db, User, SyncHistory, SyncLog
from src.garmin_client import GarminClient
from src.nike_client import NikeClient
from src.synchronizer import Synchronizer
from web.rate_limiter import rate_limiter


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
                    
                    # Usa datas se configuradas, senão usa historical_days
                    if user.initial_sync_start_date and user.initial_sync_end_date:
                        start = datetime.combine(user.initial_sync_start_date, datetime.min.time())
                        end = datetime.combine(user.initial_sync_end_date, datetime.max.time())
                        stats = sync.sync_historical(start_date=start, end_date=end)
                    else:
                        # Fallback para o método antigo (dias)
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
            
            finally:
                # Garante que o log seja finalizado mesmo em casos de exceção não tratada
                try:
                    if sync_log.finished_at is None:
                        sync_log.finished_at = datetime.utcnow()
                        sync_log.status = 'error'
                        sync_log.message = 'Processo interrompido inesperadamente'
                        db.session.commit()
                        logger.warning(f"SyncLog finalizado no finally para user {user.id}")
                except Exception as e:
                    logger.error(f"Erro ao finalizar SyncLog no finally: {e}")
    
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
        Com rate limiting e delays entre usuários
        
        Returns:
            Dicionário com resultados por usuário
        """
        with self.app.app_context():
            users = User.query.filter_by(
                is_active=True,
                sync_enabled=True
            ).all()
            
            logger.info(f"Starting sync for {len(users)} users")
            
            # Verifica se está em cooldown
            if rate_limiter:
                stats = rate_limiter.get_stats()
                if stats['in_cooldown']:
                    remaining = stats['cooldown_remaining_seconds']
                    logger.warning(
                        f"⏳ Garmin em cooldown - pulando sincronização de {len(users)} usuários "
                        f"(restam {int(remaining)}s)"
                    )
                    return {'status': 'cooldown', 'remaining_seconds': remaining}
            
            results = {}
            for idx, user in enumerate(users, 1):
                if user.has_credentials():
                    try:
                        logger.info(f"Sincronizando usuário {idx}/{len(users)}: {user.email}")
                        results[user.id] = self.sync_user(user.id)
                        
                        # Delay entre usuários (exceto o último) - AUMENTADO para evitar rate limit
                        if idx < len(users):
                            delay = 30  # 30 segundos entre cada usuário (CONSERVADOR)
                            logger.info(f"⏳ Aguardando {delay}s antes do próximo usuário...")
                            time.sleep(delay)
                        
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Error syncing user {user.id}: {error_msg}")
                        results[user.id] = {'status': 'error', 'message': error_msg}
                        
                        # Se foi rate limit, para a sincronização
                        if "RATE_LIMIT" in error_msg:
                            logger.warning("⚠️ Rate limit detectado - parando sincronização de outros usuários")
                            break
                else:
                    logger.warning(f"User {user.email} has no credentials")
                    results[user.id] = {'status': 'no_credentials'}
            
            logger.info(f"Sync completed for {len(results)} users")
            
            return results
    
    def cleanup_orphaned_logs(self, timeout_minutes=10):
        """
        Limpa logs que ficaram em estado 'running' por muito tempo
        Considera órfãos logs que estão rodando há mais de {timeout_minutes} minutos
        
        Args:
            timeout_minutes: Minutos para considerar um log órfão
            
        Returns:
            Número de logs limpos
        """
        with self.app.app_context():
            timeout_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
            
            # Busca logs órfãos
            orphaned_logs = SyncLog.query.filter(
                SyncLog.status == 'running',
                SyncLog.started_at < timeout_threshold
            ).all()
            
            if not orphaned_logs:
                logger.info("✓ Nenhum log órfão encontrado")
                return 0
            
            logger.info(f"🧹 Limpando {len(orphaned_logs)} logs órfãos...")
            
            for log in orphaned_logs:
                log.finished_at = datetime.utcnow()
                log.status = 'timeout'
                log.message = f'Processo travou/timeout após {timeout_minutes} minutos'
                logger.info(f"  ✓ Log #{log.id} marcado como timeout (user_id={log.user_id})")
            
            db.session.commit()
            
            logger.success(f"✓ {len(orphaned_logs)} logs órfãos limpos")
            return len(orphaned_logs)
