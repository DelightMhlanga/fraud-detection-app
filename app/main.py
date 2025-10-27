from flask import Blueprint, render_template, request, redirect, url_for, flash, session

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Fraud Detection System is running!"

@main.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        # Handle customer registration logic here
        return "Customer registration submitted!"
    return render_template('register.html')

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Redirect to the actual login logic in admin_auth blueprint
    return redirect(url_for('admin_auth.login'))