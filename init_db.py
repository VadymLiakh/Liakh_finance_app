from app import create_app, db
from werkzeug.security import generate_password_hash
from app.models import User, Category, Transaction, Role
from dotenv import load_dotenv
import os

load_dotenv()
app = create_app()

def seed_roles():
    with app.app_context():
        db.create_all()
        if not Role.query.filter_by(name='user').first():
            db.session.add(Role(name='user'))
        if not Role.query.filter_by(name='admin').first():
            db.session.add(Role(name='admin'))
        db.session.commit()
        print("Ролі додано.")

def create_admin():
    with app.app_context():
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not admin_email or not admin_password:
            print("ADMIN_EMAIL або ADMIN_PASSWORD не вказано у .env")
            return

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Роль 'admin' не знайдена.")
            return

        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username="admin",
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                role=admin_role
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Адміністратор створений!")
        else:
            print("ℹ️ Адміністратор вже існує.")

        admin = User.query.filte
