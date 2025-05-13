import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Load datasets
patients = pd.read_csv('marikina_patients_ml.csv')
hospitals = pd.read_csv('./datasets/hospital/hospital_dataset (cleaned).csv')
ems = pd.read_csv('./datasets/ems/marikina_ems.csv')

# Create map centered on Marikina City
marikina_center = [14.64, 121.10]  # Approximate center of Marikina
m = folium.Map(location=marikina_center, zoom_start=13, tiles='OpenStreetMap')

# Add patient locations (blue markers with clustering)
marker_cluster = MarkerCluster().add_to(m)
for _, row in patients.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"Patient {row['patient_id']}: {row['severity']}, {row['condition']}"
    ).add_to(marker_cluster)

# Add hospital locations (red markers)
for _, row in hospitals.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longtitude']],
        popup=f"Hospital {row['ID']}: {row['Name']} (Level {row['Level']})",
        icon=folium.Icon(color='red', icon='hospital', prefix='fa')
    ).add_to(m)

# Add EMS base location (green marker)
ems_base = ems.iloc[0]
folium.Marker(
    location=[ems_base['base_latitude'], ems_base['base_longitude']],
    popup='Marikina Rescue 161 Base',
    icon=folium.Icon(color='green', icon='ambulance', prefix='fa')
).add_to(m)

# Save and display map
m.save('map_marikina_patients_ml.html')
print("Map saved as marikina_map.html. Open in a browser to view.")