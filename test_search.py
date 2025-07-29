#!/usr/bin/env python3
"""
Simple test script to verify vector database search functionality.
"""

from vector_database import create_database

def test_search():
    """Test basic search functionality."""
    print("=== Vector Database Search Test ===\n")
    
    # Initialize database
    db = create_database()
    
    # Get basic stats
    stats = db.get_stats()
    print(f"Database Stats:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Code chunks: {stats['code_chunks']}")
    print(f"  Document chunks: {stats['document_chunks']}")
    print()
    
    # Test searches with different queries and thresholds
    test_queries = [
        ("robot move", "code", 0.3),
        ("move joint", "code", 0.3),
        ("import", "code", 0.3),
        ("python function", "code", 0.3),
        ("mecademicpy", "code", 0.2),
    ]
    
    for query, content_type, threshold in test_queries:
        print(f"Testing: '{query}' (type={content_type}, threshold={threshold})")
        
        try:
            results = db.search(
                query=query, 
                content_type=content_type, 
                limit=3, 
                similarity_threshold=threshold
            )
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. Score: {result['similarity_score']:.3f}")
                    print(f"     Content: {result['text'][:80]}...")
                    print(f"     Source: {result['metadata'].get('source_path', 'Unknown')}")
            else:
                print(f"❌ No results found")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_search()