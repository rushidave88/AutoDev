import numpy as np
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def generate_mock_data(num_samples=1000):
    np.random.seed(42)
    # Features: lines_of_code, cyclomatic_complexity, loop_count, dependency_count
    lines = np.random.randint(10, 500, num_samples)
    complexity = np.random.randint(1, 20, num_samples)
    loops = np.random.randint(0, 10, num_samples)
    deps = np.random.randint(0, 15, num_samples)
    
    X = np.column_stack((lines, complexity, loops, deps))
    
    # Target: has_bug
    # Create some logical relationships: high complexity/loops/lines increase bug probability
    risk_score = (lines / 500) + (complexity / 20) + (loops / 10) + (deps / 15)
    probabilities = risk_score / risk_score.max()
    
    # Introduce some noise
    y = (np.random.rand(num_samples) < probabilities).astype(int)
    
    return X, y

def train_and_save_model():
    print("Generating mock data...")
    X, y = generate_mock_data(2000)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = XGBClassifier(eval_metric='logloss')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy:.2f}")
    
    model_path = os.path.join(os.path.dirname(__file__), 'bug_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_and_save_model()
