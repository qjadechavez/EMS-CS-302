<!-- @format -->

# EMS

How to use?

1. Install the required import libraries
2. Run `marikina_ems.py`, `generate_patient_ml.py`. This will create the following updated csv file for training dataset.
3. Run `train_model.py`. This will train the `marikina_patients_ml.csv` dataset for model training.
4. Finally, run `predict_hospital.py`. Use google maps to acquire latitude and longtitude

Example:

decha@ASUS_X415e MINGW64 /d/Documents/Python/EMS (main)
$ D:/Python/Python313/python.exe d:/Documents/Python/EMS/predict_hospital.py
Enter patient details for hospital prediction:
Latitude (14.60 to 14.68): 14.6380867
Longitude (121.07 to 121.13): 121.1280829
Severity (low, medium, high): high
Condition (Minor injury, Fever, Laceration, Fracture, Moderate respiratory distress, Abdominal pain, Heart attack, Major trauma, Stroke): Stroke

Calculating route information...
API error: 400
Road routing failed for hospital 1, using straight-line distance.
API error: 400
Road routing failed for hospital 2, using straight-line distance.
API error: 400
Road routing failed for hospital 3, using straight-line distance.
API error: 400
Road routing failed for hospital 4, using straight-line distance.
API error: 400
Road routing failed for hospital 5, using straight-line distance.
API error: 400
Road routing failed for hospital 6, using straight-line distance.
API error: 400
Road routing failed for hospital 7, using straight-line distance.
API error: 400
Road routing failed for hospital 8, using straight-line distance.
API error: 400
Road routing failed for hospital 9, using straight-line distance.
API error: 400
Road routing failed for hospital 10, using straight-line distance.
API error: 400

Predicted hospital ID: 9
Predicted hospital: Marikina Valley Medical Center
Estimated distance to hospital: 1.94 km
Estimated response time: 9.57 minutes

Routing Information:
✓ Using real road network distances and times
⚠ API fallback used: calculations are based on straight-line approximation
EMS base to patient: 5.69 minutes
Patient to hospital: 3.88 minutes
