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
from flask_migrate import Migrate


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
    # Usa caminho absoluto para SQLite para evitar problemas de cwd
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Caminho absoluto para o banco SQLite local
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = f'sqlite:///{os.path.join(basedir, "instance", "garmin_nike_sync.db")}'
        # Cria diretório instance se não existir
        os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info(f"Database URL configured: {database_url[:50]}...")
    
    # Custom config
    if config:
        app.config.update(config)
    
    # Inicializa extensões
    db.init_app(app)
    logger.info("SQLAlchemy initialized")
    
    # Flask-Migrate para migrações de banco
    migrate = Migrate(app, db)
    logger.info("Flask-Migrate initialized")
    
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
                             recent_logs=recent_logs,
                             now=datetime.utcnow())
    
    @app.route('/credentials', methods=['GET', 'POST'])
    @login_required
    def credentials():
        """Configurar credenciais Garmin e Nike"""
        if request.method == 'POST':
            data = request.form
            has_changes = False
            
            # Salva credenciais Garmin
            if data.get('garmin_email') and data.get('garmin_password'):
                current_user.set_garmin_credentials(
                    data['garmin_email'],
                    data['garmin_password']
                )
                has_changes = True
                logger.info(f"Garmin credentials updated for user: {current_user.email}")
                flash('Credenciais Garmin salvas com sucesso!', 'success')
            
            # Salva credenciais Nike (admin vai configurar manualmente)
            if data.get('nike_email') and data.get('nike_password'):
                current_user.set_nike_credentials(
                    data['nike_email'],
                    data['nike_password']
                )
                current_user.nike_status = 'pending'
                current_user.nike_status_message = 'Suas credenciais foram recebidas! Nossa equipe está configurando sua conta Nike. Você será notificado em breve.'
                has_changes = True
                
                # Log para admin ver
                logger.warning(f"⚠️ ADMIN ACTION REQUIRED - Nike credentials pending for user: {current_user.email} (ID: {current_user.id})")
                logger.info(f"Nike email: {data['nike_email']}")
                
                flash('Credenciais Nike recebidas! Configuraremos sua conta em até 24 horas.', 'info')
            
            if has_changes:
                db.session.commit()
            
            return redirect(url_for('credentials'))
        
        # GET - mostra formulário
        garmin_email, _ = current_user.get_garmin_credentials()
        nike_email, _ = current_user.get_nike_credentials()
        
        # Formata data de configuração
        nike_configured_at = None
        if current_user.nike_configured_at:
            nike_configured_at = current_user.nike_configured_at.strftime('%d/%m/%Y %H:%M')
        
        return render_template('credentials.html',
                             garmin_email=garmin_email or '',
                             nike_email=nike_email or '',
                             nike_status=current_user.nike_status or 'none',
                             nike_status_message=current_user.nike_status_message,
                             nike_configured_at=nike_configured_at)
    
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
            'last_sync': current_user.last_sync.isoformat() if current_user.last_sync else None,
            'has_nike_token': bool(current_user.nike_token_enc)
        })
    
    # ============= ADMIN ROUTES =============
    
    def admin_required(f):
        """Decorator para rotas que requerem admin"""
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash('Acesso negado. Apenas administradores.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_panel():
        """Painel administrativo - lista usuários pendentes"""
        # Usuários com Nike pendente
        pending_users = User.query.filter_by(nike_status='pending').all()
        
        # Usuários ativos
        active_users = User.query.filter_by(nike_status='active').all()
        
        # Usuários com erro
        error_users = User.query.filter_by(nike_status='error').all()
        
        # Todos os usuários
        all_users = User.query.order_by(User.created_at.desc()).all()
        
        return render_template('admin/panel.html',
                             pending_users=pending_users,
                             active_users=active_users,
                             error_users=error_users,
                             all_users=all_users)
    
    @app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_user_detail(user_id):
        """Detalhes do usuário e inserir token Nike"""
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'set_token':
                token = request.form.get('nike_token', '').strip()
                
                if len(token) < 50:
                    flash('Token muito curto. Verifique se copiou corretamente.', 'error')
                else:
                    # Remove aspas se houver
                    token = token.replace('"', '').replace("'", "")
                    
                    # Salva token
                    user.set_nike_token(token)
                    user.nike_status = 'active'
                    user.nike_status_message = '✅ Nike conectado com sucesso! Sincronização automática ativa.'
                    user.nike_configured_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.success(f"Admin activated Nike for user: {user.email}")
                    flash(f'Token Nike ativado para {user.email}!', 'success')
                    
                    return redirect(url_for('admin_panel'))
            
            elif action == 'set_error':
                error_msg = request.form.get('error_message', '').strip()
                
                user.nike_status = 'error'
                user.nike_status_message = error_msg or 'Erro ao configurar Nike. Verifique suas credenciais.'
                db.session.commit()
                
                logger.warning(f"Admin set error for user: {user.email}")
                flash(f'Status de erro definido para {user.email}', 'warning')
                
                return redirect(url_for('admin_panel'))
        
        # GET - mostra detalhes
        nike_email, nike_password = user.get_nike_credentials()
        
        return render_template('admin/user_detail.html',
                             user=user,
                             nike_email=nike_email,
                             nike_password=nike_password)
    
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
