import folium
from folium.features import CustomIcon
import webbrowser
import os
import sys

def visualize_ems_route(ems_base, patient_location, hospital_location, hospital_name):
    """
    Create an interactive map visualization of the EMS route
    
    Args:
        ems_base: [lat, lon] coordinates of EMS base
        patient_location: [lat, lon] coordinates of patient
        hospital_location: [lat, lon] coordinates of hospital
        hospital_name: Name of the hospital
    """
    # Create map centered between the three points
    all_points = [ems_base, patient_location, hospital_location]
    avg_lat = sum(p[0] for p in all_points) / len(all_points)
    avg_lon = sum(p[1] for p in all_points) / len(all_points)
    
    # Create the map
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14, tiles="OpenStreetMap")
    
    # Add markers for each location
    # EMS Base marker
    folium.Marker(
        location=ems_base,
        popup="EMS Base (Marikina Rescue 161)",
        icon=folium.Icon(color="red", icon="ambulance", prefix="fa"),
    ).add_to(m)
    
    # Patient marker
    folium.Marker(
        location=patient_location,
        popup="Patient Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)
    
    # Hospital marker
    folium.Marker(
        location=hospital_location,
        popup=f"Hospital: {hospital_name}",
        icon=folium.Icon(color="green", icon="hospital", prefix="fa"),
    ).add_to(m)
    
    # Add lines representing routes
    # EMS to Patient route
    folium.PolyLine(
        locations=[ems_base, patient_location],
        color="red",
        weight=4,
        opacity=0.8,
        popup="EMS to Patient: 7.11 minutes",
    ).add_to(m)
    
    # Patient to Hospital route
    folium.PolyLine(
        locations=[patient_location, hospital_location],
        color="blue",
        weight=4,
        opacity=0.8,
        popup="Patient to Hospital: 5.47 minutes",
    ).add_to(m)
    
    # Add circle areas to show approximate coverage
    folium.Circle(
        location=ems_base,
        radius=3000,  # 3 km radius
        color="red",
        fill=True,
        fill_opacity=0.1,
        popup="EMS 3km Response Zone",
    ).add_to(m)
    
    # Save the map
    map_file = "ems_route.html"
    m.save(map_file)
    
    # Open the map in a web browser
    webbrowser.open('file://' + os.path.realpath(map_file))

if __name__ == "__main__":
    # Use the coordinates from your example
    ems_base = [14.6628689, 121.1214235]
    patient_location = [14.6380867, 121.1280829]
    
    # Get hospital location from hospital ID 9 (Marikina Valley Medical Center)
    # You should load this from your hospital dataset, but I'm using fixed coordinates for this example
    hospital_location = [14.6319118, 121.1066519]  # Replace with actual coordinates of Marikina Valley Medical Center
    hospital_name = "Marikina Valley Medical Center"
    
    visualize_ems_route(ems_base, patient_location, hospital_location, hospital_name)