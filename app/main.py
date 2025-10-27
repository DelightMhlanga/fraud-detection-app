from flask import Blueprint
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Fraud Detection System is running!"

@main.route('/customer/register')
def customer_register():
    return render_template('register.html')

@main.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')
