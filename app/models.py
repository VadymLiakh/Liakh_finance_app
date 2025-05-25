from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import date
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.relationship('Role', backref='users')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    categories = db.relationship(
        'Category',
        backref='user',
        cascade="all, delete",
        passive_deletes=True
    )

    transactions = db.relationship(
        'Transaction',
        backref='user',
        cascade="all, delete",
        passive_deletes=True
    )

    def is_admin(self):
        return self.role and self.role.name == 'admin'

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.Enum('income', 'expense'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    category = db.relationship('Category')