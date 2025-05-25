from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail
from app.models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація розширень
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Flask-Login: функція завантаження користувача
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'

    # Реєстрація blueprint-ів
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.transactions import transactions_bp
    from app.routes.categories import categories_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(settings_bp)

    return app
