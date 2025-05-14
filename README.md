<!-- @format -->

# Emergency Medical Services (EMS) System

This system predicts the optimal hospital for emergency patients based on location, severity, and medical condition, while calculating accurate response times considering actual road networks.

How to Use

1. Install the required libraries `pip install pandas numpy scikit-learn folium requests`
2. Setup the data
      - Run marikina_ems.py to initialize hospital data
      - Run generate_patient_ml.py to generate training dataset
      - Run train_model.py to train the hospital prediction model
3. Get an OpenRouteService API key (You can use my exposed API Key)
      - Sign up at OpenRouteService
      - Add your API key to predict_hospital.py (around line 64)
4. Run the prediction system `python predict_hospital.py`
5. Enter patient details when prompted
      - Use Google Maps to get accurate latitude/longitude coordinates
      - Select severity level (low, medium, high)
      - Choose the appropriate medical condition
6. Review the prediction results
      - The system will show the recommended hospital with distance and timing
      - Response time includes dispatch, travel, on-scene, and handover times
      - You can visualize the route on an interactive map

``
$ python predict_hospital.py
Enter patient details for hospital prediction:
Latitude (14.60 to 14.68): 14.665509
Longitude (121.07 to 121.13): 121.128510
Severity (low, medium, high): high
Condition (Minor injury, Fever, Laceration, Fracture, Moderate respiratory distress, Abdominal pain, Heart attack, Major trauma, Stroke): Stroke

Calculating route information...

Predicted hospital ID: 9
Predicted hospital: Marikina Valley Medical Center
Hospital Level: 3
Estimated distance to hospital: 4.05 km

Response Time Breakdown:
• Dispatch time: 2.00 minutes
• Travel to patient: 1.17 minutes
• On-scene time: 10.00 minutes
• Transport to hospital: 5.51 minutes
• Hospital handover: 5.00 minutes
• Total response time: 23.68 minutes

Routing Information:
✓ Using real road network distances and times with OpenRouteService API
EMS base to patient: 1.17 minutes
Patient to hospital: 5.51 minutes
``
