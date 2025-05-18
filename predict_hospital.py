import pandas as pd
import pickle
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import requests
import time
import subprocess

# Haversine distance function (keep for fallback)
def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on Earth in km."""
    R = 6371 
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1  # Fix: changed from "dlon = dlon - lon1"
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Road network routing function using OpenRouteService
def get_route_info(start_coords, end_coords, api_key):
    """Get road distance and duration between two points using OpenRouteService API."""
    base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    
    # Format coordinates for ORS API (lon,lat format)
    coordinates = [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]]
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "coordinates": coordinates
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()
            # Extract distance (in meters) and duration (in seconds)
            distance_km = data['routes'][0]['summary']['distance'] / 1000
            duration_min = data['routes'][0]['summary']['duration'] / 60
            return distance_km, duration_min
        else:
            print(f"API error: {response.status_code}")
            print(f"Response details: {response.text}")
            return None, None
    except Exception as e:
        print(f"Error getting route information: {e}")
        return None, None

# Load model and encoders
with open('./models/hospital_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('./models/le_severity.pkl', 'rb') as f:
    le_severity = pickle.load(f)

with open('./models/le_condition.pkl', 'rb') as f:
    le_condition = pickle.load(f)

# Load hospital dataset for distance calculations
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
hospitals['location'] = hospitals[['Latitude', 'Longtitude']].values.tolist()

# EMS base location (Marikina Rescue 161)
EMS_BASE = [14.6628689, 121.1214235]
AVERAGE_SPEED = 30

ORS_API_KEY = "5b3ce3597851110001cf6248e9e7bf352181406b956089df63e2bb75" 

# Valid severity and condition values
VALID_SEVERITIES = ['low', 'medium', 'high']
VALID_CONDITIONS = [
    'Minor injury', 'Fever', 'Laceration', 
    'Fracture', 'Moderate respiratory distress', 'Abdominal pain',  
    'Heart attack', 'Major trauma', 'Stroke'  
]

MARIKINA_BBOX = {
    'lat_min': 14.60,
    'lat_max': 14.68,
    'lon_min': 121.07,
    'lon_max': 121.13
}

def main():
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

    # Check if using road network or straight-line distance
    use_road_network = True
    if ORS_API_KEY == "your_api_key_here":
        print("\nWarning: OpenRouteService API key not configured.")
        print("Using straight-line distance calculations instead of road network.")
        use_road_network = False

    # Calculate hospital distances and times
    hospital_info = []
    print("\nCalculating route information...")

    for idx, hospital in hospitals.iterrows():
        hospital_coords = hospital['location']
        hospital_id = hospital['ID']
        
        if use_road_network:
            # Using road network to calculate distance and time
            road_distance, road_duration = get_route_info(patient_location, hospital_coords, ORS_API_KEY)
            
            if road_distance is None:
                # Fallback to haversine if API fails
                print(f"Road routing failed for hospital {hospital_id}, using straight-line distance.")
                haversine_dist = haversine_distance(patient_location, hospital_coords)
                time_estimate = (haversine_dist / AVERAGE_SPEED) * 60
                hospital_info.append((hospital_id, haversine_dist, time_estimate, True))
            else:
                hospital_info.append((hospital_id, road_distance, road_duration, False))
            
            # Sleep to avoid rate limiting if many hospitals
            time.sleep(0.1)
        else:
            # Using straight-line distance
            haversine_dist = haversine_distance(patient_location, hospital_coords)
            time_estimate = (haversine_dist / AVERAGE_SPEED) * 60
            hospital_info.append((hospital_id, haversine_dist, time_estimate, True))

    # Find closest hospital for distance calculation
    closest_hospital = min(hospital_info, key=lambda x: x[1])
    distance_to_hospital_km = closest_hospital[1]

    # Calculate response time using road network if available
    if use_road_network:
        # EMS base to patient
        road_dist_to_patient, road_time_to_patient = get_route_info(EMS_BASE, patient_location, ORS_API_KEY)
        if road_dist_to_patient is None:
            # Fallback to haversine
            distance_to_patient = haversine_distance(EMS_BASE, patient_location)
            time_to_patient = (distance_to_patient / AVERAGE_SPEED) * 60
        else:
            time_to_patient = road_time_to_patient
        
        # Patient to hospital
        time_to_hospital = closest_hospital[2]
    else:
        # Using straight-line distance
        distance_to_patient = haversine_distance(EMS_BASE, patient_location)
        time_to_patient = (distance_to_patient / AVERAGE_SPEED) * 60
        time_to_hospital = closest_hospital[2]

    # Add dispatch time and on-scene time
    dispatch_time = 2 
    on_scene_time = 10  
    handover_time = 5  

    # Total response time calculation
    response_time_min = dispatch_time + time_to_patient + on_scene_time + time_to_hospital + handover_time

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

    # Add this code to show hospital level
    hospital_level = "Unknown"  # Default value
    if 'Level' in hospitals.columns:
        hospital_level = hospitals[hospitals['ID'] == predicted_hospital_id]['Level'].iloc[0]

    print(f"Predicted hospital: {hospital_name}")
    print(f"Hospital Level: {hospital_level}")
    print(f"Estimated distance to hospital: {distance_to_hospital_km:.2f} km")

    # Detailed response time breakdown
    print("\nResponse Time Breakdown:")
    print(f"• Dispatch time: {dispatch_time:.2f} minutes")
    print(f"• Travel to patient: {time_to_patient:.2f} minutes")
    print(f"• On-scene time: {on_scene_time:.2f} minutes")
    print(f"• Transport to hospital: {time_to_hospital:.2f} minutes")
    print(f"• Hospital handover: {handover_time:.2f} minutes")
    print(f"• Total response time: {response_time_min:.2f} minutes")

    # Add extra information about the routing method used
    if use_road_network:
        print("\nRouting Information:")
        print("✓ Using real road network distances and times with OpenRouteService API")
        
        is_fallback = next((info[3] for info in hospital_info if info[0] == predicted_hospital_id), False)
        if is_fallback:
            print("⚠ API fallback used: calculations are based on straight-line approximation")
        
        print(f"EMS base to patient: {time_to_patient:.2f} minutes")
        print(f"Patient to hospital: {time_to_hospital:.2f} minutes")
    else:
        print("\nRouting Information:")
        print("⚠ Using straight-line distance approximations")
        print("  To use real road network, configure an OpenRouteService API key")

    # Ask user if they want to visualize the results
    while True:
        visualize = input("\nDo you want to visualize the route? (y/n): ").lower()
        if visualize in ['y', 'n']:
            break
        print("Please enter 'y' or 'n'.")

    if visualize == 'y':
        try:
            # Get hospital coordinates
            hospital_coords = hospitals[hospitals['ID'] == predicted_hospital_id]['location'].iloc[0]
            
            # Write the route data to a temporary file for the visualization script
            route_data = {
                'ems_base': [float(coord) for coord in EMS_BASE],
                'patient_location': [float(coord) for coord in patient_location],
                'hospital_coords': [float(coord) for coord in hospital_coords],
                'hospital_name': hospital_name,
                'hospital_level': str(hospital_level),  # Convert to string to ensure serialization
                'time_to_patient': float(time_to_patient),
                'time_to_hospital': float(time_to_hospital),
                'dispatch_time': float(dispatch_time),
                'on_scene_time': float(on_scene_time),
                'api_key': ORS_API_KEY
            }
            
            # Save route data to a temporary file
            import json
            try:
                with open('temp_route_data.json', 'w') as f:
                    json.dump(route_data, f)
                
                # Call the visualization script
                print("\nOpening visualization in web browser...")
                subprocess.run(["python", "./utilities/visualize_route.py"])
                
            except TypeError as e:
                print(f"\nError serializing data: {e}")
                # Print problematic values to help debugging
                print("Data types:")
                for key, value in route_data.items():
                    print(f"{key}: {type(value)}")
            
        except Exception as e:
            print(f"\nError visualizing route: {e}")
            print("Make sure visualize_route.py is in the same directory.")

if __name__ == "__main__":
    main()
