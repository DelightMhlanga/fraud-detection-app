from app import db
from app.models import Transaction, Customer
import pandas as pd

def load_transaction_data():
    transactions = Transaction.query.join(Customer).all()
    data = []
    for txn in transactions:
        data.append({
            'transaction_id': txn.id,
            'customer_id': txn.customer_id,
            'amount': txn.amount,
            'timestamp': txn.timestamp,
            'location': txn.location,
            'device_info': txn.device_info,
            'status': txn.status,
            'customer_name': txn.customer.name
        })
    return pd.DataFrame(data)

def label_fraud(df):
    df['label'] = df['status'].apply(lambda x: 1 if x == 'fraudulent' else 0)
    return df

def add_time_features(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    return df

def add_device_consistency(df):
    device_map = df.groupby('customer_id')['device_info'].agg(lambda x: x.mode()[0])
    df['device_consistency'] = df.apply(
        lambda row: 1 if row['device_info'] == device_map[row['customer_id']] else 0,
        axis=1
    )
    return df

def add_location_deviation(df):
    location_map = df.groupby('customer_id')['location'].agg(lambda x: x.mode()[0])
    df['location_deviation'] = df.apply(
        lambda row: 1 if row['location'] != location_map[row['customer_id']] else 0,
        axis=1
    )
    return df

print("✅ Starting data prep...")

df = load_transaction_data()
df = label_fraud(df)
df = add_time_features(df)
df = add_device_consistency(df)
df = add_location_deviation(df)

df.to_csv(r'C:\Users\dee\Fraud Detection System\fraud_model\fraud_dataset.csv', index=False)
print("✅ Saved to fraud_model/fraud_dataset.csv")