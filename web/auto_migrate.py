"""
Auto-migração para adicionar colunas sem precisar do Flask-Migrate
Útil para planos gratuitos sem acesso ao shell
"""

from loguru import logger
from sqlalchemy import text, inspect


def auto_migrate_database(db):
    """
    Adiciona colunas que faltam no banco de dados
    Executa automaticamente ao iniciar o app
    """
    
    try:
        # Verifica se as tabelas existem
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' not in tables:
            logger.info("Tabela users não existe, será criada pelo db.create_all()")
            return
        
        # Lista de colunas que devem existir
        required_columns = {
            'nike_email_enc': 'TEXT',
            'nike_password_enc': 'TEXT',
            'nike_status': "VARCHAR(20) DEFAULT 'pending'",
            'nike_status_message': 'TEXT',
            'nike_configured_at': 'TIMESTAMP',
            'is_admin': 'BOOLEAN DEFAULT FALSE'
        }
        
        # Verifica colunas existentes
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Adiciona colunas faltantes
        added = 0
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                try:
                    # SQL para adicionar coluna
                    if db.engine.url.drivername.startswith('postgresql'):
                        # PostgreSQL
                        sql = f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    else:
                        # SQLite
                        sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                    
                    with db.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    
                    logger.info(f"✓ Coluna adicionada: {column_name}")
                    added += 1
                    
                except Exception as e:
                    logger.warning(f"Erro ao adicionar coluna {column_name}: {e}")
        
        if added > 0:
            logger.info(f"🎉 Auto-migração concluída: {added} colunas adicionadas")
        else:
            logger.info("✓ Banco de dados já está atualizado")
        
        # Atualiza usuários existentes que já têm token Nike
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    UPDATE users 
                    SET nike_status = 'active', 
                        nike_configured_at = NOW() 
                    WHERE nike_token_enc IS NOT NULL 
                      AND nike_token_enc != ''
                      AND (nike_status IS NULL OR nike_status = 'pending')
                """))
                conn.commit()
                
                if result.rowcount > 0:
                    logger.info(f"✓ {result.rowcount} usuários existentes atualizados para status 'active'")
        except Exception as e:
            logger.warning(f"Erro ao atualizar usuários existentes: {e}")
    
    except Exception as e:
        logger.error(f"Erro na auto-migração: {e}")
        # Não falha o app, só loga o erro
