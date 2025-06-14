from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user_companies = db.relationship('UserCompany', back_populates='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash e define a senha do usuário"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user_companies = db.relationship('UserCompany', back_populates='company', cascade='all, delete-orphan')
    products = db.relationship('Product', back_populates='company', cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cnpj': self.cnpj,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserCompany(db.Model):
    __tablename__ = 'user_companies'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), primary_key=True)
    
    # Relacionamentos
    user = db.relationship('User', back_populates='user_companies')
    company = db.relationship('Company', back_populates='user_companies')

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    orders = db.relationship('Order', back_populates='client', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    orders = db.relationship('Order', back_populates='payment_method')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    code = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    sizes = db.Column(db.JSON)  # Ex: ['P', 'M', 'G', 'GG']
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    company = db.relationship('Company', back_populates='products')
    order_items = db.relationship('OrderItem', back_populates='product', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('company_id', 'code', name='_company_code_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'code': self.code,
            'description': self.description,
            'value': float(self.value) if self.value else 0,
            'sizes': self.sizes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    discount_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    total_value = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pendente')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', back_populates='orders')
    company = db.relationship('Company', back_populates='orders')
    client = db.relationship('Client', back_populates='orders')
    payment_method = db.relationship('PaymentMethod', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'client_id': self.client_id,
            'payment_method_id': self.payment_method_id,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'total_value': float(self.total_value) if self.total_value else 0,
            'status': self.status,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client': self.client.to_dict() if self.client else None,
            'payment_method': self.payment_method.to_dict() if self.payment_method else None,
            'items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.JSON, nullable=False)  # Ex: {'P': 10, 'M': 5, 'G': 2}
    unit_value = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_value': float(self.unit_value) if self.unit_value else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'product': self.product.to_dict() if self.product else None
        }

