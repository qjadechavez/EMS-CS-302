import pandas as pd
import pickle
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Haversine distance function
def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on Earth in km."""
    R = 6371  # Earth's radius in km
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Load model and encoders
with open('hospital_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('le_severity.pkl', 'rb') as f:
    le_severity = pickle.load(f)
with open('le_condition.pkl', 'rb') as f:
    le_condition = pickle.load(f)

# Load hospital dataset for distance calculations
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
hospitals['location'] = hospitals[['Latitude', 'Longtitude']].values.tolist()

# EMS base location (Marikina Rescue 161)
EMS_BASE = [14.6628689, 121.1214235]
AVERAGE_SPEED = 30  # km/h

# Valid severity and condition values
VALID_SEVERITIES = ['low', 'medium', 'high']
VALID_CONDITIONS = [
    'Minor injury', 'Fever', 'Laceration',  # Low
    'Fracture', 'Moderate respiratory distress', 'Abdominal pain',  # Medium
    'Heart attack', 'Major trauma', 'Stroke'  # High
]
MARIKINA_BBOX = {'lat_min': 14.60, 'lat_max': 14.68, 'lon_min': 121.07, 'lon_max': 121.13}

# Get user input
print("Enter patient details for hospital prediction:")
while True:
    try:
        latitude = float(input("Latitude (14.60 to 14.68): "))
        if not (MARIKINA_BBOX['lat_min'] <= latitude <= MARIKINA_BBOX['lat_max']):
            print(f"Error: Latitude must be between {MARIKINA_BBOX['lat_min']} and {MARIKINA_BBOX['lat_max']}.")
            continue
        break
    except ValueError:
        print("Error: Latitude must be a number.")

while True:
    try:
        longitude = float(input("Longitude (121.07 to 121.13): "))
        if not (MARIKINA_BBOX['lon_min'] <= longitude <= MARIKINA_BBOX['lon_max']):
            print(f"Error: Longitude must be between {MARIKINA_BBOX['lon_min']} and {MARIKINA_BBOX['lon_max']}.")
            continue
        break
    except ValueError:
        print("Error: Longitude must be a number.")

while True:
    severity = input(f"Severity ({', '.join(VALID_SEVERITIES)}): ").lower()
    if severity not in VALID_SEVERITIES:
        print(f"Error: Severity must be one of {', '.join(VALID_SEVERITIES)}.")
        continue
    break

while True:
    condition = input(f"Condition ({', '.join(VALID_CONDITIONS)}): ")
    if condition not in VALID_CONDITIONS:
        print(f"Error: Condition must be one of {', '.join(VALID_CONDITIONS)}.")
        continue
    break

# Calculate derived features
patient_location = [latitude, longitude]

# Estimate distance_to_hospital_km (use closest hospital as proxy)
distances = [haversine_distance(patient_location, h) for h in hospitals['location']]
distance_to_hospital_km = min(distances) if distances else 0.0

# Estimate response_time_min (EMS base to patient + patient to closest hospital)
distance_to_patient = haversine_distance(EMS_BASE, patient_location)
time_to_patient = (distance_to_patient / AVERAGE_SPEED) * 60
time_to_hospital = (distance_to_hospital_km / AVERAGE_SPEED) * 60
response_time_min = time_to_patient + time_to_hospital

# Create input DataFrame for model
new_patient = pd.DataFrame({
    'latitude': [latitude],
    'longitude': [longitude],
    'severity': [severity],
    'condition': [condition],
    'distance_to_hospital_km': [distance_to_hospital_km],
    'response_time_min': [response_time_min]
})

# Preprocess new data
new_patient['severity'] = le_severity.transform(new_patient['severity'])
new_patient['condition'] = le_condition.transform(new_patient['condition'])

# Predict hospital
predicted_hospital_id = model.predict(new_patient)[0]
print(f"\nPredicted hospital ID: {predicted_hospital_id}")

# Get hospital name
hospital_name = hospitals[hospitals['ID'] == predicted_hospital_id]['Name'].iloc[0]
print(f"Predicted hospital: {hospital_name}")
print(f"Estimated distance to hospital: {distance_to_hospital_km:.6f} km")
print(f"Estimated response time: {response_time_min:.6f} minutes")