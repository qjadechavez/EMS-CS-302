import pandas as pd
import pickle
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import requests
import time
import folium
import webbrowser
import os

# Haversine distance function (keep for fallback)
def haversine_distance(coord1, coord2):
    """Calculate the great-circle distance between two points on Earth in km."""
    R = 6371  # Earth's radius in km
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
            print(f"Response details: {response.text}")  # Add this line to see the detailed error
            return None, None
    except Exception as e:
        print(f"Error getting route information: {e}")
        return None, None

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
# Add your API key here (sign up at https://openrouteservice.org/dev/#/signup)
ORS_API_KEY = "5b3ce3597851110001cf6248e9e7bf352181406b956089df63e2bb75"  # Replace with your actual API key

# Valid severity and condition values
VALID_SEVERITIES = ['low', 'medium', 'high']
VALID_CONDITIONS = [
    'Minor injury', 'Fever', 'Laceration',  # Low
    'Fracture', 'Moderate respiratory distress', 'Abdominal pain',  # Medium
    'Heart attack', 'Major trauma', 'Stroke'  # High
]

MARIKINA_BBOX = {
    'lat_min': 14.60,
    'lat_max': 14.68,
    'lon_min': 121.07,
    'lon_max': 121.13
}

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

# Add this code to show hospital level
hospital_level = "Unknown"  # Default value
if 'Level' in hospitals.columns:
    hospital_level = hospitals[hospitals['ID'] == predicted_hospital_id]['Level'].iloc[0]

print(f"Predicted hospital: {hospital_name}")
print(f"Hospital Level: {hospital_level}")
print(f"Estimated distance to hospital: {distance_to_hospital_km:.2f} km")
print(f"Estimated response time: {response_time_min:.2f} minutes")

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

def visualize_results(ems_base, patient_location, hospital_id, hospital_name):
    """
    Create a visualization of the EMS route simulation with actual road networks
    """
    # Get hospital coordinates
    hospital_coords = hospitals[hospitals['ID'] == hospital_id]['location'].iloc[0]
    
    # Create map centered between the three points
    all_points = [ems_base, patient_location, hospital_coords]
    avg_lat = sum(p[0] for p in all_points) / len(all_points)
    avg_lon = sum(p[1] for p in all_points) / len(all_points)
    
    # Create the map
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14, tiles="OpenStreetMap")
    
    # Add markers
    folium.Marker(
        location=ems_base,
        popup="EMS Base (Marikina Rescue 161)",
        icon=folium.Icon(color="red", icon="ambulance", prefix="fa"),
    ).add_to(m)
    
    folium.Marker(
        location=patient_location,
        popup="Patient Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)
    
    # Get hospital level
    hospital_level = "Unknown"
    if 'Level' in hospitals.columns:
        hospital_level = hospitals[hospitals['ID'] == hospital_id]['Level'].iloc[0]

    folium.Marker(
        location=hospital_coords,
        popup=f"Hospital: {hospital_name}<br>Level: {hospital_level}",
        icon=folium.Icon(color="green", icon="hospital", prefix="fa"),
    ).add_to(m)
    
    # Get route geometries from OpenRouteService
    def get_route_geometry(start, end):
        """Get the detailed route geometry between two points"""
        base_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
        
        # Format coordinates for ORS API (lon,lat format)
        coordinates = [[start[1], start[0]], [end[1], end[0]]]
        
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "coordinates": coordinates
        }
        
        try:
            response = requests.post(base_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error getting route geometry: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting route geometry: {e}")
            return None
    
    # Try to get EMS to Patient route
    ems_to_patient_route = get_route_geometry(ems_base, patient_location)
    if ems_to_patient_route:
        # Add the GeoJSON to the map
        folium.GeoJson(
            ems_to_patient_route,
            name="EMS to Patient",
            style_function=lambda x: {
                "color": "red",
                "weight": 4,
                "opacity": 0.8
            },
            tooltip=f"EMS to Patient: {time_to_patient:.2f} minutes"
        ).add_to(m)
    else:
        # Fallback to straight line
        folium.PolyLine(
            locations=[ems_base, patient_location],
            color="red",
            weight=4,
            opacity=0.8,
            popup=f"EMS to Patient: {time_to_patient:.2f} minutes (straight line)",
        ).add_to(m)
    
    # Try to get Patient to Hospital route
    patient_to_hospital_route = get_route_geometry(patient_location, hospital_coords)
    if patient_to_hospital_route:
        # Add the GeoJSON to the map
        folium.GeoJson(
            patient_to_hospital_route,
            name="Patient to Hospital",
            style_function=lambda x: {
                "color": "blue",
                "weight": 4,
                "opacity": 0.8
            },
            tooltip=f"Patient to Hospital: {time_to_hospital:.2f} minutes"
        ).add_to(m)
    else:
        # Fallback to straight line
        folium.PolyLine(
            locations=[patient_location, hospital_coords],
            color="blue",
            weight=4,
            opacity=0.8,
            popup=f"Patient to Hospital: {time_to_hospital:.2f} minutes (straight line)",
        ).add_to(m)
    
    # Save the map
    map_file = "ems_route.html"
    m.save(map_file)
    
    # Open the map in a web browser
    print(f"\nOpening visualization in web browser...")
    webbrowser.open('file://' + os.path.realpath(map_file))

# Ask user if they want to visualize the results
while True:
    visualize = input("\nDo you want to visualize the route? (y/n): ").lower()
    if visualize in ['y', 'n']:
        break
    print("Please enter 'y' or 'n'.")

if visualize == 'y':
    try:
        import folium
        visualize_results(EMS_BASE, patient_location, predicted_hospital_id, hospital_name)
    except ImportError:
        print("\nError: Folium package not installed. Install it using:")
        print("pip install folium")
        print("\nThen run the program again.")
