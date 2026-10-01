import os
from db_manager import get_chroma_client

docs = [
    {
        "id": "doc1",
        "text": "When writing a LangGraph agent, ensure the state is correctly passed between nodes. The state should be a TypedDict. Example: class GraphState(TypedDict): keys: str",
        "metadata": {"type": "documentation", "topic": "langgraph"}
    },
    {
        "id": "doc2",
        "text": "Pytest requires test files to be named test_*.py or *_test.py. Test functions must start with test_. Example: def test_addition(): assert 1 + 1 == 2",
        "metadata": {"type": "documentation", "topic": "pytest"}
    },
    {
        "id": "doc3",
        "text": "If a Docker container returns exit code 1, it generally indicates a failure in the application logic or tests. Exit code 0 means success.",
        "metadata": {"type": "documentation", "topic": "docker"}
    }
]

def seed_database():
    print("Initializing ChromaDB and seeding with documentation...")
    client = get_chroma_client()
    
    # Create or get the collection
    collection = client.get_or_create_collection(name="documentation")
    
    # Check if already seeded
    if collection.count() == 0:
        ids = [doc["id"] for doc in docs]
        texts = [doc["text"] for doc in docs]
        metadatas = [doc["metadata"] for doc in docs]
        
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully seeded {len(docs)} documents into ChromaDB.")
    else:
        print(f"ChromaDB already contains {collection.count()} documents. Skipping seed.")

if __name__ == '__main__':
    seed_database()
