from flask import Blueprint, render_template, session, redirect, url_for, flash, request, make_response
from app.models import Transaction, Customer
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.extensions import db
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 🔍 Shared filter logic
def get_filtered_transactions():
    customer_name = request.args.get('customer_name')
    status = request.args.get('status')

    query = Transaction.query.join(Customer)

    if customer_name:
        query = query.filter(Customer.name.ilike(f"%{customer_name}%"))
    if status:
        query = query.filter(Transaction.status == status)

    return query.order_by(Transaction.timestamp.desc()).all()

# 📋 Dashboard with session check and cache prevention
@admin_bp.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        flash('Please provide username and password.')
        return redirect(url_for('admin_auth.login'))

    transactions = get_filtered_transactions()
    response = make_response(render_template('admin_dashboard.html', transactions=transactions))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# 👥 View all users
@admin_bp.route('/users')
def view_users():
    users = Customer.query.all()
    return render_template('admin_users.html', users=users)

# ❌ Delete user
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = Customer.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} has been deleted.')
    return redirect(url_for('admin.view_users'))

# 📤 Export to Excel with filters
@admin_bp.route('/export_excel')
def export_excel():
    if 'admin_id' not in session:
        flash('Please provide username and password.')
        return redirect(url_for('admin_auth.login'))

    transactions = get_filtered_transactions()

    data = [{
        'ID': txn.id,
        'Customer': txn.customer.name,
        'Amount': txn.amount,
        'Device': txn.device_info,
        'Location': txn.location,
        'Status': txn.status,
        'Time': txn.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for txn in transactions]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

# 📄 Export to PDF with filters
@admin_bp.route('/export_pdf')
def export_pdf():
    if 'admin_id' not in session:
        flash('Please provide username and password.')
        return redirect(url_for('admin_auth.login'))

    transactions = get_filtered_transactions()

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    y = height - 40

    pdf.setFont("Helvetica", 10)
    pdf.drawString(30, y, "Transaction Report")
    y -= 20

    for txn in transactions:
        line = f"{txn.id} | {txn.customer.name} | ${txn.amount} | {txn.device_info} | {txn.location} | {txn.status} | {txn.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        pdf.drawString(30, y, line)
        y -= 15
        if y < 40:
            pdf.showPage()
            y = height - 40

    pdf.save()
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.pdf'
    response.headers['Content-type'] = 'application/pdf'
    return response