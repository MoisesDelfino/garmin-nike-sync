"""
Nike OAuth Flow Helper
Gerencia o fluxo de autenticação com Nike
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from loguru import logger

nike_auth_bp = Blueprint('nike_auth', __name__)


@nike_auth_bp.route('/nike/connect')
@login_required
def nike_connect():
    """Página para conectar conta Nike - mobile only (simplificado)"""
    return render_template('nike_connect_mobile.html')


@nike_auth_bp.route('/nike/callback', methods=['POST'])
@login_required
def nike_callback():
    """Recebe o token extraído do Nike"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token or len(token) < 50:
            return jsonify({'error': 'Token inválido'}), 400
        
        # Salva o token do usuário
        current_user.set_nike_token(token)
        
        from web.models.database import db
        db.session.commit()
        
        logger.info(f"Token Nike salvo para usuário {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Token Nike salvo com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar token Nike: {e}")
        return jsonify({'error': str(e)}), 500
