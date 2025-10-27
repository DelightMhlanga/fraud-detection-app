from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate(app, db)  # ✅ Initialize after app is created

    # Import models so they’re registered
    from app import models

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.orders import orders_bp
    from app.routes.transactions import transactions_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(admin_bp)

    return app
    