# create_model.py
import pickle
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

import os
print("🌸 Creating Iris Classification Model for API...")

# Load Iris dataset
iris = load_iris()
X, y = iris.data, iris.target
feature_names = iris.feature_names
target_names = iris.target_names

print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
print(f"🏷️ Classes: {target_names}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train RandomForest model
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n🎯 Model Training Complete!")
print(f"📈 Test Accuracy: {accuracy:.4f}")
print(f"\n📋 Classification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))

# Save model and scaler
os.makedirs('deploy', exist_ok=True)
with open('deploy/iris-model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('deploy/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print(f"\n💾 Model saved: deploy/iris-model.pkl")
print(f"📏 Scaler saved: deploy/scaler.pkl")
print(f"✅ Ready for Docker deployment!")
