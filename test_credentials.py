#!/usr/bin/env python3
"""
Script de teste para validar credenciais
Execute antes de fazer deploy no GitHub Actions
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Adiciona diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.garmin_client import GarminClient
from src.nike_client import NikeClient


def test_credentials():
    """Testa credenciais Garmin e Nike"""
    
    logger.info("=" * 60)
    logger.info("Teste de Credenciais - Garmin → Nike Sync")
    logger.info("=" * 60)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')
    nike_token = os.getenv('NIKE_ACCESS_TOKEN')
    
    # Validações básicas
    errors = []
    
    if not garmin_email:
        errors.append("❌ GARMIN_EMAIL não configurado")
    else:
        logger.info(f"✅ GARMIN_EMAIL: {garmin_email}")
    
    if not garmin_password:
        errors.append("❌ GARMIN_PASSWORD não configurado")
    else:
        logger.info(f"✅ GARMIN_PASSWORD: {'*' * len(garmin_password)}")
    
    if not nike_token:
        errors.append("❌ NIKE_ACCESS_TOKEN não configurado")
    else:
        token_preview = f"{nike_token[:10]}...{nike_token[-10:]}" if len(nike_token) > 20 else nike_token
        logger.info(f"✅ NIKE_ACCESS_TOKEN: {token_preview}")
    
    if errors:
        logger.error("\n".join(errors))
        logger.error("\nConfigure as variáveis no arquivo .env")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Testando Garmin Connect...")
    logger.info("=" * 60)
    
    # Testa Garmin
    try:
        garmin = GarminClient(garmin_email, garmin_password)
        
        if garmin.authenticate():
            logger.success("✅ Autenticação Garmin: OK")
            
            # Tenta buscar 1 atividade para validar
            activities = garmin.get_activities(limit=1)
            if activities:
                logger.success(f"✅ Busca de atividades: OK ({len(activities)} encontrada)")
                activity = activities[0]
                logger.info(f"   Última atividade: {activity['name']} - {activity['distance']/1000:.2f}km")
            else:
                logger.warning("⚠️  Nenhuma atividade encontrada (conta nova?)")
        else:
            logger.error("❌ Falha na autenticação Garmin")
            logger.error("   Verifique email e senha")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com Garmin: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("Testando Nike Run Club...")
    logger.info("=" * 60)
    
    # Testa Nike
    try:
        nike = NikeClient(nike_token)
        
        if nike.test_connection():
            logger.success("✅ Conexão Nike: OK")
            
            # Tenta buscar 1 atividade
            activities = nike.get_activities(limit=1)
            if activities:
                logger.success(f"✅ Busca de atividades: OK ({len(activities)} encontrada)")
                activity = activities[0]
                logger.info(f"   Última atividade: {activity['name']} - {activity['distance']/1000:.2f}km")
            else:
                logger.warning("⚠️  Nenhuma atividade encontrada (conta nova?)")
        else:
            logger.error("❌ Falha na conexão Nike")
            logger.error("   Token pode estar inválido ou expirado")
            logger.error("   Veja NIKE-TOKEN-GUIDE.md para obter novo token")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com Nike: {e}")
        return False
    
    # Sucesso!
    logger.info("\n" + "=" * 60)
    logger.success("✅ TODOS OS TESTES PASSARAM!")
    logger.info("=" * 60)
    logger.info("\nPróximos passos:")
    logger.info("1. Faça commit dos arquivos (exceto .env)")
    logger.info("2. Crie repositório no GitHub")
    logger.info("3. Configure Secrets no GitHub")
    logger.info("4. Ative GitHub Actions")
    logger.info("5. Execute o workflow manualmente")
    logger.info("\nVeja QUICKSTART.md para instruções detalhadas")
    
    return True


if __name__ == "__main__":
    # Remove handler padrão do loguru
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    try:
        success = test_credentials()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\nTeste cancelado pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        sys.exit(1)
