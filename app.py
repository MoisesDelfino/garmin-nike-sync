"""
Garmin to Nike Sync - Web Application
Aplicação web para sincronização automática entre Garmin Connect e Nike Run Club
"""

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from loguru import logger
import sys

# Carrega variáveis de ambiente do .env
load_dotenv()

from web.models.database import db, User, SyncHistory, SyncLog
from web.sync_manager import SyncManager
from web.scheduler import init_scheduler
from web.nike_auth import nike_auth_bp


def create_app(config=None):
    """Factory para criar aplicação Flask"""
    
    logger.info("=== Starting Flask app creation ===")
    
    app = Flask(__name__, 
                template_folder='web/templates',
                static_folder='web/static')
    
    logger.info("Flask app instance created")
    
    # Configuração
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Fix DATABASE_URL para compatibilidade com SQLAlchemy 2.0+
    database_url = os.getenv('DATABASE_URL', 'sqlite:///garmin_nike_sync.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info(f"Database URL configured: {database_url[:20]}...")
    
    # Custom config
    if config:
        app.config.update(config)
    
    # Inicializa extensões
    db.init_app(app)
    logger.info("SQLAlchemy initialized")
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Cria tabelas (com tratamento de erro)
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Não falhar completamente, deixa app iniciar
    
    # Inicializa scheduler (sincronização automática)
    if not app.config.get('TESTING'):
        try:
            init_scheduler(app)
            logger.info("Scheduler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing scheduler: {e}")
            # Não falhar completamente, deixa app iniciar
    
    # Registra blueprints
    app.register_blueprint(nike_auth_bp)
    
    # ========== ROTAS ==========
    
    @app.route('/')
    def index():
        """Página inicial"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registro de novo usuário"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            data = request.form
            
            # Validações
            if User.query.filter_by(email=data['email']).first():
                flash('Email já cadastrado', 'error')
                return render_template('register.html')
            
            # Validar senhas
            if data['password'] != data.get('password_confirm', ''):
                flash('As senhas não coincidem', 'error')
                return render_template('register.html')
            
            if len(data['password']) < 6:
                flash('A senha deve ter no mínimo 6 caracteres', 'error')
                return render_template('register.html')
            
            # Cria usuário
            user = User(
                email=data['email'],
                name=data['name']
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {user.email}")
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login de usuário"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                logger.info(f"User logged in: {user.email}")
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Email ou senha incorretos', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout de usuário"""
        logger.info(f"User logged out: {current_user.email}")
        logout_user()
        flash('Você saiu da sua conta', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard do usuário"""
        # Últimas sincronizações
        recent_syncs = SyncHistory.query.filter_by(user_id=current_user.id)\
            .order_by(SyncHistory.synced_at.desc())\
            .limit(10)\
            .all()
        
        # Últimos logs
        recent_logs = SyncLog.query.filter_by(user_id=current_user.id)\
            .order_by(SyncLog.started_at.desc())\
            .limit(5)\
            .all()
        
        return render_template('dashboard.html',
                             user=current_user,
                             recent_syncs=recent_syncs,
                             recent_logs=recent_logs)
    
    @app.route('/credentials', methods=['GET', 'POST'])
    @login_required
    def credentials():
        """Configurar credenciais Garmin e Nike"""
        if request.method == 'POST':
            data = request.form
            
            # Salva credenciais Garmin
            if data.get('garmin_email') and data.get('garmin_password'):
                current_user.set_garmin_credentials(
                    data['garmin_email'],
                    data['garmin_password']
                )
                
                db.session.commit()
                
                logger.info(f"Garmin credentials updated for user: {current_user.email}")
                flash('Credenciais Garmin salvas com sucesso!', 'success')
            else:
                flash('Email e senha Garmin são obrigatórios', 'error')
            
            return redirect(url_for('credentials'))
        
        # GET - mostra formulário
        garmin_email, _ = current_user.get_garmin_credentials()
        
        return render_template('credentials.html',
                             garmin_email=garmin_email or '',
                             has_nike_token=bool(current_user.nike_token_enc))
    
    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        """Configurações de sincronização"""
        if request.method == 'POST':
            data = request.form
            
            current_user.sync_enabled = 'sync_enabled' in data
            current_user.historical_days = int(data.get('historical_days', 365))
            current_user.time_tolerance = int(data.get('time_tolerance', 300))
            current_user.distance_tolerance = int(data.get('distance_tolerance', 50))
            
            db.session.commit()
            
            logger.info(f"Settings updated for user: {current_user.email}")
            flash('Configurações atualizadas!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('settings.html')
    
    @app.route('/sync/manual', methods=['POST'])
    @login_required
    def manual_sync():
        """Sincronização manual"""
        if not current_user.has_credentials():
            return jsonify({'error': 'Credenciais não configuradas'}), 400
        
        try:
            manager = SyncManager(app)
            result = manager.sync_user(current_user.id)
            
            return jsonify({
                'success': True,
                'message': 'Sincronização concluída',
                'stats': result
            })
        except Exception as e:
            logger.error(f"Manual sync error for user {current_user.id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/history')
    @login_required
    def api_history():
        """API: Histórico de sincronizações"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = SyncHistory.query.filter_by(user_id=current_user.id)\
            .order_by(SyncHistory.synced_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    
    @app.route('/api/logs')
    @login_required
    def api_logs():
        """API: Logs de sincronização"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = SyncLog.query.filter_by(user_id=current_user.id)\
            .order_by(SyncLog.started_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    
    @app.route('/api/stats')
    @login_required
    def api_stats():
        """API: Estatísticas do usuário"""
        # Total sincronizado
        total = SyncHistory.query.filter_by(
            user_id=current_user.id,
            sync_status='synced'
        ).count()
        
        # Últimos 7 dias
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent = SyncHistory.query.filter(
            SyncHistory.user_id == current_user.id,
            SyncHistory.synced_at >= week_ago
        ).count()
        
        # Por tipo de atividade
        from sqlalchemy import func
        by_type = db.session.query(
            SyncHistory.activity_type,
            func.count(SyncHistory.id)
        ).filter_by(user_id=current_user.id)\
         .group_by(SyncHistory.activity_type)\
         .all()
        
        return jsonify({
            'total_synced': total,
            'last_7_days': recent,
            'by_type': {t[0]: t[1] for t in by_type if t[0]},
            'last_sync': current_user.last_sync.isoformat() if current_user.last_sync else None
        })
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    logger.info("=== Flask app created successfully ===")
    return app


# Cria instância do app para o gunicorn em produção
try:
    logger.info("Creating app instance for gunicorn...")
    app = create_app()
    logger.info("App instance created successfully for gunicorn")
except Exception as e:
    logger.error(f"FATAL: Failed to create app instance: {e}")
    logger.exception("Full traceback:")
    import sys
    sys.exit(1)


# Ponto de entrada para desenvolvimento local
if __name__ == '__main__':
    # Configurar logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Modo desenvolvimento
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
