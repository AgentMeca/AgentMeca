#!/usr/bin/env python3
"""Test just ChromaDB functionality."""

def test_chromadb():
    """Test ChromaDB basic functionality."""
    try:
        # Import with error handling
        try:
            import chromadb
            print("✓ ChromaDB imported successfully")
        except Exception as e:
            print(f"✗ ChromaDB import failed: {e}")
            return False
        
        try:
            from chromadb.config import Settings
            print("✓ ChromaDB Settings imported")
        except Exception as e:
            print(f"✗ ChromaDB Settings import failed: {e}")
            return False
        
        # Create client
        try:
            client = chromadb.Client(Settings(allow_reset=True, anonymized_telemetry=False))
            print("✓ ChromaDB client created")
        except Exception as e:
            print(f"✗ ChromaDB client creation failed: {e}")
            return False
        
        # Create collection
        try:
            collection = client.create_collection("test_simple")
            print("✓ Collection created")
        except Exception as e:
            print(f"✗ Collection creation failed: {e}")
            return False
        
        # Add simple data without numpy
        try:
            collection.add(
                ids=["id1"],
                embeddings=[[1.0, 2.0, 3.0]],
                documents=["test document"],
                metadatas=[{"type": "test"}]
            )
            print("✓ Data added successfully")
        except Exception as e:
            print(f"✗ Data addition failed: {e}")
            return False
        
        # Query
        try:
            results = collection.query(
                query_embeddings=[[1.1, 2.1, 3.1]],
                n_results=1
            )
            print(f"✓ Query successful: {len(results['documents'][0])} results")
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return False
        
        # Clean up
        try:
            client.delete_collection("test_simple")
            print("✓ Collection deleted")
        except Exception as e:
            print(f"✗ Collection deletion failed: {e}")
            # Not critical for test success
        
        return True
        
    except Exception as e:
        print(f"✗ Overall test failed: {e}")
        return False

if __name__ == "__main__":
    print("ChromaDB Only Test")
    print("=" * 20)
    
    if test_chromadb():
        print("\n✓ ChromaDB is working correctly!")
        exit(0)
    else:
        print("\n✗ ChromaDB test failed")
        exit(1)