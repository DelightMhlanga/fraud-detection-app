from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from app.models import Admin
from app.extensions import db
import re
from flask import jsonify

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

@admin_auth_bp.route('/init_db')
def init_db():
    db.create_all()
    return jsonify({'message': 'Database tables created.'})

# 🔐 Admin Login

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin.dashboard'))
        else:
            # Redirect with error query parameter
            return redirect(url_for('admin_auth.login', error='invalid'))

    # Render login page with optional error notification
    error = request.args.get('error')
    response = make_response(render_template('admin_login.html', error=error))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
# 🔑 Admin Password Change


@admin_auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'admin_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_auth.login'))

    admin = Admin.query.get(session['admin_id'])
    field_errors = {}

    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        # Validate current password
        if not admin.check_password(current):
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
            return render_template('admin_change_password.html', field_errors=field_errors)

        # Update password
        admin.set_password(new)
        db.session.commit()
        flash('Password updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_change_password.html', field_errors={})

# 🚪 Admin Logout
@admin_auth_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('Please provide username and password.')

    response = make_response(redirect(url_for('admin_auth.login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response