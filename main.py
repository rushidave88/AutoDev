import os
import sys
import time
import subprocess
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

# Import Agents and Utils
from agents.architect import architect_node
from agents.coder import coder_node
from agents.researcher import researcher_node
from agents.reviewer import reviewer_node
from database.db_manager import insert_log

class GraphState(TypedDict):
    user_prompt: str
    plan: Dict[str, Any]
    code: str
    tests: str
    iteration_count: int
    test_results: Dict[str, Any]
    fix_context: str
    start_time: float

def ensure_docker_running():
    print("Checking Docker Health...")
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("Docker Engine is running and accessible.")
    except Exception as e:
        print(f"CRITICAL ERROR: Docker Engine is not accessible. Details: {e}")
        print("Please start Docker Desktop and ensure it is fully initialized before continuing.")
        sys.exit(1)

def route_from_reviewer(state: GraphState) -> str:
    status = state.get("test_results", {}).get("status", "failed")
    iteration = state.get("iteration_count", 0)
    
    if status == "passed":
        print("Tests passed! Routing to END.")
        return "end"
    else:
        if iteration >= 3:
            print(f"Max iterations ({iteration}) reached. Graceful failure. Routing to END.")
            return "end"
        else:
            print(f"Tests failed at iteration {iteration}. Routing to Researcher.")
            return "researcher"

def end_node(state: GraphState) -> GraphState:
    print("--- END STATE ---")
    status = state.get("test_results", {}).get("status", "failed")
    prompt = state.get("user_prompt", "")
    
    # Calculate execution time
    execution_time = time.time() - state.get("start_time", time.time())
    
    # Log to SQLite (estimating tokens for mock purposes)
    estimated_tokens = len(prompt) // 4 + len(state.get("code", "")) // 4
    
    log_id = insert_log(prompt, estimated_tokens, execution_time, status)
    print(f"Execution logged to SQLite with ID: {log_id}")
    
    return state

def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("end_logging", end_node)
    
    # Add edges
    workflow.set_entry_point("architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "reviewer")
    workflow.add_edge("researcher", "coder")
    
    # Conditional edge
    workflow.add_conditional_edges(
        "reviewer",
        route_from_reviewer,
        {
            "end": "end_logging",
            "researcher": "researcher"
        }
    )
    workflow.add_edge("end_logging", END)
    
    return workflow.compile()

if __name__ == "__main__":
    ensure_docker_running()
    
    app = build_graph()
    
    # Test the orchestrator
    print("Starting AutoDev Pipeline...")
    initial_state = {
        "user_prompt": "Write a python function that Prints prime number till  number n, and a test file for it.",
        "plan": {},
        "code": "",
        "tests": "",
        "iteration_count": 0,
        "test_results": {},
        "fix_context": "",
        "start_time": time.time()
    }
    
    try:
        final_state = app.invoke(initial_state)
        print("\n--- FINAL OUTPUT ---")
        print(f"Final Status: {final_state.get('test_results', {}).get('status')}")
        safe_code = final_state.get("code", "").encode('ascii', 'replace').decode('ascii')
        print("Main Code:\n" + safe_code)
    except Exception as e:
        import traceback
        print(f"Pipeline error: {e}")
        traceback.print_exc()
