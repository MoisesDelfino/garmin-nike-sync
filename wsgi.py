"""
WSGI Entry Point
Ponto de entrada para servidores WSGI (gunicorn, etc.)
Com logging detalhado para debugging
"""

import sys
import os

# Adiciona diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("WSGI Entry Point - Starting...")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")
print("=" * 60)

# Configurar logging ANTES de importar app
from loguru import logger
logger.remove()  # Remove handlers padrão
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
logger.add(sys.stderr, level="ERROR", format="{time:HH:mm:ss} | {level} | {message}")

logger.info("Starting WSGI application initialization")

# Verificar variáveis de ambiente críticas
env_vars = {
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'ENCRYPTION_KEY': os.getenv('ENCRYPTION_KEY'),
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'PORT': os.getenv('PORT'),
}

logger.info("Environment variables check:")
for key, value in env_vars.items():
    if value:
        display_value = value[:15] + '...' if len(value) > 15 else value
        logger.info(f"  ✓ {key}: {display_value}")
    else:
        logger.warning(f"  ✗ {key}: NOT SET")

# Importar app
try:
    logger.info("Importing app module...")
    from app import app
    logger.info("✓ App imported successfully")
    
    logger.info(f"App config: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')[:30]}...")
    logger.info(f"App name: {app.name}")
    logger.info(f"App debug: {app.debug}")
    
    logger.info("=" * 60)
    logger.info("WSGI application ready!")
    logger.info("=" * 60)
    
except Exception as e:
    logger.error("=" * 60)
    logger.error("FATAL ERROR during app import:")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"Error message: {str(e)}")
    logger.error("=" * 60)
    logger.exception("Full traceback:")
    logger.error("=" * 60)
    
    # Re-raise para que o gunicorn também veja
    raise

# Exporta app para o gunicorn
application = app

if __name__ == '__main__':
    # Para testes locais
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
