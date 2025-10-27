# app/routes/orders.py
from flask import Blueprint

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/place')
def place_order():
    return "Order placement route is working!"