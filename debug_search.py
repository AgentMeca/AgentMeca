#!/usr/bin/env python3
"""
Debug script to understand why search is failing.
"""

from vector_database import create_database
import numpy as np

def debug_search():
    """Debug search functionality."""
    print("=== Vector Database Search Debug ===\n")
    
    # Initialize database
    db = create_database()
    
    # Generate a test embedding
    test_query = "import"
    print(f"Testing query: '{test_query}'")
    
    # Generate embedding using CodeBERT
    query_embedding = db.code_model.encode([test_query], convert_to_numpy=True)[0]
    print(f"Query embedding shape: {query_embedding.shape}")
    print(f"Query embedding (first 10 values): {query_embedding[:10]}")
    print()
    
    # Get some stored data to compare
    stored_data = db._collection.get(limit=3, include=['embeddings', 'documents', 'metadatas'])
    print(f"Retrieved {len(stored_data['documents'])} stored documents")
    
    if stored_data.get('embeddings') is not None and len(stored_data['embeddings']) > 0:
        stored_embedding = np.array(stored_data['embeddings'][0])
        print(f"Stored embedding shape: {stored_embedding.shape}")
        print(f"Stored embedding (first 10 values): {stored_embedding[:10]}")
        print()
        
        # Manual similarity calculation
        similarity = np.dot(query_embedding, stored_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
        )
        print(f"Manual cosine similarity: {similarity:.6f}")
        print(f"Manual distance (1-similarity): {1-similarity:.6f}")
        print()
    
    # Try raw ChromaDB query with our embedding
    print("Testing raw ChromaDB query...")
    try:
        raw_results = db._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=3,
            include=['documents', 'metadatas', 'distances']
        )
        
        print(f"Raw query returned {len(raw_results['documents'][0])} results:")
        for i, (doc, meta, dist) in enumerate(zip(
            raw_results['documents'][0],
            raw_results['metadatas'][0], 
            raw_results['distances'][0]
        ), 1):
            similarity_old = 1 - dist
            similarity_new = 1 / (1 + dist)
            print(f"  {i}. Distance: {dist:.6f}")
            print(f"     Old similarity (1-dist): {similarity_old:.6f}")
            print(f"     New similarity (1/(1+dist)): {similarity_new:.6f}")
            print(f"     Content: {doc[:60]}...")
            print()
            
    except Exception as e:
        print(f"Raw query failed: {e}")
    
    # Test our search function with very low threshold
    print("Testing our search function with threshold 0.0...")
    results = db.search("import", content_type="code", limit=3, similarity_threshold=0.0)
    print(f"Our search returned {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. Similarity: {result['similarity_score']:.6f}")
        print(f"     Content: {result['text'][:60]}...")
        print()

if __name__ == "__main__":
    debug_search()