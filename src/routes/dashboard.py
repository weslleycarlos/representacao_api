from flask import Blueprint, jsonify
from src.models.models import Order, Client, db
from src.routes.auth import jwt_login_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from flask_jwt_extended import get_jwt_identity
from src.models.models import UserCompany, Company

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/metrics', methods=['GET'])
@jwt_login_required
def get_dashboard_metrics():
    """Retorna métricas para o dashboard"""
    try:
        user_id = get_jwt_identity()
        
        # Obter company_id da associação UserCompany
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        # Data de hoje e ontem
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Data de 30 dias atrás e 60 dias atrás
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)
        
        # Pedidos hoje
        orders_today = Order.query.filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id,
                func.date(Order.order_date) == today,
                Order.status == 'Concluído'
            )
        ).count()
        
        # Pedidos ontem
        orders_yesterday = Order.query.filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id,
                func.date(Order.order_date) == yesterday,
                Order.status == 'Concluído'
            )
        ).count()
        
        # Variação percentual dos pedidos
        orders_variation = 0
        if orders_yesterday > 0:
            orders_variation = ((orders_today - orders_yesterday) / orders_yesterday) * 100
        elif orders_today > 0:
            orders_variation = 100
        
        # Valor total dos últimos 30 dias
        total_value_30_days = db.session.query(func.sum(Order.total_value)).filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id,
                Order.order_date >= thirty_days_ago,
                Order.status == 'Concluído'
            )
        ).scalar() or 0
        
        # Valor total dos 30 dias anteriores
        total_value_previous_30_days = db.session.query(func.sum(Order.total_value)).filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id,
                Order.order_date >= sixty_days_ago,
                Order.order_date < thirty_days_ago,
                Order.status == 'Concluído'
            )
        ).scalar() or 0
        
        # Variação percentual do valor
        value_variation = 0
        if total_value_previous_30_days > 0:
            value_variation = ((float(total_value_30_days) - float(total_value_previous_30_days)) / float(total_value_previous_30_days)) * 100
        elif total_value_30_days > 0:
            value_variation = 100
        
        # Últimos 5 pedidos
        latest_orders = Order.query.filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id
            )
        ).order_by(Order.order_date.desc()).limit(5).all()
        
        return jsonify({
            'orders_today': {
                'count': orders_today,
                'variation': round(orders_variation, 1)
            },
            'total_value_30_days': {
                'value': float(total_value_30_days),
                'variation': round(value_variation, 1)
            },
            'latest_orders': [order.to_dict() for order in latest_orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/pending-orders-count', methods=['GET'])
@jwt_login_required
def get_pending_orders_count():
    """Retorna a contagem de pedidos pendentes no banco"""
    try:
        user_id = get_jwt_identity()
        
        # Obter company_id da associação UserCompany
        user_company = UserCompany.query.filter_by(user_id=user_id).first()
        if not user_company:
            return jsonify({'error': 'Empresa não selecionada'}), 400
        company_id = user_company.company_id
        
        pending_count = Order.query.filter(
            and_(
                Order.user_id == user_id,
                Order.company_id == company_id,
                Order.status == 'Pendente'
            )
        ).count()
        
        return jsonify({'pending_orders': pending_count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500