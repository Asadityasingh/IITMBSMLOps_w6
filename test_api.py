# test_api.py
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Health Check: {response.status_code}")
    print(f"Response: {response.json()}")

def test_single_prediction():
    """Test single prediction"""
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"\nSingle Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_batch_prediction():
    """Test batch prediction"""
    payload = {
        "samples": [
            {
                "sepal_length": 5.1, "sepal_width": 3.5,
                "petal_length": 1.4, "petal_width": 0.2
            },
            {
                "sepal_length": 6.7, "sepal_width": 3.0,
                "petal_length": 5.2, "petal_width": 2.3
            },
            {
                "sepal_length": 7.2, "sepal_width": 3.6,
                "petal_length": 6.1, "petal_width": 2.5
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/predict_multiple", json=payload)
    print(f"\nBatch Prediction: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("🧪 Testing Iris Classification API...")
    test_health_check()
    test_single_prediction()
    test_batch_prediction()
