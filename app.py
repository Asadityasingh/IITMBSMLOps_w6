# app/app.py
from flask import Flask, request, jsonify
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)

# Load the trained model and scaler
MODEL_PATH = os.getenv('MODEL_PATH', 'deploy/iris-model.pkl')
SCALER_PATH = 'deploy/scaler.pkl'  # We'll save this in Step 3

print(f"Loading model from {MODEL_PATH}...")
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    # Fallback: use sklearn's default Iris classifier
    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    iris = load_iris()
    X_train, _, y_train, _ = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("✓ Fallback model created!")

# Load or create scaler
try:
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
except:
    # Create and save scaler
    from sklearn.datasets import load_iris
    iris = load_iris()
    scaler = StandardScaler()
    scaler.fit(iris.data)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    print("✓ Scaler created and saved!")

# Species mapping
SPECIES_MAP = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Iris Classification API is running!",
        "version": "1.0.0"
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict Iris species from measurements"""
    try:
        data = request.get_json()
        
        # Validate input
        required_features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        if not all(feature in data for feature in required_features):
            return jsonify({
                "error": "Missing required features",
                "required": required_features
            }), 400
        
        # Extract features
        features = np.array([
            [data['sepal_length'], data['sepal_width'], 
             data['petal_length'], data['petal_width']]
        ])
        
        # Validate feature ranges (typical Iris measurements)
        if not (4 <= data['sepal_length'] <= 8 and 
                2 <= data['sepal_width'] <= 4.5 and 
                1 <= data['petal_length'] <= 7 and 
                0.1 <= data['petal_width'] <= 2.5):
            return jsonify({
                "warning": "Measurements outside typical Iris range",
                "predicted_species": "unknown"
            }), 200
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        # Get species name
        species = SPECIES_MAP[prediction]
        
        return jsonify({
            "predicted_species": species,
            "confidence": float(max(probabilities)),
            "probabilities": {
                "setosa": float(probabilities[0]),
                "versicolor": float(probabilities[1]),
                "virginica": float(probabilities[2])
            },
            "measurements": {
                "sepal_length": float(data['sepal_length']),
                "sepal_width": float(data['sepal_width']),
                "petal_length": float(data['petal_length']),
                "petal_width": float(data['petal_width'])
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "message": str(e)
        }), 500

@app.route('/predict_multiple', methods=['POST'])
def predict_multiple():
    """Predict multiple Iris samples"""
    try:
        data = request.get_json()
        samples = data.get('samples', [])
        
        if not samples:
            return jsonify({"error": "No samples provided"}), 400
        
        results = []
        for i, sample in enumerate(samples):
            features = np.array([[
                sample['sepal_length'], sample['sepal_width'],
                sample['petal_length'], sample['petal_width']
            ]])
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            species = SPECIES_MAP[prediction]
            
            results.append({
                "sample_id": i,
                "predicted_species": species,
                "confidence": float(max(probabilities)),
                "measurements": sample
            })
        
        return jsonify({
            "total_samples": len(results),
            "predictions": results
        })
        
    except Exception as e:
        return jsonify({
            "error": "Batch prediction failed",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    print("🚀 Starting Iris Classification API...")
    print(f"📊 Model: {type(model).__name__}")
    print(f"📈 Scaler: {type(scaler).__name__}")
    print("🌐 API available at: http://0.0.0.0:5000")
    print("📋 Endpoints:")
    print("   GET  /           - Health check")
    print("   POST /predict    - Single prediction")
    print("   POST /predict_multiple - Batch prediction")
    app.run(host='0.0.0.0', port=5000, debug=False)
