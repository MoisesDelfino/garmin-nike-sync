"""
Database Models
Modelos de dados para aplicação web
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
import base64

db = SQLAlchemy()


def get_encryption_key():
    """Obtém ou cria chave de criptografia"""
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # Gera chave se não existir (desenvolvimento)
        key = Fernet.generate_key().decode()
    return key.encode()


class User(UserMixin, db.Model):
    """Modelo de usuário da aplicação"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Credenciais Garmin (criptografadas)
    garmin_email_enc = db.Column(db.Text)
    garmin_password_enc = db.Column(db.Text)
    
    # Credenciais Nike (criptografadas)
    nike_email_enc = db.Column(db.Text)
    nike_password_enc = db.Column(db.Text)
    
    # Token Nike (criptografado) - obtido automaticamente via credenciais
    nike_token_enc = db.Column(db.Text)
    
    # Configurações de sincronização
    sync_enabled = db.Column(db.Boolean, default=True)
    historical_days = db.Column(db.Integer, default=365)
    time_tolerance = db.Column(db.Integer, default=300)  # segundos
    distance_tolerance = db.Column(db.Integer, default=50)  # metros
    
    # Estatísticas
    total_synced = db.Column(db.Integer, default=0)
    last_sync_status = db.Column(db.String(50))  # 'success', 'error', 'pending'
    last_sync_message = db.Column(db.Text)
    
    # Relacionamento com histórico
    sync_history = db.relationship('SyncHistory', backref='user', lazy='dynamic',
                                   cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define senha do usuário (hash)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica senha do usuário"""
        return check_password_hash(self.password_hash, password)
    
    def _get_cipher(self):
        """Obtém cipher para criptografia"""
        key = get_encryption_key()
        return Fernet(key)
    
    def set_garmin_credentials(self, email, password):
        """Armazena credenciais Garmin (criptografadas)"""
        cipher = self._get_cipher()
        self.garmin_email_enc = cipher.encrypt(email.encode()).decode()
        self.garmin_password_enc = cipher.encrypt(password.encode()).decode()
    
    def get_garmin_credentials(self):
        """Recupera credenciais Garmin (descriptografadas)"""
        if not self.garmin_email_enc or not self.garmin_password_enc:
            return None, None
        
        cipher = self._get_cipher()
        email = cipher.decrypt(self.garmin_email_enc.encode()).decode()
        password = cipher.decrypt(self.garmin_password_enc.encode()).decode()
        return email, password
    
    def set_nike_credentials(self, email, password):
        """Armazena credenciais Nike (criptografadas)"""
        cipher = self._get_cipher()
        self.nike_email_enc = cipher.encrypt(email.encode()).decode()
        self.nike_password_enc = cipher.encrypt(password.encode()).decode()
    
    def get_nike_credentials(self):
        """Recupera credenciais Nike (descriptografadas)"""
        if not self.nike_email_enc or not self.nike_password_enc:
            return None, None
        
        cipher = self._get_cipher()
        email = cipher.decrypt(self.nike_email_enc.encode()).decode()
        password = cipher.decrypt(self.nike_password_enc.encode()).decode()
        return email, password
    has_garmin = bool(self.garmin_email_enc and self.garmin_password_enc)
        has_nike = bool(self.nike_email_enc and self.nike_password_enc)
        return has_garmin and has_nikerafado)"""
        cipher = self._get_cipher()
        self.nike_token_enc = cipher.encrypt(token.encode()).decode()
    
    def get_nike_token(self):
        """Recupera token Nike (descriptografado)"""
        if not self.nike_token_enc:
            return None
        
        cipher = self._get_cipher()
        return cipher.decrypt(self.nike_token_enc.encode()).decode()
    
    def has_credentials(self):
        """Verifica se usuário tem credenciais configuradas"""
        return bool(self.garmin_email_enc and 
                   self.garmin_password_enc and 
                   self.nike_token_enc)
    
    def to_dict(self):
        """Converte usuário para dicionário (sem dados sensíveis)"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'is_active': self.is_active,
            'sync_enabled': self.sync_enabled,
            'has_credentials': self.has_credentials(),
            'total_synced': self.total_synced,
            'last_sync_status': self.last_sync_status,
            'settings': {
                'historical_days': self.historical_days,
                'time_tolerance': self.time_tolerance,
                'distance_tolerance': self.distance_tolerance
            }
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class SyncHistory(db.Model):
    """Histórico de sincronizações"""
    
    __tablename__ = 'sync_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # IDs das atividades
    garmin_activity_id = db.Column(db.String(50), nullable=False)
    nike_activity_id = db.Column(db.String(50))
    
    # Dados da atividade
    activity_name = db.Column(db.String(200))
    activity_type = db.Column(db.String(50))
    distance = db.Column(db.Float)  # em metros
    duration = db.Column(db.Integer)  # em segundos
    activity_date = db.Column(db.DateTime)
    
    # Dados da sincronização
    synced_at = db.Column(db.DateTime, default=datetime.utcnow)
    sync_status = db.Column(db.String(20))  # 'synced', 'duplicate', 'error'
    
    def to_dict(self):
        """Converte histórico para dicionário"""
        return {
            'id': self.id,
            'garmin_id': self.garmin_activity_id,
            'nike_id': self.nike_activity_id,
            'name': self.activity_name,
            'type': self.activity_type,
            'distance': self.distance,
            'duration': self.duration,
            'date': self.activity_date.isoformat() if self.activity_date else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'status': self.sync_status
        }
    
    def __repr__(self):
        return f'<SyncHistory {self.garmin_activity_id}>'


class SyncLog(db.Model):
    """Logs de execução de sincronização"""
    
    __tablename__ = 'sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    
    status = db.Column(db.String(20))  # 'success', 'error', 'running'
    message = db.Column(db.Text)
    
    # Estatísticas
    total_found = db.Column(db.Integer, default=0)
    total_synced = db.Column(db.Integer, default=0)
    total_duplicates = db.Column(db.Integer, default=0)
    total_errors = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Converte log para dicionário"""
        return {
            'id': self.id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'message': self.message,
            'stats': {
                'found': self.total_found,
                'synced': self.total_synced,
                'duplicates': self.total_duplicates,
                'errors': self.total_errors
            }
        }
    
    def __repr__(self):
        return f'<SyncLog {self.id} - {self.status}>'
