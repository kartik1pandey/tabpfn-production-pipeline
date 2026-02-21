"""Test script for API endpoints."""
import requests
import numpy as np
import time

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200


def test_predict():
    """Test prediction endpoint."""
    print("\n=== Testing Prediction Endpoint ===")
    
    # Generate sample features (50 features as in dataset)
    n_samples = 10
    n_features = 50
    features = np.random.randn(n_samples, n_features).tolist()
    
    payload = {
        "features": features,
        "use_calibration": True,
        "use_conformal": False,
        "alpha": 0.1
    }
    
    start_time = time.time()
    response = requests.post(f"{API_URL}/predict", json=payload)
    latency = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Latency: {latency:.4f}s")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Predictions: {result['predictions'][:5]}...")
        print(f"Probabilities: {result['probabilities'][:5]}...")
        print(f"Model tier: {result['model_tier']}")
        print(f"Inference time: {result['inference_time']:.4f}s")
    else:
        print(f"Error: {response.text}")


def test_shift_detection():
    """Test shift detection endpoint."""
    print("\n=== Testing Shift Detection Endpoint ===")
    
    # Generate sample features
    n_samples = 200
    n_features = 50
    features = np.random.randn(n_samples, n_features).tolist()
    
    payload = {
        "features": features,
        "use_calibration": False,
        "use_conformal": False
    }
    
    response = requests.post(f"{API_URL}/detect_shift", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Shift detected: {result.get('shift_detected', 'N/A')}")
        print(f"AUC score: {result.get('auc_score', 'N/A'):.4f}")
        if 'top_drifting_features' in result:
            print(f"Top drifting features: {len(result['top_drifting_features'])}")
    else:
        print(f"Error: {response.text}")


def test_metrics():
    """Test metrics endpoint."""
    print("\n=== Testing Metrics Endpoint ===")
    response = requests.get(f"{API_URL}/metrics")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        lines = response.text.split('\n')
        print(f"Metrics available: {len([l for l in lines if l and not l.startswith('#')])} lines")
        # Print first few metrics
        for line in lines[:10]:
            if line and not line.startswith('#'):
                print(f"  {line}")


def main():
    """Run all tests."""
    print("=" * 80)
    print("API Testing Suite")
    print("=" * 80)
    
    try:
        test_health()
        test_predict()
        test_shift_detection()
        test_metrics()
        
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API. Make sure the server is running:")
        print("  python -m uvicorn src.api:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
