from flask import Blueprint, jsonify, request, session
from src.models.models import User, Company, UserCompany, db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Verifica se o usuário já existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Cria novo usuário
        user = User(email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Busca o usuário
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Cria sessão
        session['user_id'] = user.id
        
        # Busca empresas do usuário
        user_companies = db.session.query(UserCompany, Company).join(
            Company, UserCompany.company_id == Company.id
        ).filter(UserCompany.user_id == user.id).all()
        
        companies = [company.to_dict() for _, company in user_companies]
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'companies': companies
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Faz logout do usuário"""
    session.pop('user_id', None)
    session.pop('company_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/select-company', methods=['POST'])
@login_required
def select_company():
    """Seleciona a empresa ativa para o usuário"""
    try:
        data = request.json
        
        if not data or not data.get('company_id'):
            return jsonify({'error': 'ID da empresa é obrigatório'}), 400
        
        # Verifica se o usuário tem acesso à empresa
        user_company = UserCompany.query.filter_by(
            user_id=session['user_id'],
            company_id=data['company_id']
        ).first()
        
        if not user_company:
            return jsonify({'error': 'Acesso negado à empresa'}), 403
        
        # Define a empresa ativa na sessão
        session['company_id'] = data['company_id']
        
        company = Company.query.get(data['company_id'])
        
        return jsonify({
            'message': 'Empresa selecionada com sucesso',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Retorna informações do usuário logado"""
    try:
        user = User.query.get(session['user_id'])
        
        response_data = {
            'user': user.to_dict(),
            'company_id': session.get('company_id')
        }
        
        if session.get('company_id'):
            company = Company.query.get(session['company_id'])
            response_data['company'] = company.to_dict() if company else None
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

