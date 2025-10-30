import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Customer
from app import db
from app.utils.email_service import send_email
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
# 🔐 Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    field_errors = {}
    form_data = {}

    if request.method == 'POST':
        name = request.form['name']
        usual_location = request.form['location']
        device_info = request.form['device_info']
        email = request.form['email']
        password = request.form['password']

        form_data = {
            'name': name,
            'location': usual_location,
            'device_info': device_info,
            'email': email
        }

        # Validation rules
        name_valid = bool(re.fullmatch(r"[A-Za-z\`]+", name))
        email_valid = bool(re.fullmatch(r"[a-zA-Z0-9._%+-]+@gmail\.com", email))
        password_valid = len(password) >= 8 and bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

        if not name_valid:
            field_errors['name'] = "Name must contain only letters and special characters."

        if not email_valid:
            field_errors['email'] = "Email must be a valid Gmail address."

        if not password_valid:
            field_errors['password'] = "Password must be at least 8 characters and include special characters."

        existing = Customer.query.filter_by(email=email).first()
        if existing:
            field_errors['email'] = "Email already registered."

        if field_errors:
            return render_template('register.html', field_errors=field_errors, form_data=form_data)

        # All validations passed — create user
        hashed_pw = generate_password_hash(password)
        new_user = Customer(
            name=name,
            email=email,
            password_hash=hashed_pw,
            usual_location=usual_location,
            device_info=device_info
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template('register.html', field_errors={}, form_data={})
# 🔐 Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Customer.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# 🔑 Forgot Password
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = Customer.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email.')
            return redirect(url_for('auth.forgot_password'))

        reset_link = url_for('auth.reset_password', user_id=user.id, _external=True)

        subject = "🔐 Password Reset Request"
        body = f"""
Hi {user.name},

You requested to reset your password. Click the link below to set a new one:

{reset_link}

If you didn’t request this, please ignore this email.

Thanks,  
Fraud Detection System
"""
        send_email(user.email, subject, body)
        flash('Password reset link sent to your email.')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

# 🔑 Reset Password

@auth_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = Customer.query.get_or_404(user_id)
    field_errors = {}

    if request.method == 'POST':
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        # Password strength validation
        password_valid = (
            len(new) >= 8 and
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", new)
        )

        if not password_valid:
            field_errors['new_password'] = "Password must be at least 8 characters and include special characters."

        if new != confirm:
            field_errors['confirm_password'] = "Passwords do not match."

        if field_errors:
            return render_template('reset_password.html', user=user, field_errors=field_errors)

        user.password_hash = generate_password_hash(new)
        db.session.commit()
        flash('Password reset successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', user=user, field_errors={})

# 🏠 Dashboard
@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    user = Customer.query.get(session['user_id'])
    return render_template('customer_dashboard.html', user=user)

# 👤 Profile
@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    user = Customer.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# 🔒 Change Password

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user = Customer.query.get(session['user_id'])
    field_errors = {}

    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        # Validate current password
        if not check_password_hash(user.password_hash, current):
            field_errors['current_password'] = "Current password is incorrect."

        # Validate new password strength
        password_valid = (
            len(new) >= 8 and
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", new)
        )
        if not password_valid:
            field_errors['new_password'] = "Password must be at least 8 characters and include special characters."

        # Validate confirmation match
        if new != confirm:
            field_errors['confirm_password'] = "New passwords do not match."

        if field_errors:
            return render_template('change_password.html', user=user, field_errors=field_errors)

        # Update password
        user.password_hash = generate_password_hash(new)
        db.session.commit()

        # Send confirmation email
        subject = "🔐 Your Password Was Changed"
        body = f"""
Hi {user.name},

This is a confirmation that your password was successfully changed on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC.

If you did not make this change, please contact support immediately.

Thanks,  
Fraud Detection System
"""
        send_email(user.email, subject, body)

        flash('Password updated successfully. Confirmation email sent.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('change_password.html', user=user, field_errors={})
# 🚪 Logout
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('auth.login'))