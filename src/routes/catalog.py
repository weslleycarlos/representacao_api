from flask import Blueprint, jsonify, request
from src.models.models import Product, PaymentMethod, db, UserCompany
from src.routes.auth import jwt_login_required
from sqlalchemy import and_
from flask_jwt_extended import get_jwt_identity

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/products', methods=['GET'])
@jwt_login_required
def get_products():
    """Lista todos os produtos da empresa selecionada"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        products = Product.query.filter_by(company_id=company_id).all()
        
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@catalog_bp.route('/products', methods=['POST'])
@jwt_login_required
def create_product():
    """Cria um novo produto"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        data = request.json
        if not data:
            return jsonify({'error': 'Dados do produto são obrigatórios'}), 400
        
        required_fields = ['code', 'description', 'value']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        existing_product = Product.query.filter_by(
            company_id=company_id,
            code=data['code']
        ).first()
        if existing_product:
            return jsonify({'error': 'Código do produto já existe nesta empresa'}), 400
        
        product = Product(
            company_id=company_id,
            code=data['code'],
            description=data['description'],
            value=data['value'],
            sizes=data.get('sizes', [])
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Produto criado com sucesso',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@catalog_bp.route('/payment-methods', methods=['GET'])
@jwt_login_required
def get_payment_methods():
    """Lista todas as formas de pagamento ativas"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        
        payment_methods = PaymentMethod.query.filter_by(is_active=True).all()
        
        return jsonify([method.to_dict() for method in payment_methods]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@catalog_bp.route('/payment-methods', methods=['POST'])
@jwt_login_required
def create_payment_method():
    """Cria uma nova forma de pagamento"""
    try:
        user_id = get_jwt_identity()
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        
        data = request.json
        if not data or not data.get('name'):
            return jsonify({'error': 'Nome da forma de pagamento é obrigatório'}), 400
        
        existing_method = PaymentMethod.query.filter_by(name=data['name']).first()
        if existing_method:
            return jsonify({'error': 'Forma de pagamento já existe'}), 400
        
        payment_method = PaymentMethod(
            name=data['name'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(payment_method)
        db.session.commit()
        
        return jsonify({
            'message': 'Forma de pagamento criada com sucesso',
            'payment_method': payment_method.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500