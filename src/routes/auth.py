from flask import Blueprint, jsonify, request
from src.models.models import User, Company, UserCompany, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def jwt_login_required(f):
    """Decorator para verificar se o usuário está logado com JWT"""
    @jwt_required()
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
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
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Gera token JWT
        access_token = create_access_token(identity=user.id)
        
        # Busca empresas do usuário
        user_companies = db.session.query(UserCompany, Company).join(
            Company, UserCompany.company_id == Company.id
        ).filter(UserCompany.user_id == user.id).all()
        
        companies = [company.to_dict() for _, company in user_companies]
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'companies': companies,
            'token': access_token  # Adiciona o token na resposta
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_login_required
def logout():
    """Faz logout do usuário (JWT é stateless, logout é gerenciado no frontend)"""
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/select-company', methods=['POST'])
@jwt_login_required
def select_company():
    """Seleciona a empresa ativa para o usuário"""
    try:
        data = request.json
        
        if not data or 'company_id' not in data:
            return jsonify({'error': 'ID da empresa é obrigatório'}), 400
        
        # Converta company_id para string (se necessário)
        company_id = str(data['company_id'])
        
        current_user_id = get_jwt_identity()
        
        user_company = UserCompany.query.filter_by(
            user_id=current_user_id,
            company_id=company_id  # Agora garantido como string
        ).first()
        
        if not user_company:
            return jsonify({'error': 'Acesso negado à empresa'}), 403
        
        company = Company.query.get(company_id)
        
        return jsonify({
            'message': 'Empresa selecionada com sucesso',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_login_required
def get_current_user():
    """Retorna informações do usuário logado"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        response_data = {
            'user': user.to_dict(),
            'company_id': None,
            'company': None
        }
        
        # Busca a empresa selecionada (armazenada no banco ou em cache, se necessário)
        user_company = UserCompany.query.filter_by(user_id=current_user_id).first()
        if user_company:
            company = Company.query.get(user_company.company_id)
            response_data['company_id'] = company.id
            response_data['company'] = company.to_dict()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500