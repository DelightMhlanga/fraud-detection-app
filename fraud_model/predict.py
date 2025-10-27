import joblib
import pandas as pd
from datetime import datetime

# Load trained model
model = joblib.load('fraud_model/fraud_detector.pkl')

def predict_fraud(transaction):
    amount = transaction['amount']
    location = transaction['location']
    usual_location = transaction.get('usual_location')
    device_info = transaction['device_info']
    usual_device = transaction.get('usual_device')

    # Rule 1: Large amount
    if amount > 50:
        return 1

    # Rule 2: Location mismatch
    if location != usual_location:
        return 1

    # Rule 3: Device mismatch
    if device_info != usual_device:
        return 1

    # Rule 4: Odd hours (e.g., 1am–5am)
    hour = transaction['timestamp'].hour
    if hour < 5:
        return 1

    return 0  # Approved