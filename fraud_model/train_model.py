import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Load your enriched dataset
df = pd.read_csv('fraud_model/fraud_dataset.csv')

# Check for missing values
df = df.dropna()

# Define features and label
features = ['amount', 'hour_of_day', 'day_of_week', 'device_consistency', 'location_deviation']
X = df[features]
y = df['label']

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("✅ Classification Report:")
print(classification_report(y_test, y_pred))
print("✅ Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the model
joblib.dump(model, 'fraud_model/fraud_detector.pkl')
print("✅ Model retrained and saved.")