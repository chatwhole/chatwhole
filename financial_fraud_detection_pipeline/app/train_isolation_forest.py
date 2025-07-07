import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os

def main():
    # Example training data - replace with real transaction features
    X_train = np.array([[500], [200], [15000], [1000], [300], [7000], [50], [12000]])

    # Train Isolation Forest model
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)

    # Save the model to /opt/ml/model for SageMaker
    model_dir = os.environ.get('SM_MODEL_DIR', '/opt/ml/model')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'model.joblib'))

if __name__ == "__main__":
    main()
