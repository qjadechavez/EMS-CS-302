import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.inspection import permutation_importance
import pickle
import os

# Create models directory if it doesn't exist
os.makedirs('./models', exist_ok=True)
os.makedirs('./plots', exist_ok=True)

# Set plot style
plt.style.use('ggplot')
sns.set_palette("viridis")

# Load dataset          
print("Loading dataset...")
df = pd.read_csv('./datasets/patient/marikina_patients_ml.csv')

# Exploratory Data Analysis with Plots
print("Generating EDA plots...")

# Plot 1: Distribution of severity levels
plt.figure(figsize=(10, 6))
severity_counts = df['severity'].value_counts()
ax = severity_counts.plot(kind='bar', color=sns.color_palette("viridis"))
plt.title('Distribution of Patient Severity Levels')
plt.xlabel('Severity')
plt.ylabel('Count')
plt.xticks(rotation=0)
for i, v in enumerate(severity_counts):
    ax.text(i, v + 5, str(v), ha='center')
plt.tight_layout()
plt.savefig('./plots/severity_distribution.png')

# Plot 2: Distribution of hospital assignments
plt.figure(figsize=(12, 7))
hospital_counts = df['hospital_id'].value_counts().sort_index()
ax = sns.barplot(x=hospital_counts.index, y=hospital_counts.values)
plt.title('Distribution of Hospital Assignments')
plt.xlabel('Hospital ID')
plt.ylabel('Number of Patients')
for i, v in enumerate(hospital_counts.values):
    ax.text(i, v + 5, str(v), ha='center')
plt.tight_layout()
plt.savefig('./plots/hospital_distribution.png')

# Plot 3: Geographic distribution of patients with hospital assignments
plt.figure(figsize=(12, 10))
scatter = plt.scatter(df['longitude'], df['latitude'], 
                     c=df['hospital_id'], 
                     cmap='tab20', 
                     alpha=0.7,
                     s=50)
plt.colorbar(scatter, label='Hospital ID')
plt.title('Geographic Distribution of Patients and Hospital Assignments')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('./plots/geographic_distribution.png')

# Plot 4: Response time distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['response_time_min'], bins=20, kde=True)
plt.axvline(df['response_time_min'].mean(), color='red', linestyle='--', 
            label=f'Mean: {df["response_time_min"].mean():.2f} min')
plt.title('Distribution of EMS Response Times')
plt.xlabel('Response Time (minutes)')
plt.ylabel('Frequency')
plt.legend()
plt.tight_layout()
plt.savefig('./plots/response_time_distribution.png')

# Plot 5: Correlation heatmap for numeric features
plt.figure(figsize=(10, 8))
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation = df[numeric_cols].corr()
mask = np.triu(correlation)
sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", mask=mask, vmin=-1, vmax=1)
plt.title('Correlation Heatmap of Numeric Features')
plt.tight_layout()
plt.savefig('./plots/correlation_heatmap.png')

# Select features and target
print("Preparing data for modeling...")
X = df[['latitude', 'longitude', 'severity', 'condition', 'distance_to_hospital_km', 'response_time_min']].copy()
y = df['hospital_id']

# Encode categorical variables
le_severity = LabelEncoder()
le_condition = LabelEncoder()
X['severity'] = le_severity.fit_transform(X['severity'])
X['condition'] = le_condition.fit_transform(X['condition'])

# Plot 6: Condition distribution
plt.figure(figsize=(14, 8))
condition_counts = df['condition'].value_counts()
condition_counts_top = condition_counts.head(15)  # Top 15 conditions to keep plot readable
ax = condition_counts_top.plot(kind='barh', color=sns.color_palette("viridis", len(condition_counts_top)))
plt.title('Top 15 Patient Conditions')
plt.xlabel('Count')
plt.ylabel('Condition')
for i, v in enumerate(condition_counts_top):
    ax.text(v + 1, i, str(v), va='center')
plt.tight_layout()
plt.savefig('./plots/condition_distribution.png')

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
print("Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model with cross-validation
cv_scores = cross_val_score(model, X, y, cv=5)
print(f"Cross-validation scores: {cv_scores}")
print(f"Mean CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Evaluate model on test set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Test set accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=1))

# Calculate and plot confusion matrix
plt.figure(figsize=(12, 10))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=sorted(df['hospital_id'].unique()),
            yticklabels=sorted(df['hospital_id'].unique()))
plt.title('Confusion Matrix')
plt.xlabel('Predicted Hospital')
plt.ylabel('Actual Hospital')
plt.tight_layout()
plt.savefig('./plots/confusion_matrix.png')

# Plot feature importance
print("Generating feature importance plot...")
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=feature_importance, palette='viridis')
plt.title('Feature Importance')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('./plots/feature_importance.png')

# Calculate permutation importance (alternative measure of feature importance)
perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
sorted_idx = perm_importance.importances_mean.argsort()

plt.figure(figsize=(10, 6))
plt.boxplot(perm_importance.importances[sorted_idx].T,
            vert=False, labels=X.columns[sorted_idx])
plt.title('Permutation Importance (Test Set)')
plt.tight_layout()
plt.savefig('./plots/permutation_importance.png')

# Print feature importance
print("\nFeature Importance:")
print(feature_importance)

# Save model and encoders
print("Saving model and encoders...")
with open('./models/hospital_prediction_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('./models/le_severity.pkl', 'wb') as f:
    pickle.dump(le_severity, f)
with open('./models/le_condition.pkl', 'wb') as f:
    pickle.dump(le_condition, f)

print("Model training complete. Saved as hospital_prediction_model.pkl")
print("Plots saved in ./plots/ directory")

# Display one sample prediction
sample = X_test.iloc[0].values.reshape(1, -1)
sample_pred = model.predict(sample)
sample_proba = model.predict_proba(sample)

print("\nSample prediction demonstration:")
print(f"Predicted hospital: {sample_pred[0]}")

# Plot prediction probability for the sample
plt.figure(figsize=(12, 6))
hospitals = sorted(df['hospital_id'].unique())
probabilities = sample_proba[0]
sns.barplot(x=hospitals, y=probabilities)
plt.title('Prediction Probability for Sample Patient')
plt.xlabel('Hospital ID')
plt.ylabel('Probability')
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig('./plots/sample_prediction_probability.png')

print("All visualizations complete!")