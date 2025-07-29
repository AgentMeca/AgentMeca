#!/usr/bin/env python3
"""
Minimal test for vector database without heavy models.
"""

import json
import sys
from pathlib import Path

def test_chunk_processing():
    """Test chunk loading and processing without embeddings."""
    try:
        # Find a sample chunk file
        source_dir = Path("processed/semantic_chunks") 
        jsonl_files = list(source_dir.glob("**/*.jsonl"))
        
        if not jsonl_files:
            print("✗ No JSONL files found")
            return False
        
        sample_file = jsonl_files[0]
        print(f"✓ Testing with file: {sample_file.name}")
        
        # Load and process chunks
        chunks_processed = 0
        doc_chunks = 0
        code_chunks = 0
        
        with open(sample_file, 'r') as f:
            for line_num, line in enumerate(f):
                if line_num >= 10:  # Just test first 10 chunks
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                try:
                    chunk = json.loads(line)
                    
                    # Determine content type
                    content_type = 'document'
                    if 'source_path' in chunk or 'repo' in chunk or 'lang' in chunk:
                        content_type = 'code'
                    elif '/code/' in str(sample_file):
                        content_type = 'code'
                    
                    chunk['content_type'] = content_type
                    
                    # Count by type
                    if content_type == 'document':
                        doc_chunks += 1
                    else:
                        code_chunks += 1
                    
                    chunks_processed += 1
                    
                    # Show first chunk details
                    if line_num == 0:
                        print(f"  First chunk ID: {chunk.get('chunk_id', 'unknown')}")
                        print(f"  Content type: {content_type}")
                        print(f"  Text length: {len(chunk.get('text', ''))}")
                        print(f"  Has required fields: {all(f in chunk for f in ['chunk_id', 'text'])}")
                    
                except json.JSONDecodeError as e:
                    print(f"  ⚠ JSON error on line {line_num + 1}: {e}")
                    continue
        
        print(f"✓ Processed {chunks_processed} chunks successfully")
        print(f"  Document chunks: {doc_chunks}")
        print(f"  Code chunks: {code_chunks}")
        
        return True
        
    except Exception as e:
        print(f"✗ Chunk processing test failed: {e}")
        return False

def test_all_files():
    """Test processing all chunk files."""
    try:
        source_dir = Path("processed/semantic_chunks")
        jsonl_files = list(source_dir.glob("**/*.jsonl"))
        
        print(f"✓ Found {len(jsonl_files)} JSONL files")
        
        total_chunks = 0
        total_doc_chunks = 0
        total_code_chunks = 0
        error_files = 0
        
        for file_path in jsonl_files:
            try:
                file_chunks = 0
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # Just count, don't parse to save time
                            file_chunks += 1
                
                total_chunks += file_chunks
                
                # Determine type by path
                if '/docs/' in str(file_path):
                    total_doc_chunks += file_chunks
                else:
                    total_code_chunks += file_chunks
                    
            except Exception as e:
                print(f"  ✗ Error reading {file_path.name}: {e}")
                error_files += 1
                continue
        
        print(f"✓ Total chunks across all files: {total_chunks:,}")
        print(f"  Document chunks: {total_doc_chunks:,}")
        print(f"  Code chunks: {total_code_chunks:,}")
        print(f"  Files with errors: {error_files}")
        
        return True
        
    except Exception as e:
        print(f"✗ All files test failed: {e}")
        return False

def test_chromadb_minimal():
    """Test ChromaDB without embeddings."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Create in-memory client to avoid file system issues
        client = chromadb.Client(Settings(allow_reset=True, anonymized_telemetry=False))
        print("✓ ChromaDB in-memory client created")
        
        # Create collection
        collection = client.create_collection("test_minimal")
        print("✓ Test collection created")
        
        # Test with dummy embeddings (no model required)
        test_data = [
            {
                "id": "test1",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],  # Dummy 5D vector
                "document": "This is a test document about robots",
                "metadata": {"content_type": "document", "source": "test"}
            },
            {
                "id": "test2", 
                "embedding": [0.5, 0.4, 0.3, 0.2, 0.1],  # Dummy 5D vector
                "document": "def robot_move(): pass",
                "metadata": {"content_type": "code", "language": "python"}
            }
        ]
        
        # Add data
        collection.add(
            ids=[item["id"] for item in test_data],
            embeddings=[item["embedding"] for item in test_data],
            documents=[item["document"] for item in test_data],
            metadatas=[item["metadata"] for item in test_data]
        )
        print("✓ Test data added to collection")
        
        # Test query
        results = collection.query(
            query_embeddings=[[0.15, 0.25, 0.35, 0.45, 0.55]],  # Dummy query vector
            n_results=2
        )
        print(f"✓ Query successful, found {len(results['documents'][0])} results")
        
        # Test metadata filtering
        filtered_results = collection.query(
            query_embeddings=[[0.15, 0.25, 0.35, 0.45, 0.55]],
            n_results=1,
            where={"content_type": "code"}
        )
        print(f"✓ Filtered query successful, found {len(filtered_results['documents'][0])} code results")
        
        # Cleanup
        client.delete_collection("test_minimal")
        print("✓ Test collection deleted")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB minimal test failed: {e}")
        return False

def main():
    """Run minimal tests."""
    print("Vector Database Minimal Tests")
    print("=" * 35)
    
    tests = [
        ("Chunk Processing", test_chunk_processing),
        ("All Files Count", test_all_files),
        ("ChromaDB Minimal", test_chromadb_minimal)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ Core functionality working - ready for full implementation!")
        return 0
    else:
        print("✗ Some core functionality issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())