import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.models import db
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.cnpj import cnpj_bp
from src.routes.orders import orders_bp
from src.routes.catalog import catalog_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Use variável de ambiente
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Para JWT

# Configuração CORS
CORS(app, resources={r"/api/*": {"origins": "https://representacao-frontend.onrender.com"}})

# Inicializa JWT
jwt = JWTManager(app)

# Registra os blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(cnpj_bp, url_prefix='/api/cnpj')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(catalog_bp, url_prefix='/api/catalog')

# Configuração do banco de dados (Supabase)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Cria as tabelas do banco de dados
with app.app_context():
    db.create_all()
    
    # Adiciona dados iniciais se necessário
    from src.models.models import PaymentMethod, Company, User, UserCompany, Product
    
    if PaymentMethod.query.count() == 0:
        payment_methods = [
            PaymentMethod(name='Dinheiro'),
            PaymentMethod(name='Cartão de Crédito'),
            PaymentMethod(name='Cartão de Débito'),
            PaymentMethod(name='PIX'),
            PaymentMethod(name='Boleto'),
            PaymentMethod(name='Transferência Bancária')
        ]
        for method in payment_methods:
            db.session.add(method)
    
    if User.query.count() == 0:
        company = Company(
            name='Empresa Exemplo Ltda',
            cnpj='12.345.678/0001-90'
        )
        db.session.add(company)
        db.session.flush()
        
        user = User(email='admin@exemplo.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.flush()
        
        user_company = UserCompany(user_id=user.id, company_id=company.id)
        db.session.add(user_company)
        
        products = [
            Product(
                company_id=company.id,
                code='CAMISETA-001',
                description='Camiseta Básica Algodão',
                value=29.90,
                sizes=['P', 'M', 'G', 'GG']
            ),
            Product(
                company_id=company.id,
                code='CALCA-001',
                description='Calça Jeans Masculina',
                value=89.90,
                sizes=['38', '40', '42', '44', '46']
            ),
            Product(
                company_id=company.id,
                code='TENIS-001',
                description='Tênis Esportivo',
                value=159.90,
                sizes=['37', '38', '39', '40', '41', '42', '43']
            )
        ]
        for product in products:
            db.session.add(product)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)