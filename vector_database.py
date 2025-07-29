#!/usr/bin/env python3
"""
Vector Database Manager using ChromaDB

Provides a unified interface for storing and searching semantic chunks with
dual embedding models: BGE-M3 for documents, StarCoder2-15B for code.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import yaml

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np


class VectorDatabase:
    """
    Main vector database interface using ChromaDB with dual embedding models.
    """
    
    def __init__(self, config_path: str = "vector_db_config.yaml"):
        """
        Initialize the vector database.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize models (lazy loading)
        self._document_model = None
        self._code_model = None
        
        # ChromaDB client and collection
        self._client = None
        self._collection = None
        
        # Statistics
        self.stats = {
            "total_chunks": 0,
            "document_chunks": 0,
            "code_chunks": 0,
            "embedding_cache_hits": 0,
            "embedding_cache_misses": 0
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = Path(self.config['storage']['log_directory'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'vector_db.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    @property
    def document_model(self) -> SentenceTransformer:
        """Lazy-load BGE-M3 model for document embeddings."""
        if self._document_model is None:
            self.logger.info("Loading BGE-M3 model for document embeddings...")
            model_config = self.config['embeddings']['document_model']
            self._document_model = SentenceTransformer(
                model_config['name'],
                device=model_config.get('device', 'auto')
            )
            self.logger.info(f"BGE-M3 model loaded on device: {self._document_model.device}")
        return self._document_model
    
    @property 
    def code_model(self) -> SentenceTransformer:
        """Lazy-load code embedding model."""
        if self._code_model is None:
            model_config = self.config['embeddings']['code_model']
            model_name = model_config['name']
            self.logger.info(f"Loading {model_name} model for code embeddings...")
            self._code_model = SentenceTransformer(
                model_name,
                device=model_config.get('device', 'auto'),
                trust_remote_code=model_config.get('trust_remote_code', False)
            )
            self.logger.info(f"{model_name} model loaded on device: {self._code_model.device}")
        return self._code_model
    
    def initialize_database(self) -> None:
        """Initialize ChromaDB client and collection."""
        self.logger.info("Initializing ChromaDB...")
        
        # Create database directory
        db_path = Path(self.config['database']['path'])
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self._client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Create or get collection
        collection_name = self.config['database']['collection_name']
        try:
            self._collection = self._client.get_collection(collection_name)
            self.logger.info(f"Loaded existing collection: {collection_name}")
            
            # Update stats
            self.stats["total_chunks"] = self._collection.count()
            self._update_content_type_stats()
            
        except Exception:
            self._collection = self._client.create_collection(
                name=collection_name,
                metadata={"description": "Mecademic documentation and code chunks"}
            )
            self.logger.info(f"Created new collection: {collection_name}")
    
    def _update_content_type_stats(self) -> None:
        """Update statistics based on content types in the collection."""
        if not self._collection:
            return
            
        # Get all metadata to count content types
        try:
            results = self._collection.get(include=['metadatas'])
            doc_count = sum(1 for meta in results['metadatas'] 
                          if meta and meta.get('content_type') == 'document')
            code_count = sum(1 for meta in results['metadatas'] 
                           if meta and meta.get('content_type') == 'code')
            
            self.stats["document_chunks"] = doc_count
            self.stats["code_chunks"] = code_count
            
        except Exception as e:
            self.logger.warning(f"Could not update content type stats: {e}")
    
    def generate_embedding(self, text: str, content_type: str) -> np.ndarray:
        """
        Generate embedding for text using appropriate model based on content type.
        
        Args:
            text: Text to embed
            content_type: 'document' or 'code'
            
        Returns:
            Embedding vector as numpy array
        """
        if content_type == 'document':
            return self.document_model.encode([text], convert_to_numpy=True)[0]
        elif content_type == 'code':
            return self.code_model.encode([text], convert_to_numpy=True)[0]
        else:
            self.logger.warning(f"Unknown content type '{content_type}', using document model")
            return self.document_model.encode([text], convert_to_numpy=True)[0]
    
    def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """
        Add chunks to the vector database in batches.
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Number of chunks to process per batch
            
        Returns:
            Processing statistics
        """
        if not self._collection:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        self.logger.info(f"Adding {len(chunks)} chunks to database...")
        
        processed = 0
        errors = []
        doc_chunks_added = 0
        code_chunks_added = 0
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            try:
                # Prepare batch data
                ids = []
                embeddings = []
                metadatas = []
                documents = []
                
                for chunk in batch:
                    chunk_id = chunk.get('chunk_id', f'chunk_{i}_{processed}')
                    text = chunk.get('text', '')
                    content_type = chunk.get('content_type', 'document')
                    
                    # Generate embedding
                    embedding = self.generate_embedding(text, content_type)
                    
                    # Prepare metadata (exclude large fields)
                    metadata = {k: v for k, v in chunk.items() 
                              if k not in ['text', 'embedding'] and v is not None}
                    
                    # Ensure metadata values are JSON serializable
                    metadata = self._sanitize_metadata(metadata)
                    
                    ids.append(chunk_id)
                    embeddings.append(embedding.tolist())
                    metadatas.append(metadata)
                    documents.append(text)
                    
                    # Update counters
                    if content_type == 'document':
                        doc_chunks_added += 1
                    else:
                        code_chunks_added += 1
                
                # Add batch to collection
                self._collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                
                processed += len(batch)
                
                if processed % 500 == 0:
                    self.logger.info(f"Processed {processed}/{len(chunks)} chunks...")
                
            except Exception as e:
                error_msg = f"Error processing batch {i//batch_size + 1}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        # Update statistics
        self.stats["total_chunks"] = self._collection.count()
        self.stats["document_chunks"] += doc_chunks_added
        self.stats["code_chunks"] += code_chunks_added
        
        result = {
            "chunks_processed": processed,
            "document_chunks_added": doc_chunks_added,
            "code_chunks_added": code_chunks_added,
            "errors": errors,
            "success_rate": processed / len(chunks) if chunks else 0
        }
        
        self.logger.info(f"Batch processing complete: {processed} chunks processed, {len(errors)} errors")
        return result
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to ensure ChromaDB compatibility."""
        sanitized = {}
        
        for key, value in metadata.items():
            # ChromaDB only accepts str, int, float, bool, or None
            if isinstance(value, (str, int, float, bool)) or value is None:
                sanitized[key] = value
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                if all(isinstance(x, (str, int, float)) for x in value):
                    sanitized[key] = ','.join(map(str, value))
                else:
                    sanitized[key] = str(value)
            else:
                sanitized[key] = str(value)
        
        return sanitized
    
    def search(self, 
               query: str, 
               content_type: Optional[str] = None,
               limit: int = None,
               similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query: Search query text
            content_type: Filter by content type ('document' or 'code')
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of matching chunks with similarity scores
        """
        if not self._collection:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        # Use config defaults if not specified
        limit = limit or self.config['search']['default_limit']
        similarity_threshold = similarity_threshold or self.config['search']['similarity_threshold']
        
        # Generate query embedding using appropriate model
        if content_type == 'code':
            query_embedding = self.code_model.encode([query], convert_to_numpy=True)[0]
        else:
            # Default to document model for mixed or document queries
            query_embedding = self.document_model.encode([query], convert_to_numpy=True)[0]
        
        # Build where clause for content type filtering
        where_clause = None
        if content_type:
            where_clause = {"content_type": content_type}
        
        # Search in ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            # Convert distance to similarity score
            # ChromaDB uses squared Euclidean distance, convert to similarity [0,1]
            # For normalized embeddings: similarity ≈ 1 / (1 + distance)
            similarity = 1 / (1 + distance)
            
            if similarity >= similarity_threshold:
                result = {
                    'text': doc,
                    'metadata': metadata,
                    'similarity_score': similarity,
                    'rank': i + 1
                }
                formatted_results.append(result)
        
        self.logger.info(f"Search returned {len(formatted_results)} results above threshold {similarity_threshold}")
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self._collection:
            self.stats["total_chunks"] = self._collection.count()
            self._update_content_type_stats()
        
        return {
            **self.stats,
            "database_path": self.config['database']['path'],
            "collection_name": self.config['database']['collection_name'],
            "models_loaded": {
                "document_model": self._document_model is not None,
                "code_model": self._code_model is not None
            }
        }
    
    def reset_database(self) -> None:
        """Reset the database (delete all data)."""
        if self._client and self._collection:
            collection_name = self.config['database']['collection_name']
            self._client.delete_collection(collection_name)
            self._collection = None
            
            # Reset stats
            self.stats.update({
                "total_chunks": 0,
                "document_chunks": 0,
                "code_chunks": 0
            })
            
            self.logger.info("Database reset successfully")
    
    def close(self) -> None:
        """Close database connections and cleanup."""
        self._client = None
        self._collection = None
        self.logger.info("Database connections closed")


def create_database(config_path: str = "vector_db_config.yaml") -> VectorDatabase:
    """
    Factory function to create and initialize a VectorDatabase instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Initialized VectorDatabase instance
    """
    db = VectorDatabase(config_path)
    db.initialize_database()
    return db