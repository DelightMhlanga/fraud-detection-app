import os
from flask import Flask
from .extensions import db, migrate, mail

# Import blueprints
from .main import main
from .routes.admin import admin_bp  # ✅ Correct path to your admin blueprint
from .routes.admin_auth import admin_auth_bp


def create_app():
    app = Flask(__name__)

    # Load configuration from environment
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_auth_bp)

    return app