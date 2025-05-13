import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

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

# Load hospital dataset
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
hospitals['location'] = hospitals[['Latitude', 'Longtitude']].values.tolist()
hospitals = hospitals.rename(columns={'ID': 'id', 'Level': 'level', 'Has ER': 'has_er'})
hospitals = hospitals[['id', 'Name', 'Address', 'level', 'location', 'has_er']].to_dict('records')

# Load EMS dataset
ems = pd.read_csv('./datasets/ems/marikina_ems.csv')
ems['base_location'] = ems[['base_latitude', 'base_longitude']].values.tolist()
ems['last_available_time'] = pd.to_datetime(ems['last_available_time'])
ems = ems.to_dict('records')

# Parameters
NUM_PATIENTS = 1000
MARIKINA_BBOX = {'lat_min': 14.60, 'lat_max': 14.68, 'lon_min': 121.07, 'lon_max': 121.13}
SEVERITY_WEIGHTS = {'low': 0.5, 'medium': 0.3, 'high': 0.2}
CONDITIONS = {
    'low': ['Minor injury', 'Fever', 'Laceration'],
    'medium': ['Fracture', 'Moderate respiratory distress', 'Abdominal pain'],
    'high': ['Heart attack', 'Major trauma', 'Stroke']
}
START_TIME = datetime(2025, 5, 13, 8, 0, 0)
AVERAGE_SPEED = 30  # km/h

# Generate patient data with EMS simulation
np.random.seed(42)
patients = []
current_time = START_TIME
for i in range(NUM_PATIENTS):
    # Generate random patient location within Marikina
    lat = np.random.uniform(MARIKINA_BBOX['lat_min'], MARIKINA_BBOX['lat_max'])
    lon = np.random.uniform(MARIKINA_BBOX['lon_min'], MARIKINA_BBOX['lon_max'])
    patient_location = [lat, lon]
    
    # Assign severity and condition
    severity = np.random.choice(['low', 'medium', 'high'], p=[SEVERITY_WEIGHTS['low'], SEVERITY_WEIGHTS['medium'], SEVERITY_WEIGHTS['high']])
    condition = np.random.choice(CONDITIONS[severity])
    
    # Simulate call time
    time_offset = timedelta(minutes=np.random.randint(5, 15))
    call_time = current_time + time_offset
    
    # Find available ambulance
    available_ems = [unit for unit in ems if unit['status'] == 'Available' and unit['type'] == 'Ambulance' 
                     and unit['last_available_time'] <= call_time]
    if not available_ems:
        next_available = min([unit['last_available_time'] for unit in ems if unit['type'] == 'Ambulance'])
        call_time = max(call_time, next_available)
        available_ems = [unit for unit in ems if unit['status'] == 'Available' and unit['type'] == 'Ambulance']
    
    ems_unit = available_ems[0] if available_ems else ems[0]
    ems_unit['status'] = 'Dispatched'
    
    # Calculate response time to patient
    distance_to_patient = haversine_distance(ems_unit['base_location'], patient_location)
    time_to_patient = (distance_to_patient / AVERAGE_SPEED) * 60
    
    # Select hospital
    min_level = {'low': 1, 'medium': 3, 'high': 3}[severity]
    available_hospitals = [h for h in hospitals if h['level'] >= min_level]
    if available_hospitals:
        if severity == 'low':
            # Prefer Level 1 hospitals for low severity (70% chance)
            level_1_hospitals = [h for h in available_hospitals if h['level'] == 1]
            if level_1_hospitals and np.random.random() < 0.7:
                distances = [(h, haversine_distance(patient_location, h['location'])) for h in level_1_hospitals]
            else:
                distances = [(h, haversine_distance(patient_location, h['location'])) for h in available_hospitals]
        else:
            distances = [(h, haversine_distance(patient_location, h['location'])) for h in available_hospitals]
        hospital, distance_to_hospital = min(distances, key=lambda x: x[1])
        hospital_id = hospital['id']
        time_to_hospital = (distance_to_hospital / AVERAGE_SPEED) * 60
    else:
        hospital_id = None
        distance_to_hospital = None
        time_to_hospital = 0
    
    # Calculate total response time
    response_time = time_to_patient + time_to_hospital
    
    # Update EMS status
    ems_unit['status'] = 'Available'
    ems_unit['last_available_time'] = call_time + timedelta(minutes=response_time)
    
    # Store patient data
    patients.append({
        'patient_id': i + 1,
        'latitude': lat,
        'longitude': lon,
        'severity': severity,
        'condition': condition,
        'Call_Time': call_time.strftime('%Y-%m-%d %H:%M:%S'),
        'hospital_id': hospital_id,
        'distance_to_hospital_km': distance_to_hospital,
        'response_time_min': response_time
    })
    
    current_time = call_time

# Create DataFrame and save
patients_df = pd.DataFrame(patients)
patients_df = patients_df[['patient_id', 'latitude', 'longitude', 'severity', 'condition', 'Call_Time', 
                          'hospital_id', 'distance_to_hospital_km', 'response_time_min']]
patients_df.to_csv('marikina_patients_ml.csv', index=False)
print("Patient Dataset for ML (first 10 rows):")
print(patients_df.head(10).to_string(index=False))