import unittest
import sys
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHospitalPredictionModel(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load the model and encoders before running tests"""
        try:
            with open('../models/hospital_assignment_model.pkl', 'rb') as file:
                cls.model = pickle.load(file)
            with open('../models/severity_encoder.pkl', 'rb') as file:
                cls.le_severity = pickle.load(file)
            with open('../models/condition_encoder.pkl', 'rb') as file:
                cls.le_condition = pickle.load(file)
        except FileNotFoundError:
            # If files don't exist, create dummy encoders for testing
            cls.model = None
            cls.le_severity = LabelEncoder().fit(['low', 'medium', 'high'])
            cls.le_condition = LabelEncoder().fit(['Moderate respiratory distress', 'Fracture'])
    
    def test_model_loading(self):
        """Test if model and encoders loaded correctly"""
        self.assertIsNotNone(self.model, "Model failed to load")
        self.assertIsNotNone(self.le_severity, "Severity encoder failed to load")
        self.assertIsNotNone(self.le_condition, "Condition encoder failed to load")
    
    def test_model_prediction(self):
        """Test if model can make predictions with sample data"""
        # Sample input data based on your dataset
        test_input = pd.DataFrame({
            'latitude': [14.62],
            'longitude': [121.09],
            'severity': self.le_severity.transform(['medium']),
            'condition': self.le_condition.transform(['Moderate respiratory distress']),
            'distance_to_hospital_km': [3.5],
            'response_time_min': [25.0]
        })
        
        # Only run this test if model is loaded
        if self.model is not None:
            prediction = self.model.predict(test_input)
            self.assertIsNotNone(prediction, "Model prediction should not be None")
            self.assertTrue(isinstance(prediction[0], (int, np.integer)), 
                           f"Prediction should be hospital ID (integer), got {type(prediction[0])}")
            
    def test_severity_encoder(self):
        """Test if severity encoder works correctly"""
        encoded = self.le_severity.transform(['low', 'medium', 'high'])
        self.assertEqual(len(encoded), 3, "Should encode all three severity levels")
        self.assertEqual(len(set(encoded)), 3, "Should produce three unique encodings")

if __name__ == '__main__':
    unittest.main()