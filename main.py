#!/usr/bin/env python3
"""
Garmin to Nike Run Club Sync
Script principal para sincronização automática de atividades

Suporta:
- Single-user: Configuração via variáveis de ambiente (compatibilidade)
- Multi-user: Configuração via config/users.json (múltiplas contas)
"""

import os
import sys
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

from src.garmin_client import GarminClient
from src.nike_client import NikeClient
from src.synchronizer import Synchronizer
from src.multi_user import MultiUserManager


def setup_logging():
    """Configura sistema de logs"""
    # Remove handler padrão
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Arquivo de log
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        f"{log_dir}/sync_{{time:YYYY-MM-DD}}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )


def load_config() -> dict:
    """
    Carrega configurações do ambiente
    
    Returns:
        Dicionário com configurações
    """
    # Carrega .env se existir
    load_dotenv()
    
    # Validar variáveis obrigatórias
    required_vars = [
        'GARMIN_EMAIL',
        'GARMIN_PASSWORD',
        'NIKE_ACCESS_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        logger.info("Configure as variáveis no arquivo .env ou GitHub Secrets")
        sys.exit(1)
    
    return {
        'garmin_email': os.getenv('GARMIN_EMAIL'),
        'garmin_password': os.getenv('GARMIN_PASSWORD'),
        'nike_token': os.getenv('NIKE_ACCESS_TOKEN'),
        'sync_interval': int(os.getenv('SYNC_INTERVAL_MINUTES', 15)),
        'historical_days': int(os.getenv('HISTORICAL_SYNC_DAYS', 365)),
        'time_tolerance': int(os.getenv('DUPLICATE_TIME_TOLERANCE_SECONDS', 300)),
        'distance_tolerance': int(os.getenv('DUPLICATE_DISTANCE_TOLERANCE_METERS', 50))
    }


def main():
    """Função principal"""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Garmin → Nike Run Club Sync")
    logger.info(f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Carrega configurações
    load_dotenv()
    
    # Detecta modo de operação
    config_file = "config/users.json"
    use_multi_user = os.path.exists(config_file)
    
    if use_multi_user:
        logger.info("🔄 Modo: MULTI-USER")
        run_multi_user_sync()
    else:
        logger.info("👤 Modo: SINGLE-USER (compatibilidade)")
        run_single_user_sync()


def run_multi_user_sync():
    """Executa sincronização multi-usuário"""
    try:
        manager = MultiUserManager()
        
        # Verifica se há usuários configurados
        users = manager.get_enabled_users()
        if not users:
            logger.error("Nenhum usuário configurado com credenciais válidas")
            logger.info("Configure usuários em config/users.json")
            sys.exit(1)
        
        # Determina se é primeira execução (qualquer usuário sem histórico)
        is_first_run = False
        for user in users:
            history_file = user.get_history_file()
            if not os.path.exists(history_file):
                is_first_run = True
                break
        
        # Sincroniza todos os usuários
        results = manager.sync_all_users(is_first_run=is_first_run)
        
        # Verifica se houve erros
        total_errors = sum(r['errors'] for r in results.values())
        if total_errors > 0:
            logger.warning(f"Sincronização completada com {total_errors} erro(s)")
            sys.exit(1)
        else:
            logger.success("Sincronização multi-user completada com sucesso!")
            sys.exit(0)
            
    except Exception as e:
        logger.exception(f"Erro na sincronização multi-user: {e}")
        sys.exit(1)


def run_single_user_sync():
    """Executa sincronização single-user (modo compatibilidade)"""
    config = load_config()
    
    # Inicializa clientes
    logger.info("Inicializando clientes...")
    garmin = GarminClient(config['garmin_email'], config['garmin_password'])
    nike = NikeClient(config['nike_token'])
    
    # Testa conexões
    if not garmin.authenticate():
        logger.error("Falha na autenticação Garmin")
        sys.exit(1)
    
    if not nike.test_connection():
        logger.error("Falha na conexão Nike")
        sys.exit(1)
    
    # Inicializa sincronizador
    sync = Synchronizer(
        garmin,
        nike,
        time_tolerance=config['time_tolerance'],
        distance_tolerance=config['distance_tolerance']
    )
    
    # Verifica se é primeira execução
    stats_before = sync.get_sync_stats()
    is_first_run = stats_before['total_synced'] == 0
    
    if is_first_run:
        logger.info("Primeira execução detectada - sincronizando histórico")
        stats = sync.sync_historical(days=config['historical_days'])
    else:
        logger.info("Sincronizando apenas novas atividades")
        stats = sync.sync_new_activities()
    
    # Exibe resultado
    logger.info("")
    logger.info("=" * 60)
    logger.info("Resultado da Sincronização:")
    logger.info(f"  Total de atividades: {stats['total']}")
    logger.info(f"  ✅ Sincronizadas: {stats['synced']}")
    logger.info(f"  ⏭️  Duplicadas: {stats['skipped_duplicate']}")
    logger.info(f"  ⏭️  Já sincronizadas: {stats['skipped_already_synced']}")
    logger.info(f"  ❌ Erros: {stats['errors']}")
    
    # Estatísticas gerais
    stats_after = sync.get_sync_stats()
    logger.info("")
    logger.info("Estatísticas Gerais:")
    logger.info(f"  Total sincronizado (histórico): {stats_after['total_synced']}")
    logger.info("=" * 60)
    
    # Exit code baseado em erros
    if stats['errors'] > 0:
        logger.warning(f"Sincronização completada com {stats['errors']} erro(s)")
        sys.exit(1)
    else:
        logger.success("Sincronização completada com sucesso!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Sincronização cancelada pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        sys.exit(1)
