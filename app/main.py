from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Fraud Detection System is running!"

@main.route('/auth/register')
def customer_register():
    return "Customer Registration Page"

@main.route('/admin/login')
def admin_login():
    return "Admin Login Page"
