#!/usr/bin/env python3
"""
Basic test to verify vector database components work.
"""

import sys
from pathlib import Path

def test_imports():
    """Test basic imports."""
    try:
        import yaml
        print("✓ PyYAML available")
    except ImportError as e:
        print(f"✗ PyYAML import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB available")
    except ImportError as e:
        print(f"✗ ChromaDB import failed: {e}")
        return False
    
    return True

def test_config():
    """Test config loading."""
    try:
        import yaml
        with open("vector_db_config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Configuration loaded successfully")
        print(f"  Database path: {config['database']['path']}")
        print(f"  Collection name: {config['database']['collection_name']}")
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_chromadb():
    """Test ChromaDB initialization."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Create test client
        client = chromadb.Client(Settings(allow_reset=True, anonymized_telemetry=False))
        print("✓ ChromaDB client created")
        
        # Test collection operations
        collection = client.create_collection("test_collection")
        print("✓ Test collection created")
        
        # Add some test data
        collection.add(
            ids=["test1"],
            documents=["This is a test document"],
            metadatas=[{"type": "test"}]
        )
        print("✓ Test document added")
        
        # Query test
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        print("✓ Test query successful")
        print(f"  Found {len(results['documents'][0])} results")
        
        # Cleanup
        client.delete_collection("test_collection")
        print("✓ Test collection deleted")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB test failed: {e}")
        return False

def test_chunk_files():
    """Test chunk file discovery."""
    try:
        source_dir = Path("processed/semantic_chunks")
        if not source_dir.exists():
            print(f"✗ Source directory not found: {source_dir}")
            return False
        
        jsonl_files = list(source_dir.glob("**/*.jsonl"))
        print(f"✓ Found {len(jsonl_files)} JSONL files")
        
        # Test loading a sample file
        if jsonl_files:
            import json
            sample_file = jsonl_files[0]
            with open(sample_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 1:  # Just read first line
                        break
                    chunk = json.loads(line)
                    print(f"✓ Sample chunk loaded from {sample_file.name}")
                    print(f"  Chunk ID: {chunk.get('chunk_id', 'unknown')}")
                    print(f"  Text length: {len(chunk.get('text', ''))}")
                    break
        
        return True
        
    except Exception as e:
        print(f"✗ Chunk file test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("Vector Database Basic Tests")
    print("=" * 30)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("ChromaDB Test", test_chromadb),
        ("Chunk Files Test", test_chunk_files)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ All basic tests passed - ready for ingestion!")
        return 0
    else:
        print("✗ Some tests failed - check dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())