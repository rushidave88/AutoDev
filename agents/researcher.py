from typing import Dict, Any
import sys
import os

# Add parent dir to path to import database modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import get_chroma_client

def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- RESEARCHER ---")
    error_log = state.get("test_results", {}).get("output", "")
    
    if not error_log:
        return {"fix_context": "No error log provided."}
        
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="documentation")
    
    # Query ChromaDB with the error log (take first 500 chars to avoid huge context)
    results = collection.query(
        query_texts=[error_log[:500]], 
        n_results=1
    )
    
    retrieved_docs = results['documents'][0] if results['documents'] else []
    fix_context = "\n".join(retrieved_docs) if retrieved_docs else "No relevant fixes found in database."
    print(f"Retrieved context for fix.")
    
    return {"fix_context": fix_context}
