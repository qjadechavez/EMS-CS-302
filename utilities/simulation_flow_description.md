
# EMS Route Optimization and Hospital Selection System: Simulation Flow

## 1. Data Setup Phase
- **Hospital Data**: Initialized from known locations in Marikina with fallback to OpenStreetMap data
- **Patient Data**: Generated with various medical conditions and severity levels
- **EMS Base Data**: Multiple ambulance bases across Marikina with geographic coordinates

## 2. Machine Learning Model Training
- **Dataset Creation**: Combines patient and hospital data with calculated distances
- **Random Forest Model**: Trained to predict the optimal hospital based on:
  - Patient location (latitude/longitude)
  - Medical condition and severity
  - Travel distances and times
- **Model Evaluation**: Tested for accuracy and cross-validated

## 3. Simulation Execution
- **Patient Input**: User provides location, severity, and condition
- **EMS Base Selection**: Finds the closest available ambulance
- **Route Calculation**: Uses OpenRouteService API to calculate:
  - EMS base to patient route
  - Patient to hospital route
- **Hospital Selection**: Uses the ML model to recommend the most appropriate hospital
- **Response Time Calculation**: Breaks down the full emergency response timeline
  - Dispatch time (2 min)
  - Travel to patient time (variable)
  - On-scene care time (10 min)
  - Transport to hospital time (variable)
  - Hospital handover time (5 min)

## 4. Visualization
- **Map Generation**: Creates an interactive HTML map using Folium
- **Route Display**: Shows the full emergency route with:
  - EMS base marker (red)
  - Patient location marker (blue)
  - Hospital marker (green)
  - Route lines with time information
- **Information Panel**: Displays all timing and emergency details

## 5. Data Flow Between Components
- temp_route_data.json: Transfers route information between prediction and visualization
- marikina_hospitals.csv: Stores hospital location and level data
- hospital_prediction_model.pkl: Saved machine learning model for hospital predictions
