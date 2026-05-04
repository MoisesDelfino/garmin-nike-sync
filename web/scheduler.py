"""
Background Scheduler
Executa sincronização automática para todos os usuários
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from loguru import logger
import atexit

from web.sync_manager import SyncManager


scheduler = None


def sync_all_users_job(app):
    """Job que sincroniza todos os usuários"""
    try:
        logger.info("=== Starting scheduled sync for all users ===")
        
        manager = SyncManager(app)
        results = manager.sync_all_users()
        
        success_count = sum(1 for r in results.values() if r.get('status') != 'error')
        error_count = sum(1 for r in results.values() if r.get('status') == 'error')
        
        logger.info(f"=== Scheduled sync completed: {success_count} success, {error_count} errors ===")
        
    except Exception as e:
        logger.error(f"Error in scheduled sync job: {e}")


def init_scheduler(app):
    """
    Inicializa scheduler de sincronização automática
    
    Args:
        app: Instância Flask app
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return
    
    # Intervalo de sincronização (padrão: 15 minutos)
    sync_interval = int(app.config.get('SYNC_INTERVAL_MINUTES', 15))
    
    logger.info(f"Initializing scheduler with {sync_interval} minutes interval")
    
    # Cria scheduler
    scheduler = BackgroundScheduler()
    
    # Adiciona job de sincronização
    scheduler.add_job(
        func=lambda: sync_all_users_job(app),
        trigger=IntervalTrigger(minutes=sync_interval),
        id='sync_all_users',
        name='Sync all users',
        replace_existing=True
    )
    
    # Inicia scheduler
    scheduler.start()
    logger.info("Scheduler started successfully")
    
    # Registra shutdown handler
    atexit.register(lambda: shutdown_scheduler())


def shutdown_scheduler():
    """Desliga scheduler graciosamente"""
    global scheduler
    
    if scheduler is not None:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler shut down successfully")


def get_scheduler_status():
    """
    Retorna status do scheduler
    
    Returns:
        Dicionário com informações do scheduler
    """
    global scheduler
    
    if scheduler is None:
        return {'running': False}
    
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': next_run.isoformat() if next_run else None
        })
    
    return {
        'running': scheduler.running,
        'jobs': jobs
    }
