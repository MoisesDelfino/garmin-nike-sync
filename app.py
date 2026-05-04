"""
Garmin to Nike Sync - Web Application
Aplicação web para sincronização automática entre Garmin Connect e Nike Run Club
"""

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from loguru import logger
import sys

# Carrega variáveis de ambiente do .env
load_dotenv()

from web.models.database import db, User, SyncHistory, SyncLog
from web.sync_manager import SyncManager
from web.scheduler import init_scheduler
from web.nike_auth import nike_auth_bp
from web.auto_migrate import auto_migrate_database
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
    
    # Decorator para rotas admin
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
    
    # Cria tabelas (com tratamento de erro)
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database initialized successfully")
            
            # Auto-migração: adiciona colunas que faltam
            auto_migrate_database(db)
            
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
    
    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        """
        Rota de setup para criar o primeiro admin
        Acessível apenas se não houver admins no sistema
        """
        # Verifica se já existe algum admin
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            flash('Já existe um administrador no sistema.', 'info')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            setup_key = request.form.get('setup_key')
            
            # Verifica senha de setup (env var ADMIN_SETUP_PASSWORD ou padrão)
            expected_key = os.getenv('ADMIN_SETUP_PASSWORD', 'admin123')
            
            if setup_key != expected_key:
                flash('Chave de setup inválida.', 'danger')
                return render_template('setup.html')
            
            # Busca usuário por email
            user = User.query.filter_by(email=email).first()
            if not user:
                flash('Usuário não encontrado. Por favor, registre-se primeiro.', 'warning')
                return redirect(url_for('register'))
            
            # Torna admin
            user.is_admin = True
            db.session.commit()
            
            logger.info(f"🎉 First admin created: {user.email}")
            flash(f'Parabéns! {user.email} agora é administrador.', 'success')
            return redirect(url_for('login'))
        
        return render_template('setup.html')
    
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
                logger.info(f"💾 Salvando credenciais Garmin para user: {current_user.email}")
                logger.debug(f"  Email fornecido: {data['garmin_email'][:3]}***")
                logger.debug(f"  Senha fornecida: {len(data['garmin_password'])} caracteres")
                
                current_user.set_garmin_credentials(
                    data['garmin_email'],
                    data['garmin_password']
                )
                has_changes = True
                logger.success(f"✓ Credenciais Garmin armazenadas no objeto user")
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
                logger.info(f"💾 Fazendo commit das alterações no banco de dados...")
                try:
                    db.session.commit()
                    logger.success(f"✓ Credenciais salvas no banco de dados com sucesso!")
                    
                    # Verifica se salvou corretamente
                    test_email, test_pwd = current_user.get_garmin_credentials()
                    if test_email and test_pwd:
                        logger.success(f"✓ Verificação: Credenciais recuperadas com sucesso")
                        logger.debug(f"  Email recuperado na verificação: {test_email[:3]}***")
                    else:
                        logger.error(f"❌ PROBLEMA: Credenciais não puderam ser recuperadas após salvar!")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao fazer commit: {e}")
                    db.session.rollback()
                    flash('Erro ao salvar credenciais. Tente novamente.', 'danger')
                    raise
            
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
    @admin_required
    def settings():
        """Configurações de sincronização (somente admin)"""
        if request.method == 'POST':
            data = request.form
            
            current_user.sync_enabled = 'sync_enabled' in data
            
            # Processar datas de sincronização inicial
            start_date_str = data.get('initial_sync_start_date', '').strip()
            end_date_str = data.get('initial_sync_end_date', '').strip()
            
            if start_date_str:
                current_user.initial_sync_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                current_user.initial_sync_start_date = None
            
            if end_date_str:
                current_user.initial_sync_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                current_user.initial_sync_end_date = None
            
            # Manter historical_days por compatibilidade (não é mais exibido, mas mantém valor)
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
        
        # Verifica cooldown por usuário (previne spam de sincronização)
        from web.rate_limiter import rate_limiter
        can_sync, remaining = rate_limiter.check_user_cooldown(current_user.id)
        
        if not can_sync:
            minutes = remaining // 60
            seconds = remaining % 60
            return jsonify({
                'error': f'⏳ Por favor, aguarde {minutes}min {seconds}s antes de sincronizar novamente. Isso evita bloqueios do Garmin.'
            }), 429
        
        try:
            manager = SyncManager(app)
            result = manager.sync_user(current_user.id)
            
            # Marca que o usuário sincronizou (inicia cooldown)
            rate_limiter.mark_user_sync(current_user.id)
            
            return jsonify({
                'success': True,
                'message': 'Sincronização concluída',
                'stats': result
            })
        except Exception as e:
            logger.error(f"Manual sync error for user {current_user.id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/dashboard/upload')
    @login_required
    def upload_page():
        """Página de upload manual de atividades"""
        # Verifica se tem token Nike configurado
        if not current_user.nike_token_enc or current_user.nike_status != 'active':
            flash('Configure seu token Nike primeiro nas Credenciais', 'warning')
            return redirect(url_for('credentials'))
        
        return render_template('upload.html', user=current_user)
    
    @app.route('/upload/process', methods=['POST'])
    @login_required
    def upload_process():
        """Processa arquivos de atividades enviados"""
        # Verifica se tem token Nike configurado
        if not current_user.nike_token_enc or current_user.nike_status != 'active':
            return jsonify({'error': 'Token Nike não configurado'}), 400
        
        # Verifica se há arquivos
        if 'files' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        # Importa parser e clientes
        from src.file_parser import ActivityParser, validate_activity
        from src.nike_client import NikeClient
        
        # Inicializa cliente Nike
        nike_token = current_user.get_nike_token()
        nike_client = NikeClient(nike_token)
        
        results = []
        success_count = 0
        error_count = 0
        
        for file in files:
            filename = secure_filename(file.filename)
            
            try:
                # Lê conteúdo do arquivo
                file_content = file.read()
                
                # CSV é tratado diferentemente (contém múltiplas atividades)
                if filename.lower().endswith('.csv'):
                    logger.info(f"Processing CSV file: {filename}")
                    activities = ActivityParser.parse_csv_file(file_content)
                    
                    csv_success = 0
                    csv_errors = 0
                    
                    for activity in activities:
                        try:
                            # Valida atividade
                            if not validate_activity(activity):
                                csv_errors += 1
                                continue
                            
                            # Converte para formato Nike
                            nike_activity = {
                                'type': activity['type'],
                                'start_time': activity['start_time'].isoformat(),
                                'duration': int(activity['duration_seconds']),
                                'distance': activity['distance_meters'],
                                'calories': activity.get('calories') or 0,
                                'average_hr': activity.get('avg_heart_rate'),
                                'name': activity.get('activity_name', 'CSV Import')
                            }
                            
                            # Envia para Nike
                            response = nike_client.create_activity(nike_activity)
                            
                            # Verifica se foi criada com sucesso
                            if response:
                                # Registra no histórico
                                sync_history = SyncHistory(
                                    user_id=current_user.id,
                                    garmin_activity_id=f"csv_{activity['start_time'].strftime('%Y%m%d_%H%M%S')}",
                                    nike_activity_id=response,
                                    activity_name=activity.get('activity_name', 'CSV Import'),
                                    activity_type=activity['type'],
                                    distance=activity['distance_meters'] / 1000,
                                    duration=int(activity['duration_seconds']),
                                    synced_at=datetime.utcnow()
                                )
                                db.session.add(sync_history)
                                csv_success += 1
                            else:
                                logger.error(f"Nike API rejeitou atividade: {activity.get('activity_name')}")
                                csv_errors += 1
                            
                        except Exception as e:
                            logger.error(f"Error uploading activity from CSV: {e}")
                            csv_errors += 1
                    
                    # Resultado do CSV
                    if csv_success > 0:
                        results.append({
                            'filename': filename,
                            'status': 'success' if csv_errors == 0 else 'partial',
                            'message': f'{csv_success} atividades sincronizadas com sucesso' + (f', {csv_errors} com erro' if csv_errors > 0 else '')
                        })
                        success_count += 1
                    else:
                        results.append({
                            'filename': filename,
                            'status': 'error',
                            'message': f'Nenhuma atividade foi sincronizada ({csv_errors} erros)'
                        })
                        error_count += 1
                    
                else:
                    # Arquivos individuais (.FIT, .TCX, .GPX)
                    logger.info(f"Parsing file: {filename}")
                    activity = ActivityParser.parse_file(file_content, filename)
                    
                    # Valida atividade
                    if not validate_activity(activity):
                        raise ValueError("Atividade com dados inválidos")
                    
                    # Converte para formato Nike
                    nike_activity = {
                        'type': activity['type'],
                        'start_time': activity['start_time'].isoformat(),
                        'duration': int(activity['duration_seconds']),
                        'distance': activity['distance_meters'],
                        'calories': activity.get('calories') or 0,
                        'average_hr': activity.get('avg_heart_rate'),
                        'name': filename.rsplit('.', 1)[0]
                    }
                    
                    # Envia para Nike
                    logger.info(f"Uploading {filename} to Nike...")
                    response = nike_client.create_activity(nike_activity)
                    
                    # Verifica se foi criada com sucesso
                    if response:
                        # Registra no histórico
                        sync_history = SyncHistory(
                            user_id=current_user.id,
                            garmin_activity_id=f"upload_{filename}",
                            nike_activity_id=response,
                            activity_name=filename,
                            activity_type=activity['type'],
                            distance=activity['distance_meters'] / 1000,  # km
                            duration=int(activity['duration_seconds']),
                            synced_at=datetime.utcnow()
                        )
                        db.session.add(sync_history)
                        
                        results.append({
                            'filename': filename,
                            'status': 'success',
                            'message': f'Atividade enviada com sucesso! {activity["distance_meters"]/1000:.2f}km em {int(activity["duration_seconds"]/60)}min'
                        })
                        success_count += 1
                    else:
                        results.append({
                            'filename': filename,
                            'status': 'error',
                            'message': 'Nike API rejeitou a atividade. Verifique o token.'
                        })
                        error_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })
                error_count += 1
        
        # Commit das alterações
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error committing sync history: {e}")
            db.session.rollback()
        
        return jsonify({
            'success': success_count > 0,
            'total': len(files),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        })
    
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
    
    @app.route('/admin/logs/cleanup', methods=['POST'])
    @login_required
    @admin_required
    def admin_logs_cleanup():
        """Limpa logs órfãos que ficaram em estado 'running'"""
        try:
            manager = SyncManager(app)
            cleaned = manager.cleanup_orphaned_logs(timeout_minutes=10)
            
            flash(f'✓ {cleaned} logs órfãos foram limpos!', 'success')
        except Exception as e:
            logger.error(f"Erro ao limpar logs: {e}")
            flash(f'Erro ao limpar logs: {str(e)}', 'error')
        
        return redirect(url_for('admin_logs'))
    
    @app.route('/admin/logs')
    @login_required
    @admin_required
    def admin_logs():
        """Logs e histórico de sincronizações de todos os usuários"""
        # Parâmetros de filtro
        user_filter = request.args.get('user_id', type=int)
        status_filter = request.args.get('status')
        limit = request.args.get('limit', default=50, type=int)
        
        # Buscar logs de sincronização (últimas execuções)
        sync_logs_query = db.session.query(SyncLog, User)\
            .join(User, SyncLog.user_id == User.id)\
            .order_by(SyncLog.started_at.desc())
        
        if user_filter:
            sync_logs_query = sync_logs_query.filter(SyncLog.user_id == user_filter)
        
        if status_filter:
            sync_logs_query = sync_logs_query.filter(SyncLog.status == status_filter)
        
        sync_logs = sync_logs_query.limit(limit).all()
        
        # Buscar histórico de atividades sincronizadas
        sync_history_query = db.session.query(SyncHistory, User)\
            .join(User, SyncHistory.user_id == User.id)\
            .order_by(SyncHistory.synced_at.desc())
        
        if user_filter:
            sync_history_query = sync_history_query.filter(SyncHistory.user_id == user_filter)
        
        sync_history = sync_history_query.limit(limit).all()
        
        # Estatísticas gerais
        from sqlalchemy import func
        total_users = User.query.count()
        active_users = User.query.filter_by(nike_status='active', sync_enabled=True).count()
        total_synced = db.session.query(func.sum(User.total_synced)).scalar() or 0
        
        # Últimos erros
        recent_errors = db.session.query(SyncLog, User)\
            .join(User, SyncLog.user_id == User.id)\
            .filter(SyncLog.status == 'error')\
            .order_by(SyncLog.started_at.desc())\
            .limit(10)\
            .all()
        
        # Lista de usuários para filtro
        all_users = User.query.order_by(User.name).all()
        
        return render_template('admin/logs.html',
                             sync_logs=sync_logs,
                             sync_history=sync_history,
                             recent_errors=recent_errors,
                             total_users=total_users,
                             active_users=active_users,
                             total_synced=total_synced,
                             all_users=all_users,
                             current_filter_user=user_filter,
                             current_filter_status=status_filter)
    
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
    # Não usar sys.exit(1) aqui - deixa exceção propagar para gunicorn ver
    raise


# Ponto de entrada para desenvolvimento local
if __name__ == '__main__':
    # Configurar logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Modo desenvolvimento
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
