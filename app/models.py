# app/models.py
from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usual_location = db.Column(db.String(100), nullable=True)  # ✅ Temporarily allow nulls
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_suspended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    device_info = db.Column(db.String(200), nullable=True)  # ✅ Add this line


    transactions = db.relationship(
        'Transaction',
        backref='customer',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    device_info = db.Column(db.String(200), nullable=True)  # ✅ Add this line
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # 'approved', 'fraudulent', 'confirmed'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)