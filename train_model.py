import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Load dataset          
df = pd.read_csv('./datasets/patient/marikina_patients_ml.csv')

# Select features and target, create a copy to avoid SettingWithCopyWarning
X = df[['latitude', 'longitude', 'severity', 'condition', 'distance_to_hospital_km', 'response_time_min']].copy()
y = df['hospital_id']

# Encode categorical variables
le_severity = LabelEncoder()
le_condition = LabelEncoder()
X['severity'] = le_severity.fit_transform(X['severity'])
X['condition'] = le_condition.fit_transform(X['condition'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=1))

# Print feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)

# Save model and encoders
with open('./models/hospital_prediction_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('./models/le_severity.pkl', 'wb') as f:
    pickle.dump(le_severity, f)
with open('./models/le_condition.pkl', 'wb') as f:
    pickle.dump(le_condition, f)

print("Model training complete. Saved as hospital_prediction_model.pkl")