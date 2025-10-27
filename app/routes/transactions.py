from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Transaction, Customer
from app import db
from datetime import datetime
from app.utils.email_service import send_email  # ✅ Email helper
from fraud_model import predict  # ✅ Import your model predictor


transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/submit', methods=['GET', 'POST'])
def submit_transaction():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', error='login_required'))

    customer_id = session['user_id']
    customer = Customer.query.get(customer_id)

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount < 1:
                return redirect(url_for('transactions.submit_transaction', error='amount'))
        except ValueError:
            return redirect(url_for('transactions.submit_transaction', error='invalid_format'))

        device_info = request.form['device_info']
        location = request.form['location']

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
            send_email(customer.email, subject, body)

        return redirect(url_for('transactions.submit_transaction', status=status))

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
# Confirmation route for email links
@transactions_bp.route('/confirm/<int:txn_id>/<confirm>')
def confirm_fraud(txn_id, confirm):
    txn = Transaction.query.get_or_404(txn_id)

    if confirm == 'yes':
        txn.status = 'confirmed'
        flash('Thanks for confirming. Transaction marked as safe.')
    else:
        txn.status = 'fraudulent'
        flash('Thanks for reporting. We’ve flagged this transaction.')

    db.session.commit()
    return redirect(url_for('transactions.submit_transaction'))