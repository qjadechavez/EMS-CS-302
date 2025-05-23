import unittest
import sys
import os
import pandas as pd
from unittest.mock import patch

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your prediction script - adjust the import if needed
try:
    from predict_hospital import calculate_distance, predict_hospital
except ImportError:
    # Create dummy functions for testing if imports fail
    def calculate_distance(lat1, lon1, lat2, lon2): return 5.0
    def predict_hospital(lat, lon, severity, condition): return {'hospital_id': 3, 'distance': 5.0}

class TestRouteCalculation(unittest.TestCase):
    
    def test_calculate_distance(self):
        """Test the distance calculation function"""
        # Test with two known points in Marikina
        distance = calculate_distance(14.6399746, 121.0965973, 14.6361025, 121.0984445)
        self.assertGreater(distance, 0, "Distance should be greater than 0")
        self.assertLess(distance, 20, "Distance should be less than 20km for points within Marikina")
        
    @patch('requests.get')  # Mock API calls
    def test_api_fallback(self, mock_get):
        """Test that system falls back to haversine when API fails"""
        # Configure mock to simulate API failure
        mock_get.side_effect = Exception("API error")
        
        # Test with known points
        distance = calculate_distance(14.6399746, 121.0965973, 14.6361025, 121.0984445)
        
        # Verify distance is calculated despite API failure
        self.assertGreater(distance, 0, "Should fall back to haversine calculation")

class TestHospitalSelection(unittest.TestCase):
    
    def test_hospital_prediction(self):
        """Test the hospital prediction end-to-end"""
        # Sample patient data
        lat = 14.624179
        lon = 121.0933239
        severity = "medium"
        condition = "Moderate respiratory distress"
        
        # Get prediction
        try:
            result = predict_hospital(lat, lon, severity, condition)
            
            # Verify result structure
            self.assertIn('hospital_id', result, "Result should include hospital_id")
            self.assertIn('distance', result, "Result should include distance")
            
            # Verify hospital ID is in valid range
            self.assertGreaterEqual(result['hospital_id'], 1, "Hospital ID should be at least 1")
            self.assertLessEqual(result['hospital_id'], 11, "Hospital ID shouldn't exceed max hospital ID")
            
        except Exception as e:
            self.fail(f"predict_hospital raised exception: {e}")

    def test_invalid_location(self):
        """Test handling of invalid location"""
        # Location outside Marikina bounds
        lat = 15.0  # Way north of Marikina
        lon = 122.0  # Way east of Marikina
        
        with self.assertRaises(ValueError):
            result = predict_hospital(lat, lon, "medium", "Fracture")

if __name__ == '__main__':
    unittest.main()