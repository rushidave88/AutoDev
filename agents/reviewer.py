from typing import Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml_engine.predictor import predict_bug_risk
from sandbox.executor import execute_code

def reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- QA REVIEWER ---")
    code = state.get("code", "")
    tests = state.get("tests", "")
    iteration = state.get("iteration_count", 0)
    
    # Evaluate risk
    try:
        risk_prob = predict_bug_risk(code)
        print(f"Assessed Bug Risk: {risk_prob:.2%}")
    except Exception as e:
        print(f"Risk model error: {e}. Proceeding with default risk.")
        risk_prob = 0.5
        
    if risk_prob > 0.8:
        print("High bug risk detected. Returning to Coder without executing.")
        return {
            "test_results": {"status": "failed", "output": "Risk score too high (>80%). Please simplify the code."},
            "iteration_count": iteration + 1
        }
        
    print("Risk acceptable. Executing in Docker Sandbox...")
    results = execute_code(code, tests)
    print(f"Execution Status: {results['status']}")
    
    return {
        "test_results": results,
        "iteration_count": iteration + 1
    }
