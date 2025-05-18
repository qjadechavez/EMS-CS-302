<!-- @format -->

# EMS Route Optimization and Hospital Selection System

## Project Description

This Emergency Medical Services (EMS) Route Optimization and Hospital Selection System is a comprehensive healthcare simulation platform designed to predict the optimal hospital for emergency patients while calculating accurate response times using real-world road networks. The system integrates machine learning with geospatial routing to create a decision support tool for emergency medical services.

## Key Features

### 1. Machine Learning Hospital Selection

The system uses a trained machine learning model to recommend the most appropriate hospital based on:

- Patient location (latitude/longitude coordinates)
- Medical condition severity (low, medium, high)
- Specific medical condition (9 different emergency types)
- Expected travel times and distances

### 2. Real-Time Route Calculation

- Integrates with OpenRouteService API to calculate actual road network distances
- Automatically falls back to straight-line (haversine) calculations when needed
- Accounts for geographic obstacles, one-way streets, and road networks

### 3. Comprehensive Response Time Modeling

The system provides detailed time breakdowns reflecting real-world EMS operations:

- Dispatch time (initial call processing and crew mobilization)
- Travel time to patient location
- On-scene assessment and stabilization time
- Transport time to hospital
- Hospital handover time

### 4. Interactive Visualization

- Generates dynamic HTML maps showing the complete emergency route
- Displays EMS base, patient location, and selected hospital
- Shows actual road network paths with time estimates
- Includes tooltips with detailed timing information

### 5. Flexible Input System

- Accepts user-defined patient locations within a specified geographic area
- Validates input coordinates against municipal boundaries
- Allows selection from standardized medical conditions and severity levels

## Technologies Used

- **Python**: Core programming language
- **Pandas/NumPy**: Data handling and numerical computations
- **Scikit-learn**: Machine learning model training and prediction
- **Folium**: Interactive map visualization
- **OpenRouteService API**: Road network routing and travel time estimation
- **JSON**: Data transfer between program components

## Applications

This system has potential applications in:

- Emergency services planning and dispatch
- Hospital resource allocation
- EMS response time optimization
- Patient outcome improvement through faster, more appropriate hospital selection
- Training and education for emergency medical personnel
- Public health policy planning for emergency services coverage

## How to Use

1. **Install the required libraries**
      ```bash
      pip install pandas numpy scikit-learn folium requests
      ```
2. **Setup the data**
      - Run marikina_ems.py to initialize hospital data
      - Run generate_patient_ml.py to generate training dataset
      - Run train_model.py to train the hospital prediction model
3. **Get an OpenRouteService API key (You can use my exposed API Key)**
      - Sign up at OpenRouteService
      - Add your API key to predict_hospital.py (around line 64)
4. **Run the prediction system**
      ```bash
      python predict_hospital.py
      ```
5. **Enter patient details when prompted**
      - Use Google Maps to get accurate latitude/longitude coordinates
      - Select severity level (low, medium, high)
      - Choose the appropriate medical condition
6. **Review the prediction results**
      - The system will show the recommended hospital with distance and timing
      - Response time includes dispatch, travel, on-scene, and handover times
      - You can visualize the route on an interactive map

```
$ python predict_hospital.py
Enter patient details for hospital prediction:
Latitude (14.60 to 14.68): 14.646421
Longitude (121.07 to 121.13): 121.118834
Severity (low, medium, high): high
Condition (Minor injury, Fever, Laceration, Fracture, Moderate respiratory distress, Abdominal pain, Heart attack, Major trauma, Stroke): Stroke

Finding closest EMS base...

Selected EMS base: 169 Base - Pugad Lawin, Barangay Fortune
Distance to patient: 2.49 km
Estimated travel time: 3.73 minutes

Calculating route information...

Predicted hospital ID: 9
Predicted hospital: Marikina Valley Medical Center
Hospital Level: 3
Estimated distance to hospital: 1.24 km

Response Time Breakdown:
• Dispatch time: 2.00 minutes
• Travel to patient: 3.73 minutes
• On-scene time: 10.00 minutes
• Transport to hospital: 2.40 minutes
• Hospital handover: 5.00 minutes
• Total response time: 23.13 minutes

Routing Information:
✓ Using real road network distances and times with OpenRouteService API
EMS base to patient: 3.73 minutes
Patient to hospital: 2.40 minutes

Do you want to visualize the route? (y/n): y

Opening visualization in web browser...
```

teting
