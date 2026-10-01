import ast
import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'bug_model.joblib')

class CodeMetricsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        self.loops = 0
        self.dependencies = 0

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.loops += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.loops += 1
        self.generic_visit(node)
        
    def visit_Import(self, node):
        self.dependencies += len(node.names)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        self.dependencies += len(node.names)
        self.generic_visit(node)

def extract_metrics(code: str):
    lines_of_code = len(code.strip().split('\n'))
    
    try:
        tree = ast.parse(code)
        visitor = CodeMetricsVisitor()
        visitor.visit(tree)
        return [lines_of_code, visitor.complexity, visitor.loops, visitor.dependencies]
    except SyntaxError:
        # If code has syntax errors, penalize heavily
        return [lines_of_code, 20, 10, 15]

def predict_bug_risk(code: str) -> float:
    """Returns a probability (0.0 to 1.0) of the code containing a bug."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"{MODEL_PATH} not found. Run train.py first.")
        
    model = joblib.load(MODEL_PATH)
    metrics = extract_metrics(code)
    
    # XGBoost expects 2D array for prediction
    features = np.array(metrics).reshape(1, -1)
    
    # Predict probability of class 1 (bug)
    risk_prob = model.predict_proba(features)[0][1]
    return float(risk_prob)

if __name__ == '__main__':
    sample_code = """
import os
import sys

def complex_func(x):
    if x > 10:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    else:
        while x > 0:
            x -= 1
    return x
"""
    print("Extracting AST metrics and predicting risk for sample code...")
    risk = predict_bug_risk(sample_code)
    print(f"Bug Risk Probability: {risk:.2%}")
