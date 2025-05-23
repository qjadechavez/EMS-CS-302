import os
import sys
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEMSSystemE2E(unittest.TestCase):
    
    def setUp(self):
        """Load necessary data for testing"""
        try:
            # Load hospital data
            self.hospitals = pd.read_csv('../datasets/hospital/hospital_dataset (for review).csv')
            
            # Load sample patient data
            self.patients = pd.read_csv('../datasets/patient/marikina_patients_ml_full.csv', nrows=10)
            
            # Load EMS base data
            self.ems_bases = pd.read_csv('../datasets/ems/marikina_ems_generated.csv')
        except Exception as e:
            print(f"Error loading test data: {e}")
            raise
    
    def test_data_integrity(self):
        """Test that all required datasets are valid"""
        # Check hospital data
        self.assertGreater(len(self.hospitals), 0, "Hospital dataset should not be empty")
        self.assertIn('ID', self.hospitals.columns, "Hospital dataset should have ID column")
        
        # Check patient data
        self.assertGreater(len(self.patients), 0, "Patient dataset should not be empty")
        required_columns = ['patient_id', 'latitude', 'longitude', 'severity', 'condition', 
                           'hospital_id', 'response_time_min']
        for column in required_columns:
            self.assertIn(column, self.patients.columns, f"Patient dataset missing column: {column}")
        
        # Check EMS data
        self.assertGreater(len(self.ems_bases), 0, "EMS dataset should not be empty")
        self.assertIn('ems_id', self.ems_bases.columns, "EMS dataset should have ems_id column")
    
    def test_full_prediction_workflow(self):
        """Test the full prediction workflow with a sample patient"""
        # Skip test if model files not available
        if not os.path.exists('../models/hospital_assignment_model.pkl'):
            self.skipTest("Model files not available")
        
        # Load model and encoders
        with open('../models/hospital_assignment_model.pkl', 'rb') as file:
            model = pickle.load(file)
        with open('../models/severity_encoder.pkl', 'rb') as file:
            le_severity = pickle.load(file)
        with open('../models/condition_encoder.pkl', 'rb') as file:
            le_condition = pickle.load(file)
            
        # Get a sample patient
        patient = self.patients.iloc[0]
        
        # Prepare input for model
        input_data = pd.DataFrame({
            'latitude': [patient['latitude']],
            'longitude': [patient['longitude']],
            'severity': le_severity.transform([patient['severity']]),
            'condition': le_condition.transform([patient['condition']]),
            'distance_to_hospital_km': [3.0],  # Sample value
            'response_time_min': [25.0]  # Sample value
        })
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Verify prediction is a valid hospital ID
        self.assertIn(prediction, self.hospitals['ID'].values, 
                     f"Predicted hospital ID {prediction} not found in hospital dataset")

if __name__ == '__main__':
    unittest.main()