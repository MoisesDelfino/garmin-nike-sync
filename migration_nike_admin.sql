-- Migração: Adicionar campos de status Nike e admin
-- Execute este script no banco de dados de produção

ALTER TABLE users ADD COLUMN IF NOT EXISTS nike_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE users ADD COLUMN IF NOT EXISTS nike_status_message TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS nike_configured_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Atualiza usuários existentes que já têm token Nike
UPDATE users 
SET nike_status = 'active', 
    nike_configured_at = NOW() 
WHERE nike_token_enc IS NOT NULL 
  AND nike_token_enc != '';

COMMIT;
