from flask import Blueprint, jsonify, request
from src.models.models import User, db, UserCompany
from src.routes.auth import jwt_login_required
from flask_jwt_extended import get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@jwt_login_required
def get_users():
    """Lista todos os usuários associados à empresa do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        users = User.query.join(UserCompany).filter(UserCompany.company_id == company_id).all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
@jwt_login_required
def create_user():
    """Cria um novo usuário associado à empresa do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        data = request.json
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        user = User(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        user_company = UserCompany(user_id=user.id, company_id=company_id)
        db.session.add(user_company)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_login_required
def get_user(user_id):
    """Obtém detalhes de um usuário específico"""
    try:
        current_user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=current_user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        user = User.query.join(UserCompany).filter(
            User.id == user_id,
            UserCompany.company_id == company_id
        ).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado ou não autorizado'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_login_required
def update_user(user_id):
    """Atualiza um usuário específico"""
    try:
        current_user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=current_user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        user = User.query.join(UserCompany).filter(
            User.id == user_id,
            UserCompany.company_id == company_id
        ).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado ou não autorizado'}), 404
        
        data = request.json
        user.email = data.get('email', user.email)
        if data.get('password'):
            user.set_password(data['password'])
        db.session.commit()
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_login_required
def delete_user(user_id):
    """Deleta um usuário específico"""
    try:
        current_user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=current_user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        user = User.query.join(UserCompany).filter(
            User.id == user_id,
            UserCompany.company_id == company_id
        ).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado ou não autorizado'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500