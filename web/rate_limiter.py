"""
Rate Limiter Global para Garmin
Evita bloqueios (429) controlando requisições ao Garmin Connect
"""

import time
import threading
from loguru import logger
from datetime import datetime, timedelta


class GarminRateLimiter:
    """
    Rate limiter global para controlar requisições ao Garmin Connect.
    Garante que não façamos muitas requisições em sequência.
    """
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Controle de requisições
        self._last_request_time = None
        self._request_lock = threading.Lock()
        
        # Configurações (ULTRA CONSERVADORAS para evitar bloqueios)
        self.min_interval_seconds = 45  # Mínimo de 45 segundos entre requisições
        self.cooldown_after_429 = 1800  # 30 minutos de cooldown após 429
        self.last_429_time = None
        
        # Cooldown por usuário (previne spam de sincronização manual)
        self._user_last_sync = {}  # {user_id: timestamp}
        self.per_user_cooldown = 300  # 5 minutos entre syncs do mesmo usuário
        
        # Estatísticas
        self.total_requests = 0
        self.total_delays = 0
        self.total_429_errors = 0
        
        self._initialized = True
        logger.info(f"✓ GarminRateLimiter inicializado (min_interval={self.min_interval_seconds}s)")
    
    def wait_if_needed(self):
        """
        Aguarda se necessário antes de fazer requisição ao Garmin.
        Retorna True se pode prosseguir, False se está em cooldown.
        """
        with self._request_lock:
            now = time.time()
            
            # Se teve 429 recentemente, verifica cooldown
            if self.last_429_time:
                time_since_429 = now - self.last_429_time
                if time_since_429 < self.cooldown_after_429:
                    remaining = self.cooldown_after_429 - time_since_429
                    logger.warning(
                        f"⏳ Garmin em cooldown após 429 - "
                        f"Aguarde {int(remaining)}s antes de tentar novamente"
                    )
                    return False
                else:
                    # Cooldown terminou
                    logger.info("✓ Cooldown do Garmin terminou, pode prosseguir")
                    self.last_429_time = None
            
            # Calcula tempo desde última requisição
            if self._last_request_time:
                elapsed = now - self._last_request_time
                
                if elapsed < self.min_interval_seconds:
                    wait_time = self.min_interval_seconds - elapsed
                    logger.info(
                        f"⏳ Rate limit: aguardando {wait_time:.1f}s antes de requisição ao Garmin"
                    )
                    time.sleep(wait_time)
                    self.total_delays += 1
            
            # Registra requisição
            self._last_request_time = time.time()
            self.total_requests += 1
            
            return True
    
    def report_429_error(self):
        """Registra que recebemos erro 429 do Garmin"""
        with self._request_lock:
            self.last_429_time = time.time()
            self.total_429_errors += 1
            
            logger.error(
                f"❌ Garmin retornou 429 (Rate Limit) - "
                f"Entrando em cooldown de {self.cooldown_after_429}s ({self.cooldown_after_429//60} minutos)"
            )
    
    def check_user_cooldown(self, user_id):
        """
        Verifica se o usuário específico está em cooldown.
        Retorna (pode_sincronizar, segundos_restantes)
        """
        with self._request_lock:
            if user_id not in self._user_last_sync:
                return True, 0
            
            elapsed = time.time() - self._user_last_sync[user_id]
            
            if elapsed < self.per_user_cooldown:
                remaining = self.per_user_cooldown - elapsed
                return False, int(remaining)
            
            return True, 0
    
    def mark_user_sync(self, user_id):
        """Marca que o usuário acabou de sincronizar"""
        with self._request_lock:
            self._user_last_sync[user_id] = time.time()
            logger.debug(f"User {user_id} marked for cooldown ({self.per_user_cooldown}s)")
    
    def get_stats(self):
        """Retorna estatísticas do rate limiter"""
        with self._request_lock:
            cooldown_remaining = None
            if self.last_429_time:
                elapsed = time.time() - self.last_429_time
                cooldown_remaining = max(0, self.cooldown_after_429 - elapsed)
            
            return {
                'total_requests': self.total_requests,
                'total_delays': self.total_delays,
                'total_429_errors': self.total_429_errors,
                'in_cooldown': cooldown_remaining is not None and cooldown_remaining > 0,
                'cooldown_remaining_seconds': cooldown_remaining,
                'last_request_ago_seconds': time.time() - self._last_request_time if self._last_request_time else None
            }
    
    def reset(self):
        """Reset do rate limiter (usar com cuidado!)"""
        with self._request_lock:
            self._last_request_time = None
            self.last_429_time = None
            logger.warning("⚠️ Rate limiter resetado manualmente")


# Singleton global
rate_limiter = GarminRateLimiter()
