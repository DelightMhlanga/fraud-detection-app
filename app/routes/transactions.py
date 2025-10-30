from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Transaction, Customer
from app import db
from datetime import datetime
from app.utils.email_service import send_email  # ✅ Email helper
from fraud_model import predict  # ✅ Import your model predictor

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

# 🧾 Submit Transaction
@transactions_bp.route('/submit', methods=['GET', 'POST'])
def submit_transaction():
    customer_id = session.get('user_id')
    if not customer_id:
        flash("⚠️ Session expired. Please log in again.")
        return redirect(url_for('auth.login'))

    customer = Customer.query.get(customer_id)
    if not customer:
        flash("⚠️ Account not found. Please log in again.")
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))

    field_errors = {}
    form_data = {}

    if request.method == 'POST':
        amount_raw = request.form.get('amount', '').strip()
        device_info = request.form.get('device_info', '').strip()
        location = request.form.get('location', '').strip()

        form_data = {
            'amount': amount_raw,
            'device_info': device_info,
            'location': location
        }

        # Validate amount
        try:
            amount = float(amount_raw)
            if amount < 1:
                field_errors['amount'] = "Amount must be at least $1."
        except ValueError:
            field_errors['amount'] = "Amount must be a valid number."

        if not device_info:
            field_errors['device_info'] = "Device info is required."

        if not location:
            field_errors['location'] = "Location is required."

        if field_errors:
            return render_template(
                'submit_transaction.html',
                user=customer,
                error=None,
                status=None,
                form_data=form_data,
                field_errors=field_errors
            )

        # Prepare transaction data
        txn_data = {
            'amount': amount,
            'timestamp': datetime.utcnow(),
            'location': location,
            'device_info': device_info,
            'usual_location': customer.usual_location,
            'usual_device': customer.device_info
        }

        is_fraud = predict.predict_fraud(txn_data)
        status = 'fraudulent' if is_fraud == 1 else 'approved'

        txn = Transaction(
            customer_id=customer_id,
            amount=amount,
            device_info=device_info,
            location=location,
            status=status,
            timestamp=txn_data['timestamp']
        )
        db.session.add(txn)
        db.session.commit()

        # Send email if flagged
        if status == 'fraudulent':
            subject = "⚠️ Confirm Your Transaction"
            body = f"""
Hi {customer.name},

We detected a potentially fraudulent transaction:
- Amount: ${amount}
- Device: {device_info}
- Location: {location}
- Time: {txn.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

If this was you, click here to confirm:
{url_for('transactions.confirm_fraud', txn_id=txn.id, confirm='yes', _external=True)}

If this was NOT you, click here to report fraud:
{url_for('transactions.confirm_fraud', txn_id=txn.id, confirm='no', _external=True)}

Thanks,  
Fraud Detection System
"""
            try:
                send_email(customer.email, subject, body)
            except Exception as e:
                print(f"❌ Email failed: {e}")

        return redirect(url_for('transactions.submit_transaction', status=status))

    # GET request
    error = request.args.get('error')
    status = request.args.get('status')
    return render_template(
        'submit_transaction.html',
        user=customer,
        error=error,
        status=status,
        form_data={},
        field_errors={}
    )

# ✅ Confirm Transaction via Email
@transactions_bp.route('/confirm/<int:txn_id>/<confirm>')
def confirm_fraud(txn_id, confirm):
    # Ensure the user is logged in
    customer_id = session.get('user_id')
    if not customer_id:
        flash("⚠️ Please log in to confirm your transaction.")
        return redirect(url_for('auth.login'))

    txn = Transaction.query.get_or_404(txn_id)

    if txn.customer_id != customer_id:
        flash("⚠️ You are not authorized to confirm this transaction.")
        return redirect(url_for('auth.dashboard'))

    if confirm == 'yes':
        txn.status = 'confirmed'
        flash('✅ Thanks for confirming. Transaction marked as safe.')
    else:
        txn.status = 'fraudulent'
        flash('🚨 Thanks for reporting. We’ve flagged this transaction.')

    db.session.commit()
    return redirect(url_for('auth.dashboard'))
